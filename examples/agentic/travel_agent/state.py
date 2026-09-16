from typing import TypedDict


class TravelAgentState(TypedDict):
    user_request: str
    plan: list[str]
    current_step: int
    execution_result: list[str]
    final_draft: str
    final_result: str
