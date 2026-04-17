from langgraph.graph import MessagesState
from pydantic import BaseModel, Field

from agents.schemas.security_agent_schema import SecurityAgentOutput
from agents.schemas.performance_agent_schema import PerformanceAgentOutput
from agents.schemas.logic_agent_schema import LogicAgentOutput
from agents.schemas.style_agent_schema import StyleAgentOutput


class FinalReport(BaseModel):
    overall_score: int = Field(..., ge=0, le=100, description="Overall code quality score from 0 to 100.")
    executive_summary: str = Field(..., description="Short executive summary of the full review.")
    security: SecurityAgentOutput = Field(..., description="Security review output.")
    performance: PerformanceAgentOutput = Field(..., description="Performance review output.")
    logic: LogicAgentOutput = Field(..., description="Logic review output.")
    style: StyleAgentOutput = Field(..., description="Style review output.")
    top_priorities: list[str] = Field(
        default_factory=list,
        description="The most important issues to fix first.",
)

class GraphState(MessagesState):
    code : str = Field(..., description="Code to be reviewed.")
    language : str = Field(..., description="Language of the code.")
    
    security_review : SecurityAgentOutput | None = Field(None, description="Security review output.")
    performance_review : PerformanceAgentOutput | None = Field(None, description="Performance review output.")
    logic_review : LogicAgentOutput | None = Field(None, description="Logic review output.")
    style_review : StyleAgentOutput | None = Field(None, description="Style review output.")

    final_report: FinalReport | None = Field(None, description="Final synthesized review report.")