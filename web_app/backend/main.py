# -*- coding: utf-8 -*-

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHOOL_PROJECT = ROOT / "school_project"
for path in (ROOT, SCHOOL_PROJECT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from matching_core import match_images, scan_images, serialize_groups

try:
    from .schemas import MatchRequest, MatchResponse, ProjectCreate, ProjectResponse
    from .storage import create_project, load_project_state, save_project_state, save_upload
except ImportError:
    from schemas import MatchRequest, MatchResponse, ProjectCreate, ProjectResponse
    from storage import create_project, load_project_state, save_project_state, save_upload


app = FastAPI(title="Auto Image Matching Web API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post("/api/projects/{project_id}/images")
def upload_images(project_id: str, files: list[UploadFile] = File(...)):
    if load_project_state(project_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    paths = []
    for upload_file in files:
        paths.append(save_upload(project_id, upload_file))
    state = load_project_state(project_id)
    return {"project_id": project_id, "uploaded": len(paths), "image_count": len(state.get("images", [])), "paths": paths}


@app.post("/api/projects/{project_id}/match", response_model=MatchResponse)
def match_project(project_id: str, payload: MatchRequest):
    state = load_project_state(project_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Project not found")
    images = state.get("images", [])
    if not images:
        raise HTTPException(status_code=400, detail="Project has no images")

    scan_result = scan_images(images)
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
