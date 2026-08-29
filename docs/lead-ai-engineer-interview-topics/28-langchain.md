# Topic 28 — LangChain

**Status:** In Progress

## Focus
LangChain's current Python concepts relevant to the interview: model interfaces, tools, structured output, prompts, retrieval integrations, agents, tool calling, callbacks/tracing, and how LangChain relates to LangGraph and LangSmith.

## Interview outcomes
Explain when LangChain is useful, what abstractions it provides, where a custom implementation may be preferable, and how it can fit into the existing AI Platform/RAG architecture.

## Project connection
Map LangChain concepts to the abstractions already present in `ai-platform`: model/provider interfaces, retrieval, reranking, tool boundaries and structured application models. Do not claim production LangChain experience where none exists; explain the concepts and how they could be integrated.

## Current ecosystem note
LangChain is the higher-level agent framework with model/tool integrations and prebuilt agent architecture. Its current agents are built on LangGraph. LangSmith provides tracing and evaluation across these frameworks.

---

# 1. What is LangChain?

## Simple definition

LangChain is a framework/ecosystem for building applications around LLMs. It provides standardized abstractions and integrations for models, prompts, messages, structured output, tools, retrieval, agents, and related orchestration concerns.

## What problem does it solve?

Without a framework, an application may need to write and maintain its own glue code around:

- model-provider SDKs
- prompt construction
- message handling
- structured output parsing
- tool definitions and tool execution
- retrieval integrations
- agent/tool-calling loops
- tracing and callbacks

LangChain provides reusable abstractions for these concerns and makes components more composable.

## What LangChain is NOT

LangChain is not an LLM and does not replace model providers such as OpenAI, Anthropic, Google, or others. It sits at the application/framework layer above model providers.

```text
Your application
       ↓
   LangChain
       ↓
 Model provider
       ↓
      LLM
```

## Is LangChain only for agents?

No. It can be used for simple model invocation, prompt pipelines, structured output, retrieval/RAG, tool calling, and agents.

## Chain vs Agent

### Chain

A chain represents a predefined sequence of operations.

```text
Input → Prompt → LLM → Parser → Output
```

The application defines the execution flow.

### Agent

An agent can dynamically decide what action/tool to take based on the current task and model output.

```text
User → LLM → Tool A
          ↘ Tool B
          ↘ Tool C
             ↓
            LLM
             ↓
          Answer
```

Interview mental model:

> Chain = predefined flow.
>
> Agent = dynamically selected actions.

## LangChain vs LangGraph

LangChain provides higher-level abstractions for LLM applications such as models, prompts, tools, structured output, retrieval and agents.

LangGraph focuses on explicit stateful workflow orchestration, especially for complex agent workflows involving branching, loops, persistence, and human-in-the-loop.

A useful mental model:

```text
LangChain
  ├── Models
  ├── Prompts
  ├── Messages
  ├── Tools
  ├── Structured output
  ├── Retrievers
  └── Agent abstractions

LangGraph
  ├── State
  ├── Nodes
  ├── Edges
  ├── Conditional routing
  ├── Cycles
  ├── Persistence/checkpoints
  └── Human-in-the-loop
```

## When should you NOT use LangChain?

Do not introduce it automatically. A small application may be simpler with the provider SDK directly or with lightweight internal abstractions. A custom implementation can be preferable when the workflow is small, performance-sensitive, already has clean abstractions, or the team wants to minimize framework coupling.

Lead-level decision criteria:

- application complexity
- required integrations
- composability/reuse
- observability needs
- framework coupling
- performance/control requirements
- team familiarity and maintainability

## Interview answer

> LangChain is a framework and ecosystem for building LLM-powered applications. It provides abstractions and integrations for models, prompts, messages, structured output, tools, retrieval and agents, reducing the amount of custom integration and orchestration code we need to maintain. I would still evaluate whether it adds enough value for the application's complexity rather than adopting it by default.

## Experience positioning

Do not claim production LangChain experience unless it is true.

A strong honest answer is:

> My current AI platform uses custom abstractions for model providers, retrieval, reranking and tool boundaries. I understand LangChain's abstractions and how they map to those concerns, but I distinguish that from having operated LangChain in production.

---

# 2. Model Interfaces

## LLM vs Chat Model

The terminology is important because modern LangChain applications commonly use chat models.

### Traditional LLM / text-completion model

Conceptually:

```text
text prompt → text completion
```

Input and output are primarily plain text.

### Chat Model

A chat model accepts a sequence of messages and returns a message, typically an `AIMessage` in LangChain.

```text
messages → AIMessage
```

This message-oriented interface naturally supports conversation history, system instructions, tool calls, metadata, and multimodal content where the underlying provider supports it.

LangChain's current Python docs explicitly describe chat models as models that take a sequence of messages as input and return messages as output.

## Model provider vs model

These are different concepts:

```text
Provider
  ↓
OpenAI
Anthropic
Google
AWS
...
  ↓
Model
  ↓
Specific model identifier
```

For example, `OpenAI` is the provider while a specific GPT model is the model selected from that provider.

LangChain provides a standardized model interface across supported providers, allowing application-level code to be less tightly coupled to one provider.

## Common LangChain message types

### SystemMessage

Defines system-level instructions/context.

Example purpose:

> You are a financial policy assistant.

### HumanMessage

Represents user input.

### AIMessage

Represents a model response. It can contain generated content and, where supported, tool calls and response metadata.

### ToolMessage

Represents the result returned by a tool execution back to the model.

A common tool-calling sequence therefore looks like:

```text
HumanMessage
      ↓
   Chat Model
      ↓
   AIMessage
   + tool call
      ↓
   Tool execution
      ↓
  ToolMessage
      ↓
   Chat Model
      ↓
  final AIMessage
```

## Why messages instead of plain strings?

Messages provide structure around the model interaction. They carry role/type, content, and metadata, and can represent more than simple text.

They are especially useful for:

- multi-turn conversations
- system instructions
- tool calling
- multimodal content
- response metadata
- usage information
- preserving the interaction history

## `invoke()` mental model

A chat model can be invoked with either a single text input or a sequence of messages.

```python
response = model.invoke("Explain RAG")
```

or conceptually:

```python
messages = [
    SystemMessage("You are a helpful assistant."),
    HumanMessage("Explain RAG.")
]

response = model.invoke(messages)
```

The important interview distinction is that the second form makes the conversation structure explicit.

## Streaming and batching

Current LangChain model interfaces commonly expose operations such as:

- `invoke()` — generate one complete result
- `stream()` — receive output incrementally
- `batch()` — process multiple inputs

These are interface-level operations; provider-specific APIs may have their own batching or streaming mechanisms underneath.

## Interview questions

### Q1. What is the difference between an LLM and a chat model?

**Strong answer:**

> A traditional text-completion LLM is usually modeled as text-in/text-out, while a chat model works with structured messages and returns message objects. Chat models fit naturally with system/user/assistant roles, conversation history and tool-calling workflows.

### Q2. Why does LangChain use messages?

**Strong answer:**

> Messages provide a standard structured representation of model interactions. They capture the message type or role, content and metadata, and they allow LangChain to represent conversations, tool calls and multimodal content consistently across providers.

### Q3. What are `SystemMessage`, `HumanMessage`, `AIMessage`, and `ToolMessage`?

**Answer:**

- `SystemMessage` — system-level instruction/context.
- `HumanMessage` — user input.
- `AIMessage` — model-generated response, potentially including tool calls and metadata.
- `ToolMessage` — tool execution result returned to the model.

### Q4. Why is a standardized model interface useful?

**Strong answer:**

> It reduces provider coupling. Application code can use a common model interface while the provider-specific integration handles differences in the underlying APIs. This makes provider comparison or migration easier, although provider capabilities are not necessarily identical.

### Q5. Does a common LangChain model interface mean every provider behaves identically?

**No.**

The interface can be standardized while capabilities and semantics still vary by provider/model. For example, support for tools, structured output, multimodality, context limits, reasoning features, and streaming details can differ.

### Q6. How does tool calling appear in the message flow?

**Strong answer:**

> The model returns an AI message containing a tool call request. The application or agent runtime executes the requested tool and sends the result back as a tool message. The model can then use that tool result to produce the next response or request another tool.

### Q7. When would you invoke a model directly instead of using an agent?

**Answer:**

> When the task has a known execution flow, such as classification, extraction, summarization or a simple RAG response. An agent is more appropriate when the model needs to dynamically decide which tools or actions to use.

## Common interview trap

Do not say:

> LangChain provides one universal model with the same capabilities everywhere.

Better:

> LangChain provides a common application interface across providers, while actual model capabilities remain provider/model specific.

---

# Key takeaways so far

```text
LangChain
  = LLM application framework/ecosystem

LangChain ≠ LLM
  = it sits above model providers

Chat Model
  = message-in / message-out model interface

Messages
  = structured units of model context and interaction

Chain
  = predefined execution flow

Agent
  = dynamic action/tool selection

LangGraph
  = stateful workflow/agent orchestration
```

## Sources

- LangChain Models: https://docs.langchain.com/oss/python/langchain/models
- LangChain Messages: https://docs.langchain.com/oss/python/langchain/messages
- LangChain Chat Model integrations: https://docs.langchain.com/oss/python/integrations/chat
- LangChain Providers and Models: https://docs.langchain.com/oss/python/concepts/providers-and-models
