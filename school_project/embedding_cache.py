# -*- coding: utf-8 -*-

import hashlib
import os
from pathlib import Path

import numpy as np

from app_paths import PROJECT_ROOT


class EmbeddingCache:
    VERSION = "ai-embedding-v1"

    def __init__(self):
        self.cache_dir = PROJECT_ROOT / ".cache" / "embeddings"
        self.hits = 0
        self.misses = 0
        self.writes = 0

    def reset_stats(self):
        self.hits = 0
        self.misses = 0
        self.writes = 0

    def load(self, image_path, model_key):
        cache_path = self._cache_path(image_path, model_key)
        if cache_path is None or not cache_path.exists():
            self.misses += 1
            return None
        try:
            with np.load(cache_path, allow_pickle=False) as data:
                if str(data["version"]) != self.VERSION:
                    self.misses += 1
                    return None
                self.hits += 1
                return data["embedding"].astype(np.float32, copy=False)
        except Exception:
            self.misses += 1
            return None

    def save(self, image_path, model_key, embedding):
        cache_path = self._cache_path(image_path, model_key)
        if cache_path is None:
            return
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = cache_path.with_suffix(".tmp.npz")
            np.savez_compressed(
                tmp_path,
                version=np.array(self.VERSION),
                model_key=np.array(model_key),
                embedding=np.asarray(embedding, dtype=np.float32),
            )
            os.replace(tmp_path, cache_path)
            self.writes += 1
        except Exception:
            return

    def _cache_path(self, image_path, model_key):
        try:
            resolved = str(Path(image_path).resolve())
            stat = os.stat(resolved)
        except OSError:
            return None
        signature = "|".join((
            self.VERSION,
            model_key,
            resolved,
            str(stat.st_size),
            str(stat.st_mtime_ns),
        ))
        digest = hashlib.sha1(signature.encode("utf-8", errors="ignore")).hexdigest()
        return self.cache_dir / model_key.replace("/", "_").replace("\\", "_") / (digest + ".npz")


embedding_cache = EmbeddingCache()
