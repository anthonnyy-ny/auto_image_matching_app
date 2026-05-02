# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str
    image_count: int


class MatchRequest(BaseModel):
    mode: str = "fast"


class MatchResponse(BaseModel):
    project_id: str
    group_count: int
    elapsed: float
    stats: Dict[str, Any]
    groups: List[Dict[str, Any]]


class ResultsUpdate(BaseModel):
    groups: List[Dict[str, Any]]


class JobResponse(BaseModel):
    job_id: str
    status: str
