from typing import TypedDict


class State(TypedDict):
    user_request: str
    plan: list[str]
    current_step: int
    execution_result: list[str]
    final_result: str
