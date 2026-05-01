# -*- coding: utf-8 -*-

import os
from pathlib import Path


SUPPORTED_IMAGE_EXTENSIONS = {
    ".bmp",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}


def iter_image_files(directory_name):
    directory = Path(directory_name)
    if not directory.exists() or not directory.is_dir():
        return []

    files = []
    for filename in os.listdir(directory):
        path = directory / filename
        if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
            files.append(path)
    return files


def collect_image_files(paths):
    files = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            files.extend(iter_image_files(path))
        elif path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
            files.append(path)
    return files


def jpg_filename(filename):
    return Path(filename).with_suffix(".jpg").name
