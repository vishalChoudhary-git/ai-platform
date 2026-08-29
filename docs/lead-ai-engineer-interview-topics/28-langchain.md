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

## Ingestion vs Retrieval: where does LangChain fit?

LangChain can support **both document ingestion and retrieval/RAG**.

### Ingestion

LangChain provides components commonly used for ingestion workflows, such as document loaders, text splitters, embeddings integrations and vector-store integrations.

```text
Source document
      ↓
Document Loader
      ↓
Document objects
      ↓
Text splitting
      ↓
Embeddings
      ↓
Vector store
```

### Retrieval / RAG

LangChain also provides abstractions for retrieval and composing retrieval with prompts and models.

```text
User query
     ↓
Retriever
     ↓
Relevant documents
     ↓
Prompt
     ↓
Chat model
     ↓
Answer
```

### Interview positioning

LangChain is **not limited to retrieval**, and it is **not required to own ingestion**. In production systems, document ingestion is often implemented as a dedicated pipeline/service, while LangChain may be used more heavily in retrieval/RAG and agent/application orchestration.

For a platform architecture, keep ingestion and application orchestration as separate concerns unless there is a clear reason to couple them.

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

# 3. Prompt Templates

## Prompt

A prompt is the actual instruction/input given to a model.

```text
Explain Retrieval-Augmented Generation in simple terms.
```

## Prompt Template

A reusable prompt pattern with runtime variables.

```text
You are an expert {role}.
Explain {topic} for the given audience.
```

Mental model:

```text
Prompt Template
      ↓
Fill runtime variables
      ↓
Final prompt
      ↓
Model
```

## PromptTemplate vs f-string

Both can perform variable substitution. An f-string is sufficient for simple interpolation. `PromptTemplate` provides a framework-level abstraction that integrates with LangChain composition and makes inputs explicit and reusable.

Do not claim that PromptTemplate is required for variables; it is mainly valuable for standardization and composition.

## PromptTemplate vs ChatPromptTemplate

### PromptTemplate

Generally text-oriented.

```text
PromptTemplate
      ↓
formatted text
```

### ChatPromptTemplate

Builds structured chat messages for a chat model.

```text
ChatPromptTemplate
      ↓
SystemMessage
HumanMessage
...
      ↓
Chat Model
```

## Variables

Prompts commonly contain runtime values such as:

- user question
- retrieved context
- role/domain
- conversation information
- formatting instructions

Example:

```text
Use the following context to answer the question.

Context:
{context}

Question:
{question}
```

## Message placeholders

A message placeholder provides a location where a list of messages, such as conversation history, can be inserted into a chat prompt.

```text
System instructions
      ↓
Message placeholder ← conversation history
      ↓
Current human message
```

## Few-shot prompting

Few-shot prompting provides examples in the prompt to demonstrate the desired behavior/output.

```text
Instruction
  +
Example 1
Example 2
  +
New input
  ↓
LLM
```

## Prompt composition

Larger prompts can be assembled from reusable components:

```text
System instructions
        +
Few-shot examples
        +
Conversation history
        +
Retrieved context
        +
User question
        ↓
Final chat prompt
```

## Prompt templates in RAG

```text
Question
   ↓
Retriever
   ↓
Retrieved context
   ↓
ChatPromptTemplate
   ↓
Chat Model
   ↓
Answer
```

A prompt template does not make the model more intelligent; it provides structured, reusable prompt construction.

## Production prompt management

A production prompt should be treated as an application artifact that may need:

- versioning
- testing
- evaluation
- observability
- rollback

## Interview questions

### Q1. What is a PromptTemplate?

> A reusable prompt definition containing variables that are populated at runtime. It standardizes prompt construction and composes naturally with other LangChain components.

### Q2. PromptTemplate vs f-string?

> Both can substitute variables. F-strings are fine for simple cases; PromptTemplate provides a framework-level abstraction that integrates with LangChain pipelines and makes prompt inputs explicit and reusable.

### Q3. PromptTemplate vs ChatPromptTemplate?

