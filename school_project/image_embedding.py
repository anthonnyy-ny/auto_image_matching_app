# -*- coding: utf-8 -*-

import cv2
import numpy as np


def hash_bits(hash_str):
    if not hash_str or len(hash_str) < 64:
        return np.zeros(64, dtype=np.float32)
    return np.fromiter((1.0 if char == "1" else 0.0 for char in hash_str[:64]), dtype=np.float32, count=64)


def image_embedding(image, hash_str=None):
    if image is None:
        return np.zeros(131, dtype=np.float32)
    if image.size == 0:
        return np.zeros(131, dtype=np.float32)
    h, w = image.shape[:2]
    if h <= 0 or w <= 0:
        return np.zeros(131, dtype=np.float32)

    small = cv2.resize(image, (32, 32), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    hist_h = cv2.calcHist([hsv], [0], None, [32], [0, 180]).flatten()
    hist_s = cv2.calcHist([hsv], [1], None, [16], [0, 256]).flatten()
    hist_v = cv2.calcHist([hsv], [2], None, [16], [0, 256]).flatten()
    color = np.concatenate([hist_h, hist_s, hist_v]).astype(np.float32)
    color_sum = float(color.sum())
    if color_sum > 0:
        color /= color_sum

    aspect = np.array([min(4.0, max(0.25, w / max(1, h))) / 4.0], dtype=np.float32)
    vector = np.concatenate([hash_bits(hash_str), color * 4.0, aspect, np.array([w / 4096.0, h / 4096.0], dtype=np.float32)])
    norm = float(np.linalg.norm(vector))
    if norm > 0:
        vector /= norm
    return vector.astype(np.float32, copy=False)
