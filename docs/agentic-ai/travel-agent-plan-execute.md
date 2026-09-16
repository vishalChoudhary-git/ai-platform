# Travel Agent Learning Path

This example is intentionally separate from the production Expense Agent. It is the hands-on sandbox for the Agentic AI course.

## Current implementation

### Day 11: Plan-and-Execute
- Planner creates a bounded research plan.
- Executor runs one research step at a time.
- Conditional routing loops until all steps are complete.
- Final synthesis combines the evidence.

### Earlier concepts reused
- LangGraph state.
- Conditional loops.
- Short-term memory through checkpointing and `thread_id`.
- Human-in-the-loop approval using `interrupt()` / `Command(resume=...)`.

## Why this matters for the AI Engineer track

The objective is not to memorize LangGraph APIs. The example makes the underlying agent architecture explicit:

```text
state + planner + executor + tools + control flow + checkpointing + human approval
```

## Next extensions

The next iteration should add a real **replanner** that can modify unfinished work when evidence is weak or the user's constraints change. After that, independent research steps can be executed in parallel as a DAG, followed by reliability controls and evaluation.