> PromptTemplate is generally text-oriented, while ChatPromptTemplate constructs structured chat messages such as system and human messages for a chat model.

### Q4. What is a message placeholder?

> A location in a chat prompt where a list of messages, commonly conversation history, can be inserted.

### Q5. What is few-shot prompting?

> Providing a small number of examples in the prompt so the model can infer the desired behavior or output format for a new input.

### Q6. How is PromptTemplate used in RAG?

> Retrieved chunks and the user's question can be passed as variables into a reusable prompt template, which is then sent to the model.

---

# 4. Structured Output

## Definition

Structured output means obtaining model responses that conform to a predefined schema instead of relying on free-form text.

```text
User input
   ↓
LLM
   ↓
Structured response
   ↓
Schema / validation
   ↓
Application object
```

## Why structured output?

LLMs naturally produce text, while application code often needs typed data.

```text
Free-form:
"The expense was ₹4,500 for accommodation."

Structured:
{
  "merchant": "Taj Hotels",
  "amount": 4500,
  "category": "accommodation"
}
```

Structured output creates a stronger interface between probabilistic model output and deterministic application logic.

## Structured output vs JSON

JSON is a data format. Structured output is the broader requirement that the response conform to a predefined structure/schema. The resulting data may be represented as JSON or a typed object.

## Pydantic

Pydantic is useful for defining typed schemas and performing runtime validation.

```python
class Expense(BaseModel):
    merchant: str
    amount: float
    category: str
```

Mental model:

```text
Pydantic schema
      ↓
Model structured response
      ↓
Validation
      ↓
Application object
```

## Structured output vs Output Parser

An output parser processes model output after generation and converts/validates it. Provider/model-supported structured output can formalize or constrain the response according to a schema, reducing reliance on manual parsing.

Do not claim structured output guarantees semantic correctness.

## Structured output vs Tool Calling

```text
Structured output
→ return structured information

Tool calling
→ request execution of an external action/tool
```

Both can use schemas, but their purposes differ.

## Structured output in agents

An agent can return a typed decision object:

```python
class AgentDecision(BaseModel):
    decision: Literal["approved", "information_required"]
    reason: str
```

The backend can then use the decision as a deterministic application input.

## Schema correctness vs business correctness

A schema validates the shape/type of data, not whether the underlying information is correct.

```text
Schema validation
→ "Is the data shaped correctly?"

Business validation
→ "Does this make sense for the domain?"
```

Both may be required in production.

## Interview questions

### Q1. What is structured output?

> A mechanism for obtaining model responses that conform to a predefined schema instead of relying on free-form text.

### Q2. Why use Pydantic with LLMs?

> To define typed schemas and validate model-generated data before passing it into deterministic application logic.

### Q3. Structured output vs JSON?

> JSON is a data format, while structured output is the requirement that model output conform to a defined schema, potentially represented as JSON or a typed object.

### Q4. Structured output vs output parser?

> An output parser processes model output after generation, while provider-supported structured output can formalize or constrain the response according to a schema.

### Q5. Does structured output guarantee correctness?

> No. It helps with structural correctness; semantic and business correctness still require validation and domain safeguards.

### Q6. Structured output vs tool calling?

> Structured output returns data in a defined schema; tool calling lets the model request an external action using structured arguments.

---

# 5. Runnables

## What is a Runnable?

A Runnable is a LangChain abstraction representing an executable and composable unit.

Mental model:

```text
Input
  ↓
Runnable
  ↓
Output
```

Prompt templates, models, parsers, retrievers, and custom logic can participate in the Runnable model.

## Why Runnables exist

They provide a common execution/composition model instead of every component having unrelated orchestration APIs.

```text
Runnable A
    ↓
Runnable B
    ↓
Runnable C
```

## Pipe composition

```python
chain = prompt | model | parser
```

Conceptually:

```text
input
  ↓
prompt
  ↓
model
  ↓
parser
  ↓
output
```

The `|` operator composes compatible runnables; it does not execute the pipeline immediately. Execution happens when the resulting runnable is invoked/streamed/batched.

## Common execution operations

