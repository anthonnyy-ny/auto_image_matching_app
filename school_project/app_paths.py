# -*- coding: utf-8 -*-

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
DEFAULT_IMAGE_DIR = DATASETS_DIR / "demo_data"


def default_open_dir():
    if DEFAULT_IMAGE_DIR.exists():
        return str(DEFAULT_IMAGE_DIR)
    if DATASETS_DIR.exists():
        return str(DATASETS_DIR)
    return str(Path.home())


def downloads_dir():
    path = Path.home() / "Downloads"
    path.mkdir(parents=True, exist_ok=True)
    return path


def debug_output_dir():
    path = PROJECT_ROOT / "debug_output"
    path.mkdir(parents=True, exist_ok=True)
    return path
