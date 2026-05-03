# -*- coding: utf-8 -*-

from neural_image_framework import get_neural_framework


def ai_embedding(image, image_path=None, hash_str=None):
    return get_neural_framework().encode(image, image_path, hash_str)


def ai_embedding_metadata():
    return get_neural_framework().metadata()


def reload_ai_embedding():
    return get_neural_framework().reload()


def get_ai_engine():
    return get_neural_framework()
