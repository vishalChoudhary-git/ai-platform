# LangChain Concept 11 — Agents

**Status:** Complete

## Definition

> **An Agent is a system where a language model dynamically decides what actions to take, commonly by selecting tools, observing their results, and continuing until a stopping condition is reached.**

Mental model:

```text
User
 ↓
Agent
 ↓
LLM decides next action
 ↓
Tool / answer
 ↓
Observation / result
 ↓
LLM decides again
 ↓
...
 ↓
Final answer
```

## Agent vs Chain

```text
Chain
→ application-defined flow
→ A → B → C

Agent
→ model-directed action selection
→ decide → act → observe → decide again
```

An agent still operates inside a developer-controlled harness containing tools, state, policies and execution controls.

## Core pieces

Conceptually:

```text
Agent
 ├── Model
 ├── Prompt / instructions
 ├── Tools
 ├── State/context
 └── Execution loop
```

The loop is what makes the system agentic: the model can choose whether to act and what to do next.

## Agent loop

```text
START
  ↓
Model
  ↓
Tool call?
 /       \
YES       NO
 ↓         ↓
Tool      END
 ↓
Tool result
 ↓
Update state
 ↓
Model
 ↓
Tool call?
```

An agent does not have to call a tool. It can answer directly.

## Tool Calling vs Agent

```text
Tool Calling
→ mechanism for requesting a tool

Agent
→ broader decision loop using tool calling plus state/control
```

## Agent state

Typical state may contain:

```text
messages
user/task context
tool results
retrieved information
intermediate decisions
retry counters
workflow status
```

State is the evolving workflow data; long-term memory is a separate persistence/design concern.

## Agent + RAG

### Fixed RAG

```text
Question
 ↓
Retriever
 ↓
Prompt
 ↓
LLM
 ↓
Answer
```

### Agentic RAG

```text
Question
 ↓
Agent / LLM
 ↓
Need knowledge?
 /       \
NO        YES
 ↓          ↓
Answer    Search Tool
              ↓
          Retriever
              ↓
          Documents
              ↓
            Agent
```

The agent can decide whether retrieval is necessary and may repeat retrieval or call other tools.

## ReAct

ReAct is the common idea of interleaving reasoning and actions:

```text
Reason
 ↓
Act
 ↓
Observe
 ↓
Reason
 ↓
Act
 ↓
...
```

For interviews, remember the interaction pattern rather than implementation details.

## Agent harness

A useful modern mental model is:

```text
Agent = Model + Harness
```

The model supplies the decision-making signal. The harness supplies:

```text
tools
state
execution
limits
policies
persistence
interrupts
```

The model does not directly execute application capabilities.

## Agent middleware / controls

Production agents need bounded and controlled execution. Useful controls include:

- model-call limits
- tool-call limits
- timeouts
- retries/fallbacks
- dynamic prompts
- tool validation
- authorization
- context trimming
- human approval for sensitive actions
- tracing

## Security

Treat model-generated tool calls as untrusted input.

```text
LLM intent
   ↓
schema validation
   ↓
authentication / authorization
   ↓
business policy
   ↓
service
   ↓
repository / external system
```

Do not make the LLM the authorization boundary.

## Failure modes

```text
wrong tool
wrong arguments
tool failure
provider timeout
unbounded loops
poor reasoning
stale / incorrect retrieved context
```

Use explicit limits and error handling to prevent runaway execution.

## LangChain current positioning

Modern LangChain provides a high-level `create_agent` API for common tool-using agent workflows. The agent runtime is graph-based underneath, while LangGraph provides lower-level explicit graph/state orchestration when more control is required.

Mental model:

```text
LangChain create_agent
→ convenient high-level agent abstraction

LangGraph
→ explicit stateful graph orchestration
```

## Agent vs LangGraph

Do not say that LangChain agents cannot loop. Modern LangChain agents can run model/tool loops and are built on LangGraph.

The practical distinction is level of abstraction:

```text
High-level agent
→ standard model/tool loop

LangGraph
→ explicit control over nodes, edges, state,
   routing, persistence and interrupts
```

## Interview questions

### What is an Agent?

> An agent is a system where a language model dynamically chooses actions, often by calling tools, observes the results and continues until a stopping condition is reached.

### How does an Agent work?

> The model receives the task and available tool definitions, decides whether an action is needed, requests a tool when necessary, the runtime validates and executes it, the result is added to state, and the model continues until it can finish.

### Agent vs Chain?

> A chain follows a predefined application workflow; an agent allows the model to dynamically select actions and iterate based on observations.

### Tool Calling vs Agent?

> Tool calling is the mechanism by which the model requests a tool; an agent is the broader loop that decides, executes, observes and potentially repeats those actions.

### What is ReAct?

> A reasoning-and-action pattern where the system alternates between deciding what to do, taking an action, observing the result and deciding the next step.

### How do you prevent an agent from running forever?

> Bound model/tool calls and execution time, use timeouts and error handling, and define explicit stop conditions. Sensitive workflows can also require human approval.

### Can an agent work without tools?

> Yes. If the model can answer directly, it can finish without calling a tool.

### Why use LangGraph for an agent?

> When the workflow requires explicit state, branching, loops, persistence, human interaction or more detailed control than a high-level agent abstraction provides.

### What is the role of the runtime?

> The runtime manages state, execution, tool invocation and control policies. The model provides the decision signal but does not directly execute side effects.

## Mental model

```text
                         AGENT
                           │
                 Model + Harness
                           │
                          State
                           ↓
                          LLM
                           ↓
                 What should happen next?
                     /             \
                  Answer           Tool
                     │               ↓
                    END       Validate/Auth/Policy
                                     ↓
                                   Execute
                                     ↓
                                  Result
                                     ↓
                                  State
                                     ↓
                                    LLM
                                     ↓
                              Another action?
                               /          \
                             YES           NO
                              ↓             ↓
                            LOOP           END
```

## Key takeaway

> **An Agent is a controlled decision loop around a model. The model decides the next action; the runtime provides tools, state and execution controls; tool results feed back into the model until the workflow finishes.**
