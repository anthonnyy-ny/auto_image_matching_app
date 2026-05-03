# -*- coding: utf-8 -*-

import sys
import threading
import time
import uuid
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SCHOOL_PROJECT = ROOT / "school_project"
for path in (ROOT, SCHOOL_PROJECT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import ValidationError

from app_paths import feature_cache_dir, thumbnail_cache_dir
from matching_core import MatchCancelled, match_images, scan_images, serialize_groups

try:
    from .schemas import JobResponse, MatchRequest, MatchResponse, ProjectCreate, ProjectImport, ProjectResponse, ResultsUpdate
    from .storage import UploadLimitError, create_project, export_results_zip, import_project_state, list_project_states, load_project_state, save_project_state, save_uploads, state_path
except ImportError:
    from schemas import JobResponse, MatchRequest, MatchResponse, ProjectCreate, ProjectImport, ProjectResponse, ResultsUpdate
    from storage import UploadLimitError, create_project, export_results_zip, import_project_state, list_project_states, load_project_state, save_project_state, save_uploads, state_path


app = FastAPI(title="Auto Image Matching Web API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JOBS = {}


def model_to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def normalize_result_groups(groups):
    normalized = []
    for group in groups:
        group_dict = model_to_dict(group)
        group_dict["count"] = len(group_dict["images"])
        normalized.append(group_dict)
    return normalized


def parse_project_import(payload):
    if hasattr(ProjectImport, "model_validate"):
        return ProjectImport.model_validate(payload)
    return ProjectImport.parse_obj(payload)


def project_response(state):
    return ProjectResponse(
        id=state["id"],
        name=state["name"],
        created_at=state["created_at"],
        updated_at=state["updated_at"],
        image_count=len(state.get("images", [])),
    )


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/projects", response_model=ProjectResponse)
def create_project_api(payload: ProjectCreate):
    return project_response(create_project(payload.name))


@app.get("/api/projects", response_model=list[ProjectResponse])
def list_projects_api():
    return [project_response(state) for state in list_project_states()]


@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
def get_project_api(project_id: str):
    state = load_project_state(project_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_response(state)


@app.post("/api/projects/{project_id}/images")
def upload_images(project_id: str, files: list[UploadFile] = File(...)):
    if load_project_state(project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        paths = save_uploads(project_id, files)
    except UploadLimitError as exc:
        raise HTTPException(status_code=413, detail=str(exc))
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file")
    state = load_project_state(project_id)
    return {"project_id": project_id, "uploaded": len(paths), "image_count": len(state.get("images", [])), "paths": paths}


def run_match_job(job_id: str, project_id: str, mode: str):
    job = JOBS[job_id]
    started = time.time()
    try:
        state = load_project_state(project_id)
        if state is None:
            raise FileNotFoundError("Project not found")
        images = state.get("images", [])
        if not images:
            raise ValueError("Project has no images")

        def should_cancel():
            return bool(job.get("cancel_requested"))

        def scan_progress(value):
            job["progress"] = min(45, int(value * 0.45))
            job["message"] = "Scanning images..."
            job["metrics"] = {
                **job.get("metrics", {}),
                "stage": "scan",
                "scan_percent": value,
                "image_count": len(images),
            }

        def match_progress(value):
            job["progress"] = 45 + min(50, int(value * 0.50))
            job["message"] = "Matching groups..."
            job["metrics"] = {
                **job.get("metrics", {}),
                "stage": "match",
                "match_percent": value,
            }

        def match_stats(stats):
            job["metrics"] = {
                **job.get("metrics", {}),
                "stage": "match",
                **stats,
            }
            job["message"] = (
                "Matching "
                + str(stats.get("current_image", stats.get("processed_images", 0)))
                + "/"
                + str(stats.get("total_images", 0))
                + " images, "
                + str(stats.get("current_groups", 0))
                + " groups"
            )

        scan_result = scan_images(images, scan_progress, should_cancel, lazy_features=(mode in {"turbo", "ann"}))
        match_result = match_images(scan_result["images"], mode, match_progress, should_cancel, match_stats)
        groups = serialize_groups(match_result["groups"])
        stats = {
            "scan": scan_result["stats"],
            "match": match_result["stats"],
            "skipped": scan_result["skipped"],
        }
        state["results"] = groups
        state["stats"] = stats
        save_project_state(state)
        job.update({
            "status": "done",
            "progress": 100,
            "message": "Done",
            "result": {
                "project_id": project_id,
                "group_count": len(groups),
                "elapsed": time.time() - started,
                "stats": stats,
                "groups": groups,
            },
        })
    except MatchCancelled:
        job.update({"status": "cancelled", "message": "Cancelled", "progress": job.get("progress", 0)})
    except Exception as exc:
        job.update({"status": "failed", "message": str(exc), "error": str(exc)})


@app.post("/api/projects/{project_id}/match/jobs", response_model=JobResponse)
def start_match_job(project_id: str, payload: MatchRequest):
    if load_project_state(project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    job_id = uuid.uuid4().hex
    JOBS[job_id] = {
        "id": job_id,
        "project_id": project_id,
        "status": "running",
        "progress": 0,
        "message": "Queued",
        "result": None,
        "metrics": {"stage": "queued", "image_count": 0},
        "cancel_requested": False,
    }
    thread = threading.Thread(target=run_match_job, args=(job_id, project_id, payload.mode), daemon=True)
    thread.start()
    return JobResponse(job_id=job_id, status="running")


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.post("/api/jobs/{job_id}/cancel")
def cancel_job(job_id: str):
    job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("status") in {"done", "failed", "cancelled"}:
        return job
    job["cancel_requested"] = True
    job["message"] = "Cancelling..."
    return job


@app.post("/api/cache/clear")
def clear_cache():
    removed_files = 0
    removed_bytes = 0
    for cache_dir in (thumbnail_cache_dir(), feature_cache_dir()):
        if not cache_dir.exists():
            continue
        for path in cache_dir.rglob("*"):
            if path.is_file():
                try:
                    removed_bytes += path.stat().st_size
                    path.unlink()
                    removed_files += 1
                except OSError:
                    continue
        for path in sorted(cache_dir.rglob("*"), reverse=True):
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
    return {"removed_files": removed_files, "removed_bytes": removed_bytes}


@app.post("/api/projects/{project_id}/match", response_model=MatchResponse)
def match_project(project_id: str, payload: MatchRequest):
    state = load_project_state(project_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Project not found")
    images = state.get("images", [])
    if not images:
        raise HTTPException(status_code=400, detail="Project has no images")

    scan_result = scan_images(images, lazy_features=(payload.mode in {"turbo", "ann"}))
    match_result = match_images(scan_result["images"], payload.mode)
    groups = serialize_groups(match_result["groups"])
    stats = {
        "scan": scan_result["stats"],
        "match": match_result["stats"],
        "skipped": scan_result["skipped"],
    }
    state["results"] = groups
    state["stats"] = stats
    save_project_state(state)
    return MatchResponse(
        project_id=project_id,
        group_count=len(groups),
        elapsed=scan_result["elapsed"] + match_result["elapsed"],
        stats=stats,
        groups=groups,
    )


@app.get("/api/projects/{project_id}/results")
def project_results(project_id: str):
    state = load_project_state(project_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "project_id": project_id,
        "groups": state.get("results", []),
        "stats": state.get("stats", {}),
    }


@app.put("/api/projects/{project_id}/results")
def update_project_results(project_id: str, payload: ResultsUpdate):
    state = load_project_state(project_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Project not found")
    state["results"] = normalize_result_groups(payload.groups)
    save_project_state(state)
    return {"project_id": project_id, "groups": state["results"]}


@app.get("/api/projects/{project_id}/export")
def export_project(project_id: str):
    state = load_project_state(project_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Project not found")
    zip_path = export_results_zip(state)
    return FileResponse(zip_path, filename=zip_path.name, media_type="application/zip")


@app.get("/api/projects/{project_id}/project-file")
def download_project_file(project_id: str):
    state = load_project_state(project_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return FileResponse(state_path(project_id), filename=project_id + ".json", media_type="application/json")


@app.post("/api/projects/import", response_model=ProjectResponse)
def import_project(file: UploadFile = File(...)):
    try:
        import json
        payload = parse_project_import(json.load(file.file))
        payload_dict = model_to_dict(payload)
        groups = normalize_result_groups(payload.groups or payload.results or [])
        payload_dict["groups"] = groups
        payload_dict["results"] = groups
        state = import_project_state(payload_dict)
        return project_response(state)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/projects/{project_id}/image")
def project_image(project_id: str, path: str = Query(...)):
    state = load_project_state(project_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Project not found")
    upload_dir = Path(state["upload_dir"]).resolve()
    image_path = Path(path).resolve()
    if upload_dir not in image_path.parents and image_path != upload_dir:
        raise HTTPException(status_code=403, detail="Image is outside project uploads")
    if not image_path.exists() or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)
