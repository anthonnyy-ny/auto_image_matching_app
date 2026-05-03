# -*- coding: utf-8 -*-

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchSettings:
    name: str = "standard"
    crop_hash_threshold: int = 10
    full_hash_prefilter: bool = False
    full_hash_reject_threshold: int = 48
    hash_candidate_threshold: int | None = None
    max_sift_candidates: int | None = None
    nearest_fallback_candidates: int = 0
    embedding_top_k: int | None = None
    hash_auto_match_threshold: int | None = None
    use_sift: bool = True
    embedding_match_threshold: float | None = None


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
    "hybrid": MatchSettings(
        "hybrid",
        crop_hash_threshold=10,
        full_hash_prefilter=True,
        full_hash_reject_threshold=50,
        hash_candidate_threshold=44,
        max_sift_candidates=24,
        nearest_fallback_candidates=8,
        embedding_top_k=64,
        hash_auto_match_threshold=5,
    ),
    "turbo": MatchSettings(
        "turbo",
        crop_hash_threshold=10,
        full_hash_prefilter=True,
        full_hash_reject_threshold=48,
        hash_candidate_threshold=40,
        max_sift_candidates=10,
        nearest_fallback_candidates=5,
        embedding_top_k=32,
        hash_auto_match_threshold=6,
    ),
    "ann": MatchSettings(
        "ann",
        crop_hash_threshold=10,
        full_hash_prefilter=True,
        full_hash_reject_threshold=48,
        hash_candidate_threshold=None,
        max_sift_candidates=None,
        nearest_fallback_candidates=0,
        embedding_top_k=16,
        hash_auto_match_threshold=6,
        use_sift=False,
        embedding_match_threshold=0.42,
    ),
    "ai": MatchSettings(
        "ai",
        crop_hash_threshold=10,
        full_hash_prefilter=True,
        full_hash_reject_threshold=52,
        hash_candidate_threshold=None,
        max_sift_candidates=None,
        nearest_fallback_candidates=0,
        embedding_top_k=24,
        hash_auto_match_threshold=4,
        use_sift=False,
        embedding_match_threshold=0.32,
    ),
    "ai-hybrid": MatchSettings(
        "ai-hybrid",
        crop_hash_threshold=10,
        full_hash_prefilter=True,
        full_hash_reject_threshold=54,
        hash_candidate_threshold=50,
        max_sift_candidates=28,
        nearest_fallback_candidates=10,
        embedding_top_k=72,
        hash_auto_match_threshold=5,
        use_sift=True,
        embedding_match_threshold=0.34,
    ),
    "ai-trained": MatchSettings(
        "ai-trained",
        crop_hash_threshold=10,
        full_hash_prefilter=True,
        full_hash_reject_threshold=54,
        hash_candidate_threshold=50,
        max_sift_candidates=32,
        nearest_fallback_candidates=12,
        embedding_top_k=96,
        hash_auto_match_threshold=5,
        use_sift=True,
        embedding_match_threshold=0.30,
    ),
}


def get_match_settings(name):
    return MATCH_SETTINGS.get(name, MATCH_SETTINGS["standard"])
