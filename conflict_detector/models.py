from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class Annotation(BaseModel):
    annotator: str = Field(..., description="Annotator identifier")
    intent: str = Field(..., description="Intent label")
    urgency: str = Field(..., description="Urgency label")

    @property
    def label(self) -> str:
        """Composite label used for conflict detection."""
        return f"{self.intent}|{self.urgency}"


class Ticket(BaseModel):
    id: str
    text: str
    annotations: List[Annotation]


class LabelEntry(BaseModel):
    annotator: str
    label: str


class Resolution(BaseModel):
    majority_label: str
    confidence: float
    explanation: str


class OutputSample(BaseModel):
    id: str
    text: str
    labels: List[LabelEntry]
    is_conflict: bool
    conflict_reason: Optional[str]
    suggested_label: str
    resolution: Optional[Resolution] = None
