from typing import List, Literal

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    source: Literal["logs", "metrics", "traces", "deployments", "incidents"]
    summary: str
    detail: str


class Hypothesis(BaseModel):
    rank: int
    title: str
    likelihood: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[EvidenceItem]
    recommended_next_steps: List[str]


class InvestigationRequest(BaseModel):
    service: str
    description: str


class InvestigationResponse(BaseModel):
    service: str
    summary: str
    hypotheses: List[Hypothesis]
    human_in_the_loop: bool = True
    safe_to_continue: bool = True
