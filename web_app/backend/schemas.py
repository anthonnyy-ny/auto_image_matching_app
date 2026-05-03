# -*- coding: utf-8 -*-

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, StrictInt, StrictStr


class ProjectCreate(BaseModel):
    name: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str
    image_count: int


class MatchRequest(BaseModel):
    mode: Literal["strict", "standard", "loose", "fast", "hybrid", "turbo", "ann"] = "hybrid"


class ResultImage(BaseModel):
    filename: StrictStr
    source_path: StrictStr

    class Config:
        extra = "forbid"


class ResultGroup(BaseModel):
    name: StrictStr
    count: StrictInt
    images: List[ResultImage]

    class Config:
        extra = "forbid"


class MatchResponse(BaseModel):
    project_id: str
    group_count: int
    elapsed: float
    stats: Dict[str, Any]
    groups: List[ResultGroup]


class ResultsUpdate(BaseModel):
    groups: List[ResultGroup]


class ProjectImport(BaseModel):
    name: Optional[str] = None
    groups: Optional[List[ResultGroup]] = None
    results: Optional[List[ResultGroup]] = None
    stats: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "ignore"


class JobResponse(BaseModel):
    job_id: str
    status: str
