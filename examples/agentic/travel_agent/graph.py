import logging
import os

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from langchain_tavily import TavilySearch
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt

from .prompts import (
    executor_system_prompt,
    executor_user_prompt,
    final_system_prompt,
    final_user_prompt,
    planner_system_prompt,
    planner_user_prompt,
)
from .state import TravelAgentState

logger = logging.getLogger(__name__)


MODEL = os.getenv("MODEL", "gpt-4o-mini")
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")

llm = init_chat_model(model=MODEL, model_provider=MODEL_PROVIDER)
search_tool = TavilySearch(max_results=5, topic="general")


def planner(state: TravelAgentState) -> dict:
    response = llm.invoke(
        [
            SystemMessage(content=planner_system_prompt),
            HumanMessage(
                content=planner_user_prompt.format(user_request=state["user_request"])
            ),
        ]
    )

    steps = []
    for line in response.content.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if "." in line[:4]:
            line = line.split(".", 1)[1].strip()
        steps.append(line)

    if not steps:
        raise ValueError("Planner returned no executable research steps")

    return {"plan": steps[:5], "current_step": 0, "execution_result": []}


def executor(state: TravelAgentState) -> dict:
    step_index = state["current_step"]
    if step_index >= len(state["plan"]):
        return {}

    step = state["plan"][step_index]
    query = llm.invoke(
        [
            SystemMessage(
                content="Convert the research step into one concise web search query. Return the query only."
            ),
            HumanMessage(content=step),
        ]
    ).content.strip()

    result = search_tool.invoke(query)
    parts = [
        f"title: {item.get('title', '')}, content: {item.get('content', '')}"
        for item in result.get("results", [])
    ]

    summary = llm.invoke(
        [
            SystemMessage(content=executor_system_prompt),
            HumanMessage(
                content=executor_user_prompt.format(
                    step=step,
                    search_results="\n".join(parts),
                )
            ),
        ]
    ).content.strip()

    execution_results = list(state["execution_result"])
    execution_results.append(f"Step: {step}\nResult: {summary}")

    return {
        "execution_result": execution_results,
        "current_step": step_index + 1,
    }


def route_after_executor(state: TravelAgentState) -> str:
    return "executor" if state["current_step"] < len(state["plan"]) else "draft"


def final_draft(state: TravelAgentState) -> dict:
    result = llm.invoke(
        [
            SystemMessage(content=final_system_prompt),
            HumanMessage(
                content=final_user_prompt.format(
                    user_request=state["user_request"],
                    plan="\n".join(state["plan"]),
                    results="\n".join(state["execution_result"]),
                )
            ),
        ]
    ).content.strip()
    return {"final_draft": result}


def approval_gate(state: TravelAgentState) -> dict:
    decision = interrupt(
        {
            "type": "travel_plan_approval",
            "message": "Review the proposed itinerary before publishing it.",
            "draft": state["final_draft"],
        }
    )

    if not decision.get("approved", False):
        return {"final_result": "Travel plan was not approved and was not published."}

    return {"final_result": state["final_draft"]}


def create_graph():
    graph = StateGraph(TravelAgentState)
    graph.add_node("planner", planner)
    graph.add_node("executor", executor)
    graph.add_node("draft", final_draft)
    graph.add_node("approval", approval_gate)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "executor")
    graph.add_conditional_edges(
        "executor",
        route_after_executor,
        {"executor": "executor", "draft": "draft"},
    )
    graph.add_edge("draft", "approval")
    graph.add_edge("approval", END)

    return graph.compile(checkpointer=InMemorySaver())
