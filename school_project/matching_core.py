# -*- coding: utf-8 -*-

import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import cv2
import numpy as np

from controller import IMG, a_hash, classification, sift_ahash
from ai_embedding import ai_embedding, ai_embedding_metadata
from embedding_cache import embedding_cache
from feature_cache import feature_cache
from image_embedding import image_embedding
from image_matcher import get_match_settings
from image_utils import collect_image_files
from vector_index import VectorCandidateIndex


class MatchCancelled(Exception):
    pass


AI_MODES = {"ai", "ai-hybrid", "ai-trained"}
LAZY_FEATURE_MODES = {"hybrid", "turbo", "ann", *AI_MODES}


def scan_images(input_paths, progress=None, should_cancel=None, lazy_features=False, use_ai=False):
    start = time.time()
    feature_cache.reset_stats()
    embedding_cache.reset_stats()
    image_files = collect_image_files(input_paths)
    loaded_items = []
    skipped = []
    total = len(image_files)
    max_workers = min(8, max(1, (os.cpu_count() or 2) - 1), max(1, total))

    def load_image(index, image_path):
        if should_cancel and should_cancel():
            raise MatchCancelled("Match job cancelled")
        item = IMG(str(image_path), image_path.name)
        item.img_shape()
        if lazy_features:
            cached_hash = feature_cache.load_hash(item.name)
            if cached_hash is not None:
                item.hash_str = cached_hash
                item.features_ready = False
            else:
                item.hash_str = a_hash(item.img)
                item.features_ready = False
        else:
            item.create_sift()
            item.features_ready = True
        if use_ai:
            item.embedding = ai_embedding(item.img, item.name, item.hash_str)
        else:
            item.embedding = image_embedding(item.img, item.hash_str)
        return index, item

    if total:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(load_image, index, image_path): image_path
                for index, image_path in enumerate(image_files)
            }
            for count, future in enumerate(as_completed(future_map), start=1):
                if should_cancel and should_cancel():
                    raise MatchCancelled("Match job cancelled")
                image_path = future_map[future]
                try:
                    loaded_items.append(future.result())
                except Exception as exc:
                    skipped.append({"path": str(image_path), "error": str(exc)})
                if progress:
                    progress(int(count / total * 100))

    loaded_items.sort(key=lambda item: item[0])
    loaded_images = [item for _, item in loaded_items]

    return {
        "images": loaded_images,
        "elapsed": time.time() - start,
        "skipped": skipped,
        "stats": {
            "cache_hits": feature_cache.hits,
            "cache_misses": feature_cache.misses,
            "cache_writes": feature_cache.writes,
            "embedding_cache_hits": embedding_cache.hits,
            "embedding_cache_misses": embedding_cache.misses,
            "embedding_cache_writes": embedding_cache.writes,
            "lazy_features": lazy_features,
            "parallel_scan_workers": max_workers,
            **(ai_embedding_metadata() if use_ai else {}),
        },
    }


