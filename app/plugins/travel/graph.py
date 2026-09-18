import logging
import os

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from langchain_tavily import TavilySearch
from langgraph.graph import END, START, StateGraph
from prompts import (
    executor_system_prompt,
    executor_user_prompt,
    final_system_prompt,
    final_user_prompt,
    planner_system_prompt,
    planner_user_prompt,
)
from state import State

logger = logging.getLogger(__name__)

model = os.environ["LLM_MODEL"]
provider = os.environ["provider"]
# create model connection
llm = init_chat_model(model=model, model_provider=provider)

search_tool = TavilySearch(max_results=5, topic="general")


def planner(state: State):
    logger.info("Planning the research steps. %s", state)

    response = llm.invoke(
        [
            SystemMessage(content=planner_system_prompt),
            HumanMessage(content=planner_user_prompt.format(user_request=state["user_request"])),
        ]
    )
    logger.info(response.content)

    steps = []

    for line in response.content.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        steps.append(line)

    logger.info(f"after cleansing we have #{len(steps)} number of steps")
    logger.info("")

    return {"plan": steps, "current_step": 0, "execution_result": []}


def executor(state: State):
    step_index = state["current_step"]
    step = state["plan"][step_index]
    total_steps = len(state["plan"])

    logger.info(f"executor started execution job for step {step_index}/{total_steps}")
    logger.info(f"executing step: {step}")

    response = llm.invoke(
        [
            SystemMessage(
                content="""
        Convert the current step into a valid web search query.
        Return the search query ONLY. Nothing else.
        """
            ),
            HumanMessage(content=step),
        ]
    )
    search_query = response.content.strip()
    logger.info(f"search query = {search_query}")

    result = search_tool.invoke(search_query)
    parts = []
    for r in result["results"]:
        title = r["title"]
        content = r["content"]
        parts.append(f"title: {title}, content: {content}")

    logger.info("summarizing the results")

    summarized_result = llm.invoke(
        [
            SystemMessage(content=executor_system_prompt),
            HumanMessage(content=executor_user_prompt.format(step=step, search_results=parts)),
        ]
    )
    step_final_result = summarized_result.content.strip()
    execution_results = list(state["execution_result"])
    execution_results.append(f"step: {step}\nresult: {step_final_result}")
    return {"execution_result": execution_results, "current_step": step_index + 1}


def final_result(state: State):
    logger.info("generating the final result")

    result = llm.invoke(
        [
            SystemMessage(content=final_system_prompt),
            HumanMessage(
                content=final_user_prompt.format(
                    user_request=state["user_request"],
                    plan="\n".join(state["plan"]),
                    results=state["execution_result"],
                )
            ),
        ]
    )
    logger.info("")
    return {"final_result": result.content.strip()}


def route(state: State):
    if state["current_step"] < len(state["plan"]):
        return "executor"
    return "final"


def create_graph():
    graph = StateGraph(State)

    graph.add_node("planner", planner)
    graph.add_node("executor", executor)
    graph.add_node("final", final_result)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "executor")
    graph.add_conditional_edges("executor", route, {"executor": "executor", "final": "final"})
    graph.add_edge("final", END)

    app = graph.compile()
    image = app.get_graph().draw_mermaid_png()
    with open("image.png", "wb") as file:
        file.write(image)

    return app
