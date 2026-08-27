# Topic 9 — LLM Fundamentals: Tokens, Context, Temperature & Inference

**Status:** Complete

## Focus
Tokens, context windows, temperature, top-p, system/user messages, structured output, tool calling, inference, model selection, latency and cost.

## 1. What is an LLM?

### Simple definition

> **An LLM (Large Language Model) is an AI model trained on large amounts of text that can understand and generate text. It generates a response by predicting what token should come next based on the input and the context.**

### Simple example

If we give:

```text
The capital of France is
```

the model predicts something like:

```text
Paris
```

For an AI application:

```text
User question
      ↓
     LLM
      ↓
Generated answer
```

For RAG:

```text
User query
      ↓
Retrieve relevant chunks
      ↓
Query + context
      ↓
     LLM
      ↓
Final answer
```

The LLM is the **generation layer**; retrieval supplies external knowledge/context.

## 2. Tokens

A token is a unit produced by the model's tokenizer. A token can be a whole word, part of a word, punctuation, or another text fragment.

```text
Text
 ↓
Tokenizer
 ↓
Tokens
 ↓
LLM
 ↓
Next-token prediction
```

Tokens matter because they affect:

- context-window limits
- input/output cost
- latency
- prompt size

## 3. Context window

The context window is the amount of tokenized input/output a model can handle for a request, subject to that model's limits.

A RAG request may contain:

```text
System instructions
+
Conversation history
+
User query
+
Retrieved chunks
+
Tool results
+
Expected output
```

### Interview point

A large context window does not mean we should send the entire knowledge base. More irrelevant context can increase cost/latency and reduce the signal-to-noise ratio.

## 4. Temperature

Temperature controls the randomness/variability of token sampling.

```text
Low temperature
→ more predictable / deterministic behavior

Higher temperature
→ more variation in generated output
```

Use cases:

- extraction / structured workflows → usually lower temperature
- creative generation → potentially higher temperature

### Interview question

**Does temperature make the model more intelligent?**

> No. Temperature changes sampling behavior; it does not increase the model's underlying capability.

## 5. Top-P

Top-P limits token selection to a set of candidates whose cumulative probability reaches a chosen threshold.

Mental model:

```text
Temperature
→ changes randomness

Top-P
→ limits the probability mass considered during sampling
```

For production systems, avoid changing multiple sampling parameters without an evaluation reason.

## 6. System vs user message

```text
System
→ defines behavior/instructions/context

User
→ provides the task/request
```

Example:

```text
System: You are an accounting assistant.
User: What was EBITDA in 2025?
```

## 7. Structured output

Production applications often need predictable data rather than free-form text.

Example:

```python
class Answer(BaseModel):
    answer: str
    citations: list[str]
    confidence: float
```

Mental model:

```text
LLM
 ↓
structured output
 ↓
Pydantic validation
 ↓
application object
```

This connects Topic 9 to Topic 3.

## 8. Tool / function calling

An LLM can be given tools such as:

```text
search_documents()
get_customer()
calculate_tax()
send_email()
```

The model can request a tool call, while the application executes the actual operation and returns the result to the model.

```text
User
 ↓
LLM
 ↓
tool decision
 ↓
application executes tool
 ↓
tool result
 ↓
LLM
 ↓
final answer
```

Important distinction: the model chooses/request tools; your application controls and executes the actual side effect.

## 9. Inference

Inference is the process of using a trained model to generate predictions/output for a new input.

Simple example:

```text
trained model
     ↓
new prompt
     ↓
inference
     ↓
response
```

## 10. Model selection

Do not automatically choose the largest model.

Consider:

- response quality
- latency
- cost
- context requirements
- structured-output/tool support
- throughput
- privacy/security requirements

Typical thinking:

```text
Simple classification
→ smaller/cheaper model may be enough

Complex reasoning
→ stronger model may be justified

Embeddings
→ embedding model

Reranking
→ reranker/cross-encoder
```

## 11. LLM latency

End-to-end latency can include:

```text
Request
 ↓
Retrieval
 ↓
Reranking
 ↓
Prompt construction
 ↓
LLM time-to-first-token
 ↓
Token generation
 ↓
Response
```

Streaming improves perceived responsiveness by showing generated output incrementally instead of waiting for the entire response.

## 12. LLM cost

Token usage directly affects model/API cost, depending on the provider/model.

Project connection: our AI Knowledge Assistant reduced token consumption using context compression and semantic caching. This is an example of optimizing the application around the model rather than only changing models.

## 13. RAG + LLM mental model

```text
User Query
    ↓
Retrieval
    ↓
Relevant chunks
    ↓
Prompt / context construction
    ↓
LLM
    ↓
Answer
```

The LLM should not be treated as the knowledge store. In RAG, retrieved context is supplied to ground generation.

## Likely interview questions

### What is an LLM?

> An LLM is an AI model trained on large amounts of text that can understand and generate text. At a high level, it generates output by predicting the next token based on the input context.

### What is a token?

> A token is a unit produced by the model tokenizer. Tokens affect context limits, cost and latency.

### What is a context window?

> The amount of tokenized input/output a model can handle for a request within its model-specific limit.

### What is temperature?

> A sampling parameter that controls the randomness/variability of generation.

### What is Top-P?

> A sampling parameter that restricts candidate tokens based on cumulative probability mass.

### Temperature vs Top-P?

> They both affect sampling, but temperature changes the distribution's sharpness/randomness while Top-P limits the candidate probability mass. I would tune them deliberately and validate changes rather than changing both blindly.

### Why structured output?

> To make model output predictable and machine-consumable, with schema validation at the application boundary.

### What is tool calling?

> The model requests a defined function/tool and the application executes it, controls the side effect, and returns the result.

### Why not always use the biggest model?

> Model choice is an engineering trade-off across quality, latency, cost, context requirements, throughput and operational constraints.

### How does an LLM fit into a RAG pipeline?

> It is the generation layer. Retrieval and optional reranking first provide relevant context, then the LLM generates the final grounded response from the query plus that context.

## Interview feedback / revision priority

These are high-value concepts because they connect directly to the RAG and LLM discussions expected in an AI engineering interview:

- [x] simple LLM definition
- [x] tokens
- [x] context window
- [x] temperature
- [x] top-p
- [x] system vs user messages
- [x] structured output
- [x] tool/function calling
- [x] inference
- [x] model selection
- [x] latency
- [x] cost
