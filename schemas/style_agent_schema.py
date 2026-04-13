from pydantic import BaseModel, Field
from typing import Literal


class OutputSchema(BaseModel):
    title: str = Field(..., description="Short name for the style issue.")
    priority: Literal["MUST FIX", "SHOULD FIX", "NICE TO HAVE"] = Field(..., description="How important it is to address this issue.")
    line_number: int | None = Field(default=None, description="The most relevant line number, if it can be identified.")
    explanation: str = Field(..., description="Why this style issue matters.")
    improved_version: str = Field(..., description="Suggested improved version or rewrite.")


class StyleAgentOutput(BaseModel):
    issues: list[OutputSchema] = Field(
        default_factory=list, description="List of all style issues found."
    )
    summary: str = Field(..., description="Short summary of the style review.")
