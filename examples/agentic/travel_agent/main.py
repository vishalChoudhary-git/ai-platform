from langchain_core.messages import HumanMessage
from langgraph.types import Command

from .graph import create_graph


def main() -> None:
    app = create_graph()
    thread_id = input("Thread ID [travel-demo]: ").strip() or "travel-demo"
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            return

        state = {"user_request": user_input}
        result = app.invoke(state, config=config)

        while "__interrupt__" in result:
            request = result["__interrupt__"][0].value
            print("\n--- HUMAN REVIEW REQUIRED ---")
            print(request["draft"])
            approved = input("Approve this itinerary? [y/N]: ").strip().lower() == "y"
            result = app.invoke(Command(resume={"approved": approved}), config=config)

        print("\n--- FINAL RESULT ---\n")
        print(result["final_result"])


if __name__ == "__main__":
    main()
