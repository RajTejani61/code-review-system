from pydantic import BaseModel, Field
from typing import Literal


class OutputSchema(BaseModel):
    title: str = Field(..., description="Short name for the logic issue.")
    severity: Literal["HIGH", "MEDIUM", "LOW"] = Field(..., description="How severe the bug is.")
    line_number: int | None = Field(default=None, description="The most relevant line number, if it can be identified.")
    explanation: str = Field(..., description="Why the code is logically incorrect.")
    suggestion: str = Field(..., description="Suggested fix or correction.")
    example_input: str | None = Field(default=None, description="Example input that would trigger the bug.")
    corrected_code: str | None = Field(default=None, description="Corrected code snippet if one can be suggested.")


class LogicAgentOutput(BaseModel):
    issues: list[OutputSchema] = Field(default_factory=list, description="List of all logic issues found.")
    summary: str = Field(..., description="Short summary of the logic review.")
