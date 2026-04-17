from pydantic import BaseModel, Field
from typing import Literal


class OutputSchema(BaseModel):
    title: str = Field(..., description="Short name for the performance issue.")
    impact: Literal["HIGH", "MEDIUM", "LOW"] = Field(..., description="How strongly this issue affects performance.")
    line_number: int | None = Field(default=None, description="The most relevant line number, if it can be identified.")
    complexity: str = Field(..., description="Explain the current inefficiency or complexity.")
    suggestion: str = Field(..., description="Optimized alternative or fix.")
    expected_improvement: str = Field(..., description="Expected improvement from applying the optimization.")


class PerformanceAgentOutput(BaseModel):
    issues: list[OutputSchema] = Field(default_factory=list, description="List of all performance issues found.")
    summary: str = Field(..., description="Short summary of the performance review.")
