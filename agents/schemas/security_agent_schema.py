from pydantic import BaseModel, Field
from typing import Literal


class OutputSchema(BaseModel):
    title: str = Field(..., description="Short name for the security issue.")
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"] = Field(..., description="How severe the security problem is.")
    line_number: int | None = Field(default=None, description="The most relevant line number, if it can be identified.")
    explanation: str = Field(..., description="Why this is a security risk.")
    suggestion: str = Field(..., description="How to fix or reduce the risk.")


class SecurityAgentOutput(BaseModel):
    issues: list[OutputSchema] = Field(
        default_factory=list, description="List of all security issues found."
    )
    summary: str = Field(..., description="Short summary of the security review.")


SubAgentOutput = SecurityAgentOutput
