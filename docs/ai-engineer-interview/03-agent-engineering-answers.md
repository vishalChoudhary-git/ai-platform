# 03 — Agent Engineering — Interview Notes

## 1. What Is an AI Agent?

An AI agent is an LLM-driven system that can decide what action to take, use tools, observe results, update state, and continue until the task is complete.

A useful distinction is:

- **LLM application:** model mainly generates an answer from a fixed flow.
- **Agent:** model can choose actions and control part of the execution flow.

For production systems, use autonomy only where it adds value; deterministic workflows are often simpler and safer.

## 2. Tool / Function Calling

Tool calling lets the model request a predefined function with structured arguments instead of directly performing the action.

Typical flow:

```
User → LLM → tool call → application validates/executes tool → result → LLM → response
```

The application, not the model, should own actual tool execution and authorization.

### Why tool schemas matter

A strict schema gives the model a clear contract for tool name, parameters, types, and required fields. Validation prevents malformed or unsafe arguments from reaching downstream systems.

## 3. Agent State

Agent state is the data required to continue a workflow, such as messages, tool results, current task, intermediate decisions, approvals, and status.

State should contain **durable business/workflow state**, not blindly store the whole context forever.

## 4. Planning and Reasoning

Planning means breaking a goal into steps before or during execution.

Common approaches:

- **Direct execution:** choose the next tool/action only.
- **Plan-and-execute:** create a plan, then execute steps.
- **Replanning:** update the plan after failures or new observations.

For simple tasks, explicit planning can add unnecessary latency and tokens.

## 5. Observation and Execution Loop

A common agent loop is:

```
Reason/decide → select tool → execute → observe result → decide next step
```

The loop ends when the model reaches a valid final state or a safety/budget limit.

Production systems should enforce limits such as maximum steps, time, tokens, and tool calls.

## 6. ReAct

ReAct combines reasoning with actions and observations:

```
Thought/decision → Action → Observation → next decision
```

It is useful when the next action depends on tool results. In production, internal reasoning should not be treated as a trusted audit trail; log structured decisions, tool calls, and outcomes instead.

## 7. Plan-and-Execute

A planner creates a high-level plan, then an executor performs the steps.

**Advantages:** clearer decomposition and potentially better performance on complex tasks.

**Trade-offs:** extra model calls, stale plans, and more orchestration complexity.

Replanning is useful when external results make the original plan invalid.

## 8. Agent Architectures

### Router Agent

Chooses which specialized workflow or agent should handle the request.

```
Request → Router → Specialist A / B / C
```

Good when tasks have clear categories.

### Supervisor Agent

A central agent delegates work to specialists and combines their results.

Good for multi-step collaboration but creates a central bottleneck and control-plane dependency.

### Hierarchical Agents

Agents are organized into multiple levels, for example supervisor → sub-supervisor → workers.

Useful for large task decomposition, but coordination and observability become harder.

### Multi-Agent System

Multiple specialized agents collaborate through controlled messages, shared state, or handoffs.

Use multi-agent designs only when specialization or parallelism provides a real benefit over one agent or a deterministic workflow.

## 9. Agent Handoffs

A handoff transfers responsibility from one agent/workflow to another, usually with a structured context and clear ownership.

A good handoff specifies:

- Why the handoff happened
- What context is required
- What the next agent is allowed to do
- What result is expected

Avoid passing unnecessary history because it increases latency, cost, and confusion.

## 10. Agent Workflow vs Autonomous Agent

A deterministic workflow is preferable when the sequence is known and predictable.

An agent is useful when the path depends on dynamic information and tool results.

A practical rule:

> **Use workflows for known paths; use agents for variable decisions.**

Hybrid systems are common: deterministic control flow with LLM decisions inside bounded steps.

## 11. Memory

### Short-Term Memory

State needed during the current task or conversation, such as recent messages and intermediate results.

### Long-Term Memory

Information retained across sessions, such as user preferences or durable facts.

It should be explicitly stored, retrieved, updated, and governed; do not assume every conversation detail deserves permanent storage.

### Conversation Memory

Maintains conversational context so the agent can reference earlier turns.

A common production strategy is recent messages + summarized older history rather than sending the entire conversation every time.

### Semantic Memory

Stores factual knowledge or reusable information that can be retrieved by meaning, often using embeddings and vector search.

### Episodic Memory

Stores past events or experiences, such as what happened during a previous task execution.

## 12. Memory Retrieval and Summarization

Memory is useful only if retrieval is relevant and trustworthy.

Typical flow:

```
Current task → retrieve relevant memories → rank/filter → add selected context
```

Summarization reduces context size, but summaries can lose important details. Critical facts should be stored as structured data when possible.

## 13. Checkpointing and State Persistence

Checkpointing saves agent state so execution can resume after interruption or failure.

A production checkpoint should be associated with a workflow/execution ID and versioned state.

Important properties:

- Durable persistence
- Recoverable state
- Clear execution status
- Idempotent resume behavior

## 14. Retries, Timeouts and Recovery

### Retries

Retry transient failures such as temporary network errors, rate limits, or service unavailability.

Use exponential backoff and jitter.

Do **not** blindly retry validation errors or non-idempotent actions.

### Timeouts

Every external model/tool call should have a bounded timeout.

### Recovery

Recovery should define what happens after partial execution: retry, resume from checkpoint, compensate, ask for approval, or fail safely.

## 15. Idempotency

An operation is idempotent when repeating it produces the same intended final state.

This matters because agents may retry or resume after uncertain failures.

Example: creating a payment should use an idempotency key so a retry does not create a second payment.

