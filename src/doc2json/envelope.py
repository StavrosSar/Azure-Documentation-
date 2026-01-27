from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, List, Optional


class ExtractionError(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str
    message: str
    field: Optional[str] = None


class FieldResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: Any = None
    confidence: Optional[float] = None
    source: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


class ExtractionEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ok: bool = True
    doc_type: str
    model_id: str
    labels: Dict[str, Any]
    data: Dict[str, FieldResult]
    errors: List[ExtractionError] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)