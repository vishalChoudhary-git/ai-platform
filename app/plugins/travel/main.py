import logging

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

console = Console()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s - %(message)s")
# load the configurations from .env file
load_dotenv()

from graph import create_graph  # noqa: E402

app = create_graph()

while True:
    user_input = input("> ")
    if user_input in ["exit", "quit"]:
        break

    state = {"user_request": user_input}

    response = app.invoke(state)
    console.print(Markdown(response["final_result"]))
