# Topic 30 — LangChain Tools

**Status:** In Progress

## Focus
LangChain Tool concepts for interviews: tool abstraction, tool metadata, input schemas, tool vs function/API/Runnable, read-only vs mutating tools, tool security, `@tool`, and the separation between tool definition, tool calling and tool execution.

## Interview outcomes
Explain what a Tool is, why an LLM needs tools, how a tool is described to a model, who actually executes a tool, and how to design secure production tools.

## Project connection
Map the concepts to the existing AI Platform tool boundaries without claiming production LangChain usage. The Expense Agent already has read-only capabilities such as expense lookup, evidence lookup, policy lookup and policy search; these are useful examples for discussing tool design and security.

---

# 1. What is a Tool?

A **Tool** is a model-facing callable capability that allows an LLM or agent to request access to external information or an application capability.

```text
LLM
 ↓
Tool request
 ↓
Application/runtime
 ↓
Tool implementation
 ↓
Result
 ↓
LLM
```

Examples:

- database lookup
- REST/API call
- Python function
- internal service
- search operation
- file retrieval

### Interview definition

> A Tool is a model-facing interface to an application capability. The model can request the capability, while the application/runtime is responsible for validation and execution.

---

# 2. Why do we need Tools?

An LLM by itself should not be treated as having direct access to application systems.

Instead, application capabilities are exposed explicitly:

```text
                 LLM
                  │
       ┌──────────┼──────────┐
       ↓          ↓          ↓
  get_expense  search_policy  get_employee
       │          │          │
       ↓          ↓          ↓
   Database     Search API   Internal API
```

This gives the system a controlled boundary between model reasoning and real-world actions/data.

---

# 3. Where does a Tool method such as `get_expense()` live?

A Tool should generally **not be confused with a Controller**. The Tool is the model-facing interface; the actual business logic should remain in the application's normal service/domain layers.

A clean backend-style layout is:

```text
LLM / Agent
    ↓
Tool Adapter / Tool Definition
    ↓
Service Layer
    ↓
Repository / External Client
    ↓
Database / External System
```

Example:

```text
get_expense Tool
      ↓
ExpenseService.get_expense()
      ↓
ExpenseRepository.get_by_id()
      ↓
PostgreSQL
```

### Where does the Controller fit?

A Controller is normally an **HTTP/API entry point for external callers**:

```text
HTTP Request
    ↓
Controller / Route
    ↓
Service
    ↓
Repository
```

A model-generated tool call does not have to pass through an HTTP Controller inside the same application. The Tool execution layer can call the service layer directly.

If the capability belongs to another microservice, the Tool can call that service's API instead:

```text
LLM
 ↓
Tool
 ↓
Internal HTTP Client
 ↓
Other service Controller/API
 ↓
Service
 ↓
Repository
```

### Key principle

> **Tool is an adapter at the LLM boundary; Service owns business logic; Repository/clients own data or infrastructure access.**

This keeps the AI-facing interface separate from core business logic and avoids putting business rules directly inside the tool wrapper.

---

# 4. Tool vs Function

A normal Python function is implementation logic:

```python
def get_expense(expense_id: int):
    ...
```

A Tool exposes that capability to the model with additional model-facing metadata.

```text
Python Function
      ↓
Tool abstraction
      ├── name
      ├── description
      ├── input schema
      └── callable implementation
```

### Mental model

> Function = implementation.
>
> Tool = model-facing capability around that implementation.

A function does not automatically become a useful model-facing tool merely because it is callable.

---

# 5. Tool metadata

A useful tool generally exposes:

```text
Name
Description
Input schema
Execution implementation
```

Example:

```text
Name:
get_expense

Description:
Retrieve an expense by expense ID, including amount,
merchant, status and submission date.

Input:
expense_id: integer
```

The **description matters** because the model uses the available tool information to decide whether a tool is relevant to the current task.

---

# 6. Tool input schema

The schema defines what arguments the tool accepts.

Conceptually:

```json
{
  "type": "object",
  "properties": {
    "expense_id": {
      "type": "integer"
    }
  },
  "required": ["expense_id"]
}
```

The LLM does not execute the Python function directly. It produces a structured request that identifies the tool and supplies arguments matching the declared contract.

---

# 7. `@tool`

LangChain provides a convenient way to expose a Python function as a tool.

Conceptually:

```python
from langchain_core.tools import tool

@tool
def get_expense(expense_id: int):
    """Retrieve an expense by ID."""
    return ...
```

LangChain can use the function's name, description/docstring and type information to build the model-facing tool definition.

The exact generated schema depends on the function signature and supported features.

---

# 8. Tool vs API

These are not the same concept.

```text
API
→ programmatic interface exposed by a service

Tool
→ model-facing capability exposed to an LLM/agent
```

A Tool may internally call:

```text
REST API
GraphQL API
Database
Python function
Redis
Internal microservice
External service
```

Therefore:

> A Tool may be implemented using an API, but a Tool is not synonymous with an API.

---

# 9. Tool vs Runnable

```text
Runnable
→ standardized execution/composition abstraction

Tool
→ model-facing capability/interface
```

The concepts can overlap in implementation, but they answer different questions:

- Runnable: **How can this unit participate in execution/composition?**
- Tool: **What capability can the model request?**

---

# 10. Tool vs Agent

```text
Tool
= capability

Agent
= decision maker/orchestrator
```

Example:

```text
Agent
 ↓
"I need policy information"
 ↓
search_policy Tool
 ↓
Tool result
 ↓
Agent
```

The agent decides which tool to request. The tool performs the capability.

---

# 11. Read-only vs mutating Tools

This distinction is important in production systems.

### Read-only tools

```text
get_expense
get_policy
search_policy
get_evidence
```

These retrieve information without changing system state.

### Mutating tools

```text
approve_expense
update_expense
send_payment
update_policy
```

These change system state and therefore need stronger controls.

A useful architecture is:

```text
Model tool request
       ↓
Input validation
       ↓
Authentication / Authorization
       ↓
Business rules / policy
       ↓
Optional human approval
       ↓
Service
       ↓
Repository / external client
       ↓
Execution
```

---

# 12. The LLM does NOT execute the tool

This is one of the most important interview points.

Do not say:

> "The LLM calls my Python function."

More accurately:

> The LLM generates a structured tool-call request. The application or agent runtime validates and executes the corresponding tool and then returns the result to the model.

Mental model:

```text
LLM
 ↓
REQUEST
 ↓
Application/runtime
 ↓
EXECUTE
 ↓
RESULT
 ↓
LLM
```

---

# 13. Recommended end-to-end mental model for Tool Calling

This is the model to remember for interviews:

```text
                         USER
                           ↓
                         AGENT
                           ↓
                         LLM
                           ↓
              Needs external information/action?
                           ↓
                 Tool request / tool call
                           ↓
             Available tools + descriptions/schema
                           ↓
              Model selects appropriate capability
                           ↓
                 Tool execution boundary
                           ↓
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
     Validate           Authorize          Policy check
        └──────────────────┼──────────────────┘
                           ↓
                    Tool / Tool Adapter
                           ↓
                    Service Layer
                           ↓
              Repository / External Client
                           ↓
                  DB / External System
                           ↓
                       Result
                           ↓
                    ToolMessage
                           ↓
                         Agent
                           ↓
                         LLM
                           ↓
              Need another tool/action?
                    /              \
                  YES              NO
                   ↓                ↓
             another cycle      Final answer
```

### Important refinement

The model does not independently "search" some secret registry after the agent asks it for a tool. The **available tools and their descriptions/schemas are supplied to the model as part of the model interaction**, and the model selects an appropriate tool based on that information.

The runtime then performs the actual execution.

### Interview mental model

> **Agent needs information or an action → model chooses a tool from the available tool definitions → runtime receives the tool call → validates/authenticates/authorizes it → executes the Tool → Service → Repository/external system → result comes back as a ToolMessage → model decides whether it needs another tool or can produce the final answer.**

This is the preferred mental model for our interview preparation.

---

# 14. Tool security

The model should be treated as an **untrusted caller**.

Never rely on the LLM to enforce authorization.

For example:

```text
LLM requests:
delete_user(user_id=100)

        ↓
Tool boundary
        ↓
Authentication / authorization
        ↓
Input validation
        ↓
Business policy
        ↓
Optional approval
        ↓
Execute or reject
```

### Lead-level rule

> LLM intent is not authorization.

The tool implementation or the surrounding execution layer must enforce the application's actual security rules.

---

# 15. Tool design best practices

Good tools tend to be:

### Narrow

Prefer:

```text
get_expense
get_policy
search_policy
```

over a vague:

```text
do_everything(...)
```

### Well described

The model needs enough information to understand when the tool is appropriate.

### Strongly typed

Tool arguments should have explicit schemas/types.

### Permission-aware

Authorization should happen outside the model's reasoning.

### Safe

Expose the minimum capability required by the agent.

### Idempotent where possible

Especially useful for operations that may be retried or replayed.

---

# 16. Tool and structured output

Both can use schemas, but their purposes differ.

```text
Structured Output
→ produce structured application data

Tool Calling
→ request execution of a capability
```

Example structured output:

```json
{
  "decision": "approved",
  "reason": "Within policy"
}
```

Example tool request:

```json
{
  "name": "get_expense",
  "arguments": {
    "expense_id": 123
  }
}
```

---

# 17. Typical Tool interaction

```text
User
 ↓
Agent / Chat Model
 ↓
AI message containing tool request
 ↓
Tool runtime
 ↓
Tool implementation
 ↓
Tool result
 ↓
Tool message
 ↓
Chat Model
 ↓
Final answer or another tool request
```

The detailed protocol is covered separately in **Tool Calling**.

---

# Interview Questions

## Q1. What is a Tool in LangChain?

> A Tool is a model-facing callable capability that allows an LLM or agent to request information or an external/application action through a defined interface.

## Q2. Does the LLM execute a Tool?

> No. The LLM generates a structured request for a tool. The application or agent runtime validates and executes the tool, then returns the result to the model.

## Q3. Tool vs Function?

> A function is implementation logic. A Tool wraps or exposes that capability with model-facing metadata such as a name, description and input schema.

## Q4. Tool vs API?

> An API is a programmatic service interface. A Tool is a model-facing capability and may internally call an API, database, Python function or another service.

## Q5. Why is the tool description important?

> The model uses tool metadata to understand what the capability does and decide when the tool is relevant.

## Q6. Why is an input schema important?

> It defines the contract for tool arguments, improves reliability and validation, and tells the model what inputs the tool expects.

## Q7. Tool vs Runnable?

> Runnable is an execution/composition abstraction, while a Tool is primarily a model-facing capability interface.

## Q8. Tool vs Agent?

> A Tool provides a capability; an Agent decides which capabilities or actions to use.

## Q9. Where should tool business logic live?

> The Tool should act as the model-facing adapter. Business logic should remain in the service/domain layer, while repositories or clients handle persistence and infrastructure access. A Controller is only involved when the tool crosses an HTTP service boundary.

## Q10. Who validates a tool call?

> The application/runtime should validate the model-generated request before execution. That includes schema/type validation, authentication and authorization, and domain/business-policy checks. This is conceptually similar to validating an external API request: the model is an untrusted caller.

## Q11. How should mutating tools be handled?

> They should have stronger validation and authorization controls and may require approval or additional policy checks. The model should never be the source of authorization.

## Q12. How would you design tools for a production agent?

> I would keep them narrow and well described, use explicit input schemas, enforce authentication and authorization at the tool boundary, distinguish read-only from mutating operations, make retry behavior safe where possible, and expose only the minimum capabilities required by the agent.

---

# Key mental model

```text
                    AGENT / LLM
                         ↓
                   Tool request
                         ↓
                 ┌──────────────┐
                 │ Tool Runtime │
                 └──────┬───────┘
                        ↓
              Validation / Auth / Policy
                        ↓
                   Tool Adapter
                        ↓
                    Service
                        ↓
              Repository / API client
                        ↓
              Database / External System
                        ↓
                    Tool result
                        ↓
                   ToolMessage
                        ↓
                    AGENT / LLM
```

## Key takeaway

> **A Tool is a controlled, model-facing capability. The model decides to request it, but the application/runtime owns validation, authorization and execution.**
