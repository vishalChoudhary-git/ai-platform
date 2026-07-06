dev:
	uv run uvicorn main:app --reload

start:
	uv run uvicorn main:app --host 0.0.0.0 --port 8000

lint:
	uv run ruff check .

format:
	uv run ruff format .

test:
	uv run pytest