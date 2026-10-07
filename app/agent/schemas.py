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
    service: str = Field(min_length=1, max_length=200, pattern=r".*\S.*")
    description: str = Field(min_length=1, max_length=8000, pattern=r".*\S.*")
    backend: Literal["demo", "opensre"] = "demo"


class InvestigationResponse(BaseModel):
    service: str
    summary: str
    hypotheses: List[Hypothesis]
    human_in_the_loop: bool = True
    safe_to_continue: bool = True

    backend: Literal["demo", "opensre"] = "demo"
    status: Literal["success", "needs_input", "approval_required", "error"] = "success"
    evidence_mode: Literal["mock", "opensre"] = "mock"
    llm_mode: str = "mock"
    investigation_plan: list[str] = Field(default_factory=list)
    investigation_notes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    questions: list[dict] = Field(default_factory=list)
    denied_tools: list[str] = Field(default_factory=list)
