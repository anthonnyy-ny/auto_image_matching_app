# -*- coding: utf-8 -*-

import json
import shutil
import uuid
import zipfile
from io import StringIO
from datetime import datetime
from pathlib import Path

from app_paths import web_runtime_dir
from image_utils import SUPPORTED_IMAGE_EXTENSIONS


RUNTIME_DIR = web_runtime_dir()
PROJECTS_DIR = RUNTIME_DIR / "projects"
UPLOADS_DIR = RUNTIME_DIR / "uploads"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def create_project(name=None):
    project_id = uuid.uuid4().hex
    now = datetime.now().isoformat(timespec="seconds")
    project_dir = UPLOADS_DIR / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    state = {
        "id": project_id,
        "name": name or ("Project " + project_id[:8]),
        "created_at": now,
        "updated_at": now,
        "upload_dir": str(project_dir),
        "images": [],
        "results": [],
        "stats": {},
    }
    save_project_state(state)
    return state


def state_path(project_id):
    return PROJECTS_DIR / (project_id + ".json")


def load_project_state(project_id):
    path = state_path(project_id)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)


def list_project_states():
    projects = []
    for path in sorted(PROJECTS_DIR.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            with open(path, "r", encoding="utf-8") as json_file:
                projects.append(json.load(json_file))
        except (OSError, json.JSONDecodeError):
            continue
    return projects


def save_project_state(state):
    state["updated_at"] = datetime.now().isoformat(timespec="seconds")
    with open(state_path(state["id"]), "w", encoding="utf-8") as json_file:
        json.dump(state, json_file, ensure_ascii=False, indent=2)


def import_project_state(payload):
    state = create_project(payload.get("name") or "Imported project")
    state["images"] = []
    for group in payload.get("groups", payload.get("results", [])):
        for image in group.get("images", []):
            source_path = image.get("source_path")
            if source_path and Path(source_path).exists():
                state["images"].append(source_path)
    state["results"] = payload.get("groups", payload.get("results", []))
    state["stats"] = payload.get("stats", {})
    save_project_state(state)
    return state


def save_upload(project_id, upload_file):
    state = load_project_state(project_id)
    if state is None:
        raise FileNotFoundError(project_id)
    upload_dir = Path(state["upload_dir"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(upload_file.filename or "image").name
    target = upload_dir / safe_name
    counter = 1
    while target.exists():
        target = upload_dir / (Path(safe_name).stem + "_" + str(counter) + Path(safe_name).suffix)
        counter += 1
    with open(target, "wb") as output:
        shutil.copyfileobj(upload_file.file, output)
    state["images"].append(str(target))
    save_project_state(state)
    return str(target)


def save_uploads(project_id, upload_files):
    state = load_project_state(project_id)
    if state is None:
        raise FileNotFoundError(project_id)
    upload_dir = Path(state["upload_dir"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    existing_names = {Path(path).name.lower() for path in state.get("images", [])}
    for upload_file in upload_files:
        safe_name = Path(upload_file.filename or "image").name
        if Path(safe_name).suffix.lower() == ".zip":
            zip_paths = _save_zip_upload(upload_dir, upload_file, existing_names)
            paths.extend(zip_paths)
            state["images"].extend(zip_paths)
            continue
        stem = Path(safe_name).stem
        suffix = Path(safe_name).suffix
        target = upload_dir / safe_name
        counter = 1
        while target.exists() or target.name.lower() in existing_names:
            target = upload_dir / (stem + "_" + str(counter) + suffix)
            counter += 1
        with open(target, "wb") as output:
            shutil.copyfileobj(upload_file.file, output, length=1024 * 1024)
        existing_names.add(target.name.lower())
        path_text = str(target)
        paths.append(path_text)
        state["images"].append(path_text)
    save_project_state(state)
    return paths


def _save_zip_upload(upload_dir, upload_file, existing_names):
    saved = []
    with zipfile.ZipFile(upload_file.file) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            source_name = Path(info.filename).name
            if not source_name:
                continue
            if Path(source_name).suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
                continue
            stem = Path(source_name).stem
            suffix = Path(source_name).suffix
            target = upload_dir / source_name
            counter = 1
            while target.exists() or target.name.lower() in existing_names:
                target = upload_dir / (stem + "_" + str(counter) + suffix)
                counter += 1
            with archive.open(info) as source, open(target, "wb") as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)
            existing_names.add(target.name.lower())
            saved.append(str(target))
    return saved


def export_results_zip(state):
    export_dir = RUNTIME_DIR / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    zip_path = export_dir / (state["id"] + "_classification.zip")
    groups = state.get("results", [])
    manifest_rows = []
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("project.json", json.dumps(state, ensure_ascii=False, indent=2))
        for group in groups:
            group_name = group.get("name", "Group")
            for image in group.get("images", []):
                source_path = Path(image.get("source_path", ""))
                if not source_path.exists() or not source_path.is_file():
                    continue
                filename = Path(image.get("filename") or source_path.name).name
                zip_item_path = str(Path(group_name) / filename)
                archive.write(source_path, zip_item_path)
                manifest_rows.append({
                    "group": group_name,
                    "filename": filename,
                    "source_path": str(source_path),
                    "zip_path": zip_item_path,
                })
        archive.writestr("manifest.json", json.dumps(manifest_rows, ensure_ascii=False, indent=2))
        csv_file = StringIO()
        csv_file.write("group,filename,source_path,zip_path\n")
        for row in manifest_rows:
            csv_file.write(",".join(_csv_cell(row[key]) for key in ("group", "filename", "source_path", "zip_path")) + "\n")
        archive.writestr("manifest.csv", csv_file.getvalue())
    return zip_path


def _csv_cell(value):
    text = str(value).replace('"', '""')
    return '"' + text + '"'