## 16. Human-in-the-Loop

Human approval is appropriate for high-impact or irreversible actions such as financial transfers, account deletion, production changes, or external communications.

A good approval gate shows the proposed action and important parameters before execution.

## 17. Tool Authorization

The agent should not automatically receive every tool.

Authorization should be based on:

```
User identity + tenant + role/permissions + tool + action + resource
```

Treat tool access as a security boundary.

## 18. Tool Sandboxing

Sandboxing limits what a tool can access and what it can change.

Examples include isolated containers, restricted filesystem/network access, read-only credentials, and allowlisted commands.

Principle:

> Give the minimum capability needed for the task.

## 19. Prompt Injection

Prompt injection is an attempt to manipulate the model through untrusted instructions.

**Indirect prompt injection** happens when malicious instructions come from retrieved documents, webpages, emails, or tool output rather than the user's message.

Key defenses:

- Separate trusted instructions from untrusted data
- Restrict tool permissions
- Validate tool arguments
- Use allowlists and policy checks
- Require approval for sensitive actions
- Do not treat retrieved text as authoritative instructions

## 20. Tool Abuse and Excessive Agency

A compromised or misbehaving agent may call tools excessively, access data it should not access, or perform actions beyond the user's intent.

Mitigations include:

- Least privilege
- Tool-specific authorization
- Step/cost limits
- Rate limits
- Approval gates
- Resource scoping
- Audit logs

## 21. Data Exfiltration

Data exfiltration occurs when sensitive data is transferred to an unauthorized destination, potentially through model output, tools, or external APIs.

Defenses include permission-aware retrieval, output controls, secret filtering, destination allowlists, and preventing agents from combining unrelated permissions.

## 22. LangGraph Concepts

LangGraph models an agent as a stateful graph of nodes and edges.

Important concepts:

- **State:** shared workflow data
- **Node:** processing step
- **Edge:** transition
- **Conditional edge:** decision-based transition
- **Checkpoint:** persisted execution state
- **Human interrupt:** pause for approval or intervention

Its main strength is explicit control over stateful, cyclic, recoverable workflows.

## 23. LangChain Agent Concepts

LangChain provides abstractions for models, tools, prompts, retrievers, agents, and orchestration.

A LangChain agent typically combines an LLM with tools and an execution loop.

For production, the important engineering questions are state, reliability, observability, permissions, and deterministic control around the framework—not just the framework API.

## 24. OpenAI Agents SDK Concepts

The OpenAI Agents SDK provides primitives for building agents with models, tools, instructions, handoffs, and orchestration.

The architectural concepts remain the same regardless of framework: tool contracts, state, delegation, guardrails, approvals, tracing, and bounded execution.

## 25. MCP Concepts

Model Context Protocol (MCP) standardizes how AI applications expose and consume tools and contextual resources.

Think of MCP as a protocol boundary between an AI client and external capabilities.

A production MCP integration still needs authentication, authorization, input validation, network controls, auditability, and least privilege.

## 26. Production Agent Architecture

A practical production design often looks like:

```
Client
  ↓
API / Auth
  ↓
Agent Orchestrator
  ├─ State / Checkpoint Store
  ├─ Model Gateway
  ├─ Tool Registry + Authorization
  ├─ Memory / Retrieval
  └─ Human Approval
        ↓
External Services / Data
```

Cross-cutting concerns:

- Timeouts and retries
- Step/token/cost budgets
- Tracing and audit logs
- Idempotency
- Rate limits
- Security policies
- Failure recovery

## 27. Key Production Trade-offs

| Decision | Trade-off |
|---|---|
| One agent vs multi-agent | Simplicity vs specialization |
| Workflow vs agent | Predictability vs flexibility |
| More memory vs less memory | Context vs cost/noise |
| More autonomy vs approvals | Speed vs safety |
| More retries vs fewer retries | Resilience vs duplicate work/latency |
| More planning vs direct execution | Better decomposition vs extra calls |

## 28. Interview Questions

### Fundamentals

1. What is an AI agent, and how is it different from an LLM application?
2. What is tool/function calling?
3. Why should the application own tool execution and authorization?
4. What should be stored in agent state?
5. Explain the observe → act loop.
6. What is ReAct?
7. What is plan-and-execute?
8. When would you use replanning?

### Architecture

9. Router vs supervisor vs hierarchical agents?
10. When would you choose a multi-agent architecture?
11. When is a deterministic workflow better than an agent?
12. How would you design an enterprise agent with multiple tools?
13. How would you make an agent resumable after failure?
14. How would you handle long-running agent tasks?

### Memory

15. Short-term vs long-term memory?
16. Semantic vs episodic memory?
17. How would you prevent memory from growing indefinitely?
18. How would you retrieve only relevant memories?
19. When should a fact be stored as structured data instead of vector memory?

### Reliability

20. How do retries affect agent design?
21. How would you make tool execution idempotent?
22. What happens if a tool succeeds but the agent never receives the response?
23. How would you recover from a partially completed workflow?
24. What limits would you put on an agent?

### Security

25. What is prompt injection?
26. What is indirect prompt injection?
27. How can a retrieved document compromise an agent?
28. How would you prevent tool abuse?
29. How would you protect against data exfiltration?
30. Why is least privilege especially important for agents?
31. Where would you place a human approval gate?

### Frameworks / Practical

32. Why use LangGraph instead of a simple agent loop?
33. What problem does checkpointing solve in LangGraph?
34. What are agent handoffs?
35. What is MCP and why is it useful?
36. What remains important even when using an agent framework?