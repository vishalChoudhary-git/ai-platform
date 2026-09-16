# AI Engineer / Agentic AI Trackers

This file tracks the learning path alongside the production AI Platform and the Agentic AI course.

## Project boundaries

| Project | Purpose | Current state |
|---|---|---|
| AI Platform / Expense Agent | Production-oriented AI engineering project | Existing RAG/retrieval + single Expense Agent; LangGraph migration is planned |
| Travel Agent extension | Agentic AI learning sandbox inside `app/extensions/travel` | Day 11 Plan-and-Execute learned; implementation is intentionally user-written and in progress |
| Finance Agent | Main portfolio/project for applying agent concepts | Continue extending as new agentic concepts are learned |

> Retrieval/RAG is already covered in the AI Platform / Expense work. Do not mark RAG as completed for the Finance Agent unless it is implemented there separately.

## Learning workflow

For each teacher lesson:

1. Understand the underlying concept.
2. Identify what the teacher covered and what is missing for an AI Engineer.
3. User writes the implementation in the project/extension.
4. Review the implementation and design trade-offs.
5. Add interview questions and production concerns.
6. Update this tracker.

The goal is **concept mastery + implementation ability**, not copying teacher code.

## Concept tracker

| Concept | Course status | Practical implementation | AI Engineer depth |
|---|---|---|---|
| Tool calling | Learned | Expense Agent / Travel extension | Must know |
| ReAct | Learned | Course exercises | Must know |
| State / nodes / edges | Learned | Travel extension — user implementation in progress | Must know |
| Conditional routing / loops | Learned | Travel extension — user implementation in progress | Must know |
| Short-term memory / checkpointing | Learned | Travel extension — user implementation in progress | Must know |
| Human-in-the-loop | Learned | Travel extension — user implementation in progress | Must know |
| Middleware | Learned | Course exercise | Should know |
| Plan-and-Execute | Learned | Travel extension — Day 11 | Must know |
| Replanning | Next | Not implemented | Must know |
| DAG / parallel execution | Next | Not implemented | Should know |
| Tool retries / timeouts | Gap to add | Not implemented | Must know |
| Long-term semantic memory | Gap to add | Not implemented | Should know |
| RAG / retrieval | Covered in AI Platform | Existing Expense/Knowledge pipeline | Must know |
| Evaluation | Gap to add | Not implemented in Travel extension | Must know |
| Observability / tracing | Gap to add | Not implemented in Travel extension | Must know |
| Guardrails / agent security | Gap to add | Existing platform direction; deepen with agents | Must know |

## Finance Agent implementation tracker

- [ ] Integrate LangGraph state
- [ ] Add tool calling through LangGraph
- [ ] Add short-term conversation memory
- [ ] Add checkpoint persistence
- [ ] Add human-in-the-loop for high-impact actions
- [ ] Add retries, timeouts, and bounded loops
- [ ] Add long-term memory where justified
- [ ] Add evaluation harness
- [ ] Add observability/tracing
- [ ] Add production guardrails

## Travel Agent extension tracker

- [ ] User writes planner node
- [ ] User writes executor node
- [ ] User writes conditional execution loop
- [ ] User adds checkpointed short-term memory
- [ ] User adds human approval before publishing final itinerary
- [ ] Replanner
- [ ] Parallel/DAG research
- [ ] Reliability controls
- [ ] Evaluation
- [ ] Observability

## Interview readiness

For each new topic, be able to answer all four:

1. What problem does this concept solve?
2. How does it work without the framework?
3. Why use it instead of the simpler alternative?
4. How would you make it reliable in production?

### Current questions

- What is the difference between ReAct and Plan-and-Execute?
- When should planning be explicit state versus hidden inside an agent loop?
- What does checkpointing persist, and how is that different from long-term memory?
- Where should a human approval gate exist in an agent workflow?
- When should independent plan steps execute in parallel?
- What conditions should trigger replanning?
- How do retries avoid infinite agent/tool loops?
- How would you evaluate whether a planning agent actually improved?
