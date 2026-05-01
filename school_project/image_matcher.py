# -*- coding: utf-8 -*-

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchSettings:
    name: str = "standard"
    crop_hash_threshold: int = 10
    full_hash_prefilter: bool = False
    full_hash_reject_threshold: int = 48


MATCH_SETTINGS = {
    "strict": MatchSettings("strict", crop_hash_threshold=8),
    "standard": MatchSettings("standard", crop_hash_threshold=10),
    "loose": MatchSettings("loose", crop_hash_threshold=14),
    "fast": MatchSettings(
        "fast",
        crop_hash_threshold=10,
        full_hash_prefilter=True,
        full_hash_reject_threshold=48,
    ),
}


def get_match_settings(name):
    return MATCH_SETTINGS.get(name, MATCH_SETTINGS["standard"])
