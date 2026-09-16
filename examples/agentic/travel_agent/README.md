# Travel Agent — Plan and Execute

This example applies the Agentic AI course concepts to a standalone travel-planning workflow without changing the production Expense Agent.

## Concepts combined

- Plan-and-Execute: create a bounded research plan and execute one step at a time.
- LangGraph state and conditional routing.
- Checkpointed short-term memory with a thread ID.
- Human-in-the-loop approval before publishing the itinerary.
- Explicit state boundaries between planning, execution, drafting, and approval.

## Flow

```text
User request
    ↓
Planner
    ↓
Executor ──→ more steps ──→ Executor
    ↓
Final draft
    ↓
Human approval
   ├── approved → final answer
   └── rejected → stop without publishing
```

## Run

From the repository root, install the example dependencies:

```bash
python -m pip install -r examples/agentic/travel_agent/requirements.txt
```

Set at least:

```text
MODEL_PROVIDER=openai
MODEL=gpt-4o-mini
OPENAI_API_KEY=...
TAVILY_API_KEY=...
```

Then run the module from the repository root:

```bash
python -m examples.agentic.travel_agent.main
```

Use the same `thread_id` to demonstrate checkpoint-backed conversation state across turns.

## Deliberate next extensions

1. Add a real replanner that can replace unfinished steps when evidence is insufficient.
2. Parallelize independent research steps with a DAG/fan-out pattern.
3. Add bounded retries and tool timeouts.
4. Add evaluation for plan quality, tool selection, evidence coverage, latency, and cost.