- `invoke()` — one input, one result
- `stream()` — incremental output
- `batch()` — multiple inputs

## RunnableSequence

A sequence composes runnables in order:

```text
A → B → C
```

For example:

```python
prompt | model | parser
```

## RunnableParallel

Parallel composition allows multiple branches to work from the same input.

```text
       ┌→ A ─┐
Input ─┤     ├→ combined result
       └→ B ─┘
```

Useful for independent operations such as multiple lookups or independent transformations.

## RunnablePassthrough

Passes its input through unchanged. This is useful when preserving the original input while deriving additional values.

Conceptually:

```text
Question
  ├────────→ original question
  └→ Retriever → context
```

## RunnableLambda

Wraps custom Python logic so it can participate in the Runnable composition model.

```python
def clean_context(value):
    return value.strip()

cleaner = RunnableLambda(clean_context)
```

Use this for custom logic when an existing LangChain component does not already provide the behavior you need.

## Built-in implementations vs RunnableLambda

LangChain provides many Runnable-compatible implementations; applications do not need to use `RunnableLambda` for every pipeline step.

Examples:

```text
Prompt
  → ChatPromptTemplate

Model
  → provider integration such as a chat model class

Parser
  → built-in output parser implementations

Custom application logic
  → RunnableLambda when needed
```

This means the typical model is:

```text
LangChain components
        +
Provider integrations
        +
Your custom Runnable logic
        ↓
Composed pipeline
```

## Runnable vs Agent

A Runnable is an execution/composition abstraction.

An Agent is a decision-making system that can dynamically choose actions or tools.

Mental model:

```text
Runnable
→ How is this component executed?

Agent
→ What should I do next?
```

## Runnable vs Chain

Historically, LangChain exposed many specialized Chain classes. Modern LangChain emphasizes the Runnable interface for general composition.

Useful mental model:

```text
Runnable
= fundamental execution/composition abstraction

Chain
= workflow/pipeline concept
```

## Interview questions

### Q1. What is a Runnable?

> A Runnable is a LangChain abstraction for an executable and composable unit, with a common execution model such as invoke, stream, and batch.

### Q2. What does `prompt | model | parser` mean?

> It composes Runnable-compatible components into a sequential pipeline where each stage's output feeds the next stage's input.

### Q3. What is RunnableSequence?

> A sequential composition of Runnable components.

### Q4. What is RunnableParallel?

> A composition that lets multiple runnable branches operate from the same input and return a combined result.

### Q5. What is RunnablePassthrough?

> A runnable that passes its input through unchanged, useful for preserving original inputs while generating additional values.

### Q6. What is RunnableLambda?

> A way to wrap custom Python logic so that it participates in LangChain's Runnable composition model.

### Q7. Why isn't RunnableLambda used for every step?

> Because LangChain already provides many Runnable-compatible components for prompts, models, parsers, retrievers and other operations. RunnableLambda is mainly useful when custom application logic is needed.

### Q8. What happens when you write `prompt | model | parser`?

> The components are composed into a sequential runnable pipeline. The composition itself does not perform execution; invoking the resulting runnable performs the work.

---

# 6. Chains

## Definition

A Chain is a workflow that connects multiple processing steps into a single application flow.

```text
Input
  ↓
Step A
  ↓
Step B
  ↓
Step C
  ↓
Output
```

Example:

```text
Question
  ↓
Prompt
  ↓
LLM
  ↓
Parser
  ↓
Answer
```

## Why chains are useful

A chain lets an application treat several connected operations as one workflow.

Instead of manually executing:

```python
prompt_result = prompt.invoke(data)
model_result = model.invoke(prompt_result)
final_result = parser.invoke(model_result)
```

we can compose:

```python
chain = prompt | model | parser
final_result = chain.invoke(data)
```

## Historical Chain classes

Older LangChain code commonly used specialized chain classes for predefined workflows, such as:

- `LLMChain`
- `SequentialChain`
- `RetrievalQA`

These are useful to recognize when reading existing code and understanding LangChain's evolution.

## Modern Runnable composition

Modern LangChain emphasizes Runnables as the common composition/execution abstraction.

So rather than thinking:

```text
Everything must be a Chain class
```

think:

```text
Runnable components
      ↓
compose them into a workflow
      ↓
chain/pipeline
```

## Specialized Chain classes vs Runnables

Interview mental model:

```text
Specialized Chain class
→ often encapsulates a common/predefined workflow

Runnable composition
→ gives more granular building blocks so the developer can explicitly compose the pipeline
```

Important nuance:

Do not claim that Chain classes cannot be customized, or that Runnables automatically provide dynamic routing. Complex dynamic branching, cycles and stateful orchestration are better modeled with LangGraph.

A stronger statement is:

> Historically, LangChain provided specialized Chain classes that encapsulated common workflows. Runnable composition provides more granular building blocks for explicitly constructing and customizing pipelines. For complex dynamic routing, branching, loops and persistent state, LangGraph is the more appropriate abstraction.

## Chain vs Agent

### Chain

```text
A → B → C → D
```

The application largely determines the workflow.

### Agent

```text
            ┌→ Tool A
User → LLM ─┼→ Tool B
            └→ Tool C
                 ↓
                LLM
                 ↓
              Answer
```

The model can dynamically decide which tool/action to take.

## Chain vs LangGraph

Simple predefined flow:

```text
A → B → C → D
```

Stateful graph:

```text
       A
       ↓
       B
      / \
     C   D
     ↓   ↓
     └→ B
```

LangGraph is designed for explicit state, branching, loops, persistence, interrupts and human-in-the-loop workflows.

## Chain vs RunnableSequence

`RunnableSequence` is a specific sequential Runnable composition. "Chain" is the broader workflow concept and historical LangChain terminology.

## Chain is not limited to LLM calls

A chain/workflow can connect prompts, models, retrievers, parsers and custom logic as long as the components can participate in the required composition interface.

## RAG chain mental model

```text
Question
   ↓
Retriever
   ↓
Documents
   ↓
Prompt
   ↓
Chat Model
   ↓
Answer
```

## Interview questions

### Q1. What is a Chain?

> A Chain is a composed application workflow in which multiple processing steps are connected so outputs from earlier stages feed later stages.

### Q2. Chain vs Runnable?

> Runnable is the standardized execution/composition abstraction in modern LangChain, while Chain is the broader workflow concept. Modern chain-like pipelines are commonly expressed as Runnable compositions.

### Q3. What does `prompt | model | parser` represent?

> A sequential composition of Runnable-compatible components.

### Q4. Chain vs Agent?

> A chain generally follows a predefined workflow, while an agent can dynamically decide which tools or actions to take.

### Q5. Chain vs LangGraph?

> Chains are a good fit for relatively straightforward predefined flows. LangGraph is better for explicit stateful workflows with branching, loops, persistence and human-in-the-loop requirements.

### Q6. Are Chain classes unable to customize their flow?

> No. The key distinction is that specialized Chain classes often encapsulate common workflows, while Runnable composition gives more granular control over how components are composed. Dynamic routing and cycles are a separate concern where LangGraph becomes useful.

### Q7. What happens when you compose a chain with `|`?

> You create a Runnable-based composition. Execution occurs when the resulting object is invoked, streamed or batched.

---

# Key takeaways

```text
LangChain
  = LLM application framework/ecosystem

Model Interface
  = standardized way to interact with model providers

Chat Model
  = message-in / message-out model interface

Prompt Template
  = reusable parameterized prompt construction

Structured Output
  = schema-conforming model response

Runnable
  = executable/composable LangChain unit

Chain
  = composed workflow/pipeline

Agent
  = dynamic decision-making/tool selection

LangGraph
  = stateful workflow/agent orchestration
```

## Sources

- LangChain Models: https://docs.langchain.com/oss/python/langchain/models
- LangChain Messages: https://docs.langchain.com/oss/python/langchain/messages
- LangChain Chat Model integrations: https://docs.langchain.com/oss/python/integrations/chat
- LangChain Providers and Models: https://docs.langchain.com/oss/python/concepts/providers-and-models
