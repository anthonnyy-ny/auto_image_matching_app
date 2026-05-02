# -*- coding: utf-8 -*-

import numpy as np


class VectorCandidateIndex:
    def __init__(self, dim, space="l2"):
        self.dim = dim
        self.space = space
        self.labels = []
        self.vectors = []
        self._matrix = None
        self._dirty = True
        self._hnsw = None
        self.backend = "numpy"
        try:
            import hnswlib
            self._hnswlib = hnswlib
            self.backend = "hnswlib"
        except Exception:
            self._hnswlib = None

    def __len__(self):
        return len(self.labels)

    def add(self, label, vector):
        vector = np.asarray(vector, dtype=np.float32)
        if vector.shape[0] != self.dim:
            return
        self.labels.append(label)
        self.vectors.append(vector)
        if self._matrix is not None and not self._dirty and self.backend == "numpy":
            self._matrix = np.vstack([self._matrix, vector.reshape(1, -1)]).astype(np.float32, copy=False)
        else:
            self._dirty = True

    def rebuild(self, labels, vectors):
        self.labels = list(labels)
        self.vectors = [np.asarray(vector, dtype=np.float32) for vector in vectors]
        self._dirty = True

    def query(self, vector, top_k):
        if not self.labels or top_k <= 0:
            return []
        vector = np.asarray(vector, dtype=np.float32)
        top_k = min(top_k, len(self.labels))
        if self._hnswlib is not None and len(self.labels) >= 128:
            return self._query_hnsw(vector, top_k)
        return self._query_numpy(vector, top_k)

    def _matrix_view(self):
        if self._dirty or self._matrix is None:
            if not self.vectors:
                self._matrix = np.empty((0, self.dim), dtype=np.float32)
            else:
                self._matrix = np.vstack(self.vectors).astype(np.float32, copy=False)
            self._dirty = False
        return self._matrix

    def _query_numpy(self, vector, top_k):
        matrix = self._matrix_view()
        if matrix.size == 0:
            return []
        distances = np.sum((matrix - vector) * (matrix - vector), axis=1)
        top = np.argpartition(distances, top_k - 1)[:top_k]
        top = top[np.argsort(distances[top])]
        return [(self.labels[int(index)], float(distances[int(index)])) for index in top]

    def _query_hnsw(self, vector, top_k):
        if self._dirty or self._hnsw is None:
            matrix = self._matrix_view()
            self._hnsw = self._hnswlib.Index(space=self.space, dim=self.dim)
            self._hnsw.init_index(max_elements=len(self.labels), ef_construction=120, M=16)
            self._hnsw.add_items(matrix, np.arange(len(self.labels)))
            self._hnsw.set_ef(max(32, top_k * 3))
        ids, distances = self._hnsw.knn_query(vector.reshape(1, -1), k=top_k)
        return [(self.labels[int(index)], float(distance)) for index, distance in zip(ids[0], distances[0])]
