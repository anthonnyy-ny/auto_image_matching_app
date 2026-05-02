# -*- coding: utf-8 -*-

import hashlib
import os
from pathlib import Path

import cv2
import numpy as np

from app_paths import feature_cache_dir


class FeatureCache:
    VERSION = "sift-v2"

    def __init__(self):
        self.cache_dir = feature_cache_dir()
        self.hits = 0
        self.misses = 0
        self.writes = 0

    def reset_stats(self):
        self.hits = 0
        self.misses = 0
        self.writes = 0

    def load(self, image_path):
        cache_path = self._cache_path(image_path)
        if cache_path is None or not cache_path.exists():
            self.misses += 1
            return None
        try:
            with np.load(cache_path, allow_pickle=False) as data:
                if str(data["version"]) != self.VERSION:
                    self.misses += 1
                    return None
                keypoints = self._decode_keypoints(data["keypoints"])
                descriptors = data["descriptors"]
                if descriptors.size == 0:
                    descriptors = None
                else:
                    descriptors = descriptors.astype(np.float32, copy=False)
                self.hits += 1
                return {
                    "hash_str": str(data["hash_str"]),
                    "keypoints": keypoints,
                    "descriptors": descriptors,
                }
        except Exception:
            self.misses += 1
            return None

    def save(self, image_path, hash_str, keypoints, descriptors):
        cache_path = self._cache_path(image_path)
        if cache_path is None:
            return
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            keypoint_array = self._encode_keypoints(keypoints)
            if descriptors is None:
                descriptor_array = np.empty((0, 128), dtype=np.float32)
            else:
                descriptor_array = descriptors.astype(np.float32, copy=False)
            tmp_path = cache_path.with_suffix(".tmp.npz")
            np.savez_compressed(
                tmp_path,
                version=np.array(self.VERSION),
                hash_str=np.array(hash_str),
                keypoints=keypoint_array,
                descriptors=descriptor_array,
            )
            os.replace(tmp_path, cache_path)
            self.writes += 1
        except Exception:
            return

    def _cache_path(self, image_path):
        try:
            resolved = str(Path(image_path).resolve())
            stat = os.stat(resolved)
        except OSError:
            return None
        signature = "|".join((
            self.VERSION,
            resolved,
            str(stat.st_size),
            str(stat.st_mtime_ns),
        ))
        digest = hashlib.sha1(signature.encode("utf-8", errors="ignore")).hexdigest()
        return self.cache_dir / (digest + ".npz")

    def _encode_keypoints(self, keypoints):
        rows = []
        for kp in keypoints or []:
            rows.append((
                kp.pt[0],
                kp.pt[1],
                kp.size,
                kp.angle,
                kp.response,
                kp.octave,
                kp.class_id,
            ))
        return np.array(rows, dtype=np.float32)

    def _decode_keypoints(self, keypoint_array):
        keypoints = []
        for row in keypoint_array:
            keypoints.append(cv2.KeyPoint(
                float(row[0]),
                float(row[1]),
                float(row[2]),
                float(row[3]),
                float(row[4]),
                int(row[5]),
                int(row[6]),
            ))
        return keypoints


feature_cache = FeatureCache()
