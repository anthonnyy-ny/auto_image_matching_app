# -*- coding: utf-8 -*-

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from app_paths import web_runtime_dir


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


def save_project_state(state):
    state["updated_at"] = datetime.now().isoformat(timespec="seconds")
    with open(state_path(state["id"]), "w", encoding="utf-8") as json_file:
        json.dump(state, json_file, ensure_ascii=False, indent=2)


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
