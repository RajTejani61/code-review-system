import asyncio
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage, SystemMessage

from config import llm
from schemas.orchestrator_schema import FinalReport, GraphState
from prompts.orchestrator_prompt import orchestrator_agent_prompt

from agents.sub_agents import security_agent, performance_agent, logic_agent, style_agent

sub_agents_input_message = """
    Review the following code written in {language} and provide feedback.

    CODE:
    {code}
"""

def get_input_payload(state: GraphState):
    user_message = sub_agents_input_message.format(
        language=state["language"],
        code=state["code"],
    )
    return {"messages" : [{"role" : "user", "content" : user_message}]}

async def security_node(state: GraphState) -> dict:
    """Invoke the security agent."""
    result = await security_agent.ainvoke(get_input_payload(state))
    return {"security_review": result["structured_response"]}

async def performance_node(state: GraphState) -> dict:
    """Invoke the performance agent."""
    result = await performance_agent.ainvoke(get_input_payload(state))
    return {"performance_review": result["structured_response"]}

async def logic_node(state: GraphState) -> dict:
    """Invoke the logic agent."""
    result = await logic_agent.ainvoke(get_input_payload(state))
    return {"logic_review": result["structured_response"]}

async def style_node(state: GraphState) -> dict:
    """Invoke the style agent."""
    result = await style_agent.ainvoke(get_input_payload(state))
    return {"style_review": result["structured_response"]}


async def generate_final_report(state: GraphState) -> dict:
    """Feed all sub-agent outputs to the orchestrator LLM and get FinalReport."""
    
    orchestrator_llm = llm.with_structured_output(FinalReport)

    synthesis_prompt = f"""
        Here are the outputs from the four specialized review agents:

        SECURITY REVIEW:
        {state["security_review"].model_dump_json(indent=2) if state.get("security_review") else "None"}

        PERFORMANCE REVIEW:
        {state["performance_review"].model_dump_json(indent=2) if state.get("performance_review") else "None"}

        LOGIC REVIEW:
        {state["logic_review"].model_dump_json(indent=2) if state.get("logic_review") else "None"}

        STYLE REVIEW:
        {state["style_review"].model_dump_json(indent=2) if state.get("style_review") else "None"}

        Synthesize all of the above into a single final report as per your instructions.
    """

    messages = [
        SystemMessage(content=orchestrator_agent_prompt),
        HumanMessage(content=synthesis_prompt),
    ]

    final_report: FinalReport = await orchestrator_llm.ainvoke(messages)
    return {"final_report": final_report}


def build_graph():
    checkpointer = InMemorySaver()

    graph = StateGraph(GraphState)
    
    # Add nodes for each agent
    graph.add_node("security_node", security_node)
    graph.add_node("performance_node", performance_node)
    graph.add_node("logic_node", logic_node)
    graph.add_node("style_node", style_node)
    graph.add_node("generate_final_report", generate_final_report)

    # Parallel execution from START
    graph.add_edge(START, "security_node")
    graph.add_edge(START, "performance_node")
    graph.add_edge(START, "logic_node")
    graph.add_edge(START, "style_node")

    # All nodes must finish before synthesis
    graph.add_edge("security_node", "generate_final_report")
    graph.add_edge("performance_node", "generate_final_report")
    graph.add_edge("logic_node", "generate_final_report")
    graph.add_edge("style_node", "generate_final_report")

    graph.add_edge("generate_final_report", END)

    return graph.compile(checkpointer=checkpointer)


orchestrator_graph = build_graph()


async def run_review(code: str, language: str) -> FinalReport:
    """Convenience wrapper - call this from your API / CLI."""
    
    result = await orchestrator_graph.ainvoke(
        {"code": code, "language": language, "messages": []},
        config={"configurable": {"thread_id": "review-session"}},
    )

    return result["final_report"]
