from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

from config import llm

from prompts.sub_agents_prompts import (
    security_agent_prompt,
    style_agent_prompt,
    logic_agent_prompt,
	performance_agent_prompt,
    )


from schemas.style_agent_schema import StyleAgentOutput
style_agent = create_agent(
    model=llm,
    system_prompt=style_agent_prompt,
    response_format=ToolStrategy(StyleAgentOutput),
)


from schemas.security_agent_schema import SecurityAgentOutput
security_agent = create_agent(
    model=llm,
    system_prompt=security_agent_prompt,
    response_format=ToolStrategy(SecurityAgentOutput),
)


from schemas.performance_agent_schema import PerformanceAgentOutput
performance_agent = create_agent(
    model=llm,
    system_prompt=performance_agent_prompt,
    response_format=ToolStrategy(PerformanceAgentOutput),
)


from schemas.logic_agent_schema import LogicAgentOutput
logic_agent = create_agent(
    model=llm,
    system_prompt=logic_agent_prompt,
    response_format=ToolStrategy(LogicAgentOutput),
)