def match_images(images, mode="fast", progress=None, should_cancel=None, stats_callback=None):
    start = time.time()
    settings = get_match_settings(mode)
    groups = []
    rep_embeddings = []
    rep_matrix_cache = [None]
    rep_matrix_dirty = [True]
    vector_index = [VectorCandidateIndex(len(images[0].embedding)) if images and getattr(images[0], "embedding", None) is not None else None]
    vector_index_dirty = [True]
    embedding_distances = {}
    total = len(images)
    stats = {
        "mode": mode,
        "ai_enabled": mode in AI_MODES,
        "candidate_rejects": 0,
        "hash_candidates_considered": 0,
        "embedding_candidates": 0,
        "vector_backend": "none",
        "limited_candidates": 0,
        "sift_calls": 0,
        "hash_auto_matches": 0,
        "parallel_tasks": 0,
        "merged_groups": 0,
        "processed_images": 0,
        "current_image": 0,
        "total_images": total,
        "current_groups": 0,
        "last_candidates": 0,
        "images_per_second": 0.0,
        "eta_seconds": None,
    }
    max_workers = min(4, max(1, (os.cpu_count() or 2) - 1))
    last_stats_emit = [0.0]

    def emit_stats(force=False):
        now = time.time()
        if not force and now - last_stats_emit[0] < 0.5:
            return
        last_stats_emit[0] = now
        stats["current_groups"] = len(groups)
        elapsed = max(0.001, now - start)
        stats["images_per_second"] = round(stats["processed_images"] / elapsed, 2)
        if stats["processed_images"] and total:
            remaining = total - stats["processed_images"]
            stats["eta_seconds"] = int(remaining / max(0.001, stats["images_per_second"]))
        if stats_callback:
            stats_callback(dict(stats))

    def quick_reject(first, second):
        if settings.full_hash_prefilter and first.hash_str and second.hash_str:
            from controller import cam_hash
            if cam_hash(first.hash_str, second.hash_str) > settings.full_hash_reject_threshold:
                stats["candidate_rejects"] += 1
                return True
        return False

    def embedding_prefilter(image_item, start_index):
        if settings.embedding_top_k is None or len(rep_embeddings) <= settings.embedding_top_k:
            return list(range(start_index, len(groups)))
        query = getattr(image_item, "embedding", None)
        if query is None:
            return list(range(start_index, len(groups)))
        if start_index == 0:
            if vector_index[0] is None:
                vector_index[0] = VectorCandidateIndex(len(query))
            if vector_index_dirty[0]:
                vector_index[0].rebuild(range(len(rep_embeddings)), rep_embeddings)
                vector_index_dirty[0] = False
            stats["vector_backend"] = vector_index[0].backend
            hits = vector_index[0].query(query, settings.embedding_top_k)
            embedding_distances.clear()
            for label, distance in hits:
                embedding_distances[int(label)] = float(distance)
            stats["embedding_candidates"] += len(hits)
            return [int(label) for label, _ in hits]
        if rep_matrix_dirty[0] or rep_matrix_cache[0] is None:
            rep_matrix_cache[0] = np.asarray(rep_embeddings, dtype=np.float32)
            rep_matrix_dirty[0] = False
        matrix = rep_matrix_cache[0][start_index:]
        if matrix.size == 0:
            return []
        distances = np.sum((matrix - query) * (matrix - query), axis=1)
        top_count = min(settings.embedding_top_k, len(distances))
        top_local = np.argpartition(distances, top_count - 1)[:top_count]
        ordered_local = top_local[np.argsort(distances[top_local])]
        stats["embedding_candidates"] += int(top_count)
        embedding_distances.clear()
        for index in ordered_local:
            embedding_distances[start_index + int(index)] = float(distances[int(index)])
        return [start_index + int(index) for index in ordered_local]

    def candidate_indices(image_item, start_index=0):
        candidates = []
        rejected = []
        indexes = embedding_prefilter(image_item, start_index)
        for index in indexes:
            if should_cancel and should_cancel():
                raise MatchCancelled("Match job cancelled")
            representative = groups[index].same[0]
            distance = None
            if settings.full_hash_prefilter and image_item.hash_str and representative.hash_str:
                from controller import cam_hash
                distance = cam_hash(image_item.hash_str, representative.hash_str)
                if settings.hash_candidate_threshold is not None and distance > settings.hash_candidate_threshold:
                    rejected.append((distance, index))
                    stats["candidate_rejects"] += 1
                    continue
                if distance > settings.full_hash_reject_threshold:
                    rejected.append((distance, index))
                    stats["candidate_rejects"] += 1
                    continue
            elif quick_reject(image_item, representative):
                continue
            candidates.append((distance if distance is not None else 0, index))
        stats["hash_candidates_considered"] += len(candidates)
        candidates.sort(key=lambda item: item[0])
        if not candidates and settings.nearest_fallback_candidates > 0:
            rejected.sort(key=lambda item: item[0])
            candidates = rejected[:settings.nearest_fallback_candidates]
        if settings.max_sift_candidates is not None and len(candidates) > settings.max_sift_candidates:
            stats["limited_candidates"] += len(candidates) - settings.max_sift_candidates
            candidates = candidates[:settings.max_sift_candidates]
        stats["last_candidates"] = len(candidates)
        return [index for _, index in candidates]

    def compare_candidate(image_item, group):
        ensure_features(image_item)
        ensure_features(group.same[0])
        return sift_ahash(image_item, group.same[0], settings, cv2.BFMatcher(crossCheck=True))

    def hash_auto_match(image_item, group):
        if settings.hash_auto_match_threshold is None:
            return None
        representative = group.same[0]
        if not image_item.hash_str or not representative.hash_str:
            return None
        from controller import cam_hash
        distance = cam_hash(image_item.hash_str, representative.hash_str)
        if distance > settings.hash_auto_match_threshold:
            return None
        area_ratio = image_item.area / max(1, representative.area)
        width_ratio = image_item.width / max(1, representative.width)
        height_ratio = image_item.hight / max(1, representative.hight)
        if 0.72 <= area_ratio <= 1.38 and 0.72 <= width_ratio <= 1.38 and 0.72 <= height_ratio <= 1.38:
            stats["hash_auto_matches"] += 1
            if not settings.use_sift:
                return False
            return image_item.area > representative.area
        return None

    def ensure_features(image_item):
        if getattr(image_item, "features_ready", False):
            return
        image_item.create_sift()
        image_item.features_ready = True

    def find_first_match(image_item, candidates):
        if not candidates:
            return None
        results = {}
        for index in candidates:
            auto_big = hash_auto_match(image_item, groups[index])
            if auto_big is not None:
                return index, auto_big
        if not settings.use_sift:
            threshold = settings.embedding_match_threshold
            if threshold is None:
                return None
            for index in candidates:
                if embedding_distances.get(index, 999.0) <= threshold:
                    return index, False
            return None
        worker_count = min(max_workers, len(candidates))
        if worker_count <= 1:
            for index in candidates:
                if should_cancel and should_cancel():
                    raise MatchCancelled("Match job cancelled")
                stats["sift_calls"] += 1
                results[index] = compare_candidate(image_item, groups[index])
                emit_stats()
        else:
            stats["parallel_tasks"] += len(candidates)
            with ThreadPoolExecutor(max_workers=worker_count) as executor:
                future_map = {
                    executor.submit(compare_candidate, image_item, groups[index]): index
                    for index in candidates
                }
                for future in as_completed(future_map):
                    if should_cancel and should_cancel():
                        raise MatchCancelled("Match job cancelled")
                    index = future_map[future]
                    stats["sift_calls"] += 1
                    try:
                        results[index] = future.result()
                    except Exception:
                        results[index] = (False, False)
        for index in candidates:
            is_same, is_big = results.get(index, (False, False))
            if is_same:
                return index, is_big
        return None

    for index, image_item in enumerate(images):
        if should_cancel and should_cancel():
            raise MatchCancelled("Match job cancelled")
        if progress and total:
            progress(int(index / total * 100))
        stats["current_image"] = index + 1

        first_match = find_first_match(image_item, candidate_indices(image_item))
        if first_match is not None:
            group_index, is_big = first_match
            group = groups[group_index]
            group.save_img(image_item, is_big)
            if is_big:
                rep_embeddings[group_index] = getattr(group.same[0], "embedding", image_embedding(group.same[0].img, group.same[0].hash_str))
                rep_matrix_dirty[0] = True
                vector_index_dirty[0] = True
            if is_big:
                merge_indexes = []
                for merge_index in candidate_indices(group.same[0], group_index + 1):
                    if should_cancel and should_cancel():
                        raise MatchCancelled("Match job cancelled")
                    stats["sift_calls"] += 1
                    merge_same, merge_big = compare_candidate(groups[merge_index].same[0], group)
                    if merge_same and not merge_big:
                        group.union(groups[merge_index])
                        merge_indexes.append(merge_index)
                        stats["merged_groups"] += 1
                for merge_index in sorted(merge_indexes, reverse=True):
                    del groups[merge_index]
                    del rep_embeddings[merge_index]
                    rep_matrix_dirty[0] = True
                    vector_index_dirty[0] = True
        else:
            groups.append(classification(image_item))
            embedding = getattr(image_item, "embedding", image_embedding(image_item.img, image_item.hash_str))
            rep_embeddings.append(embedding)
            if vector_index[0] is not None:
                vector_index[0].add(len(rep_embeddings) - 1, embedding)
            rep_matrix_dirty[0] = True
        stats["processed_images"] = index + 1
        if index == 0 or (index + 1) % 10 == 0 or index + 1 == total:
            emit_stats(force=True)

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
