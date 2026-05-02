# -*- coding: utf-8 -*-

import time
from pathlib import Path

import cv2

from controller import IMG, classification, sift_ahash
from feature_cache import feature_cache
from image_matcher import get_match_settings
from image_utils import collect_image_files


def scan_images(input_paths, progress=None):
    start = time.time()
    feature_cache.reset_stats()
    image_files = collect_image_files(input_paths)
    loaded_images = []
    skipped = []
    total = len(image_files)

    for count, image_path in enumerate(image_files, start=1):
        try:
            item = IMG(str(image_path), image_path.name)
            item.img_shape()
            item.create_sift()
            loaded_images.append(item)
        except Exception as exc:
            skipped.append({"path": str(image_path), "error": str(exc)})
        if progress and total:
            progress(int(count / total * 100))

    return {
        "images": loaded_images,
        "elapsed": time.time() - start,
        "skipped": skipped,
        "stats": {
            "cache_hits": feature_cache.hits,
            "cache_misses": feature_cache.misses,
            "cache_writes": feature_cache.writes,
        },
    }


def match_images(images, mode="fast", progress=None):
    start = time.time()
    settings = get_match_settings(mode)
    groups = []
    stats = {
        "candidate_rejects": 0,
        "sift_calls": 0,
        "merged_groups": 0,
    }
    total = len(images)

    for index, image_item in enumerate(images):
        if progress and total:
            progress(int(index / total * 100))

        matched = False
        for group_index, group in enumerate(groups):
            representative = group.same[0]
            if settings.full_hash_prefilter and image_item.hash_str and representative.hash_str:
                from controller import cam_hash
                if cam_hash(image_item.hash_str, representative.hash_str) > settings.full_hash_reject_threshold:
                    stats["candidate_rejects"] += 1
                    continue
            stats["sift_calls"] += 1
            is_same, is_big = sift_ahash(image_item, representative, settings, cv2.BFMatcher(crossCheck=True))
            if is_same:
                matched = True
                group.save_img(image_item, is_big)
                if is_big:
                    merge_indexes = []
                    for merge_index in range(group_index + 1, len(groups)):
                        stats["sift_calls"] += 1
                        merge_same, merge_big = sift_ahash(
                            groups[merge_index].same[0],
                            group.same[0],
                            settings,
                            cv2.BFMatcher(crossCheck=True),
                        )
                        if merge_same and not merge_big:
                            group.union(groups[merge_index])
                            merge_indexes.append(merge_index)
                            stats["merged_groups"] += 1
                    for merge_index in sorted(merge_indexes, reverse=True):
                        del groups[merge_index]
                break
        if not matched:
            groups.append(classification(image_item))

    if progress:
        progress(100)

    groups = sorted(groups, key=lambda item: item.img_count)
    return {
        "groups": groups,
        "elapsed": time.time() - start,
        "stats": stats,
    }


def serialize_groups(groups):
    group_count = len(groups)
    group_number_width = max(2, len(str(group_count)))
    payload = []
    for group_index, group in enumerate(groups, start=1):
        group_name = "Group" + str(group_index).zfill(group_number_width)
        payload.append({
            "name": group_name,
            "count": len(group.same),
            "images": [
                {
                    "filename": image.filename,
                    "source_path": image.name,
                }
                for image in group.same
            ],
        })
    return payload


def image_paths_from_upload_dir(upload_dir):
    return [str(path) for path in Path(upload_dir).iterdir() if path.is_file()]
