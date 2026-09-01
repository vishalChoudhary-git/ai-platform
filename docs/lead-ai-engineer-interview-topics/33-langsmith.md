# LangChain Concept 13 — LangSmith

**Status:** Complete

## Definition

> **LangSmith is an observability and evaluation platform for LLM and agent applications. It helps developers trace executions, inspect runs, build evaluation datasets, compare experiments and monitor application behavior.**

Mental model:

```text
AI Application
      ↓
LangChain / LangGraph / model SDK
      ↓
Tracing / instrumentation
      ↓
LangSmith
      ↓
Traces + datasets + evaluations
```

## 1. Why LangSmith?

LLM applications are harder to debug than normal request/response APIs because the final answer hides the intermediate behavior.

For example:

```text
User question
 ↓
Agent
 ↓
Model call
 ↓
Tool call
 ↓
Retriever
 ↓
Reranker
 ↓
Model call
 ↓
Final answer
```

Without tracing, you may only see the final response. LangSmith helps expose the intermediate execution.

## 2. What is a Run?

A run represents one execution of an operation such as:

```text
chain invocation
model call
tool call
retriever call
agent step
```

A run can contain nested child runs.

```text
Agent Run
 ├── Model Run
 ├── Tool Run
 ├── Retriever Run
 └── Model Run
```

This makes complex execution inspectable.

## 3. Tracing

Tracing records the execution path and timing of a request.

For an agent:

```text
Trace
 ├── Agent start
 ├── Model call
 ├── Tool call
 ├── Tool result
 ├── Model call
 └── Final response
```

Useful information can include inputs/outputs, metadata, timing, token usage and errors, subject to the application's data-capture settings.

## 4. RAG debugging

A trace can help answer:

```text
Was the query correct?
Which documents were retrieved?
How many candidates were returned?
Did reranking change the order?
What context reached the model?
Which model was used?
How many tokens were consumed?
Where did the latency come from?
```

Mental model:

```text
Bad answer
   ↓
Open trace
   ↓
Check retrieval
   ↓
Check reranking
   ↓
Check context
   ↓
Check model call
   ↓
Locate root cause
```

## 5. Agent debugging

For agents, tracing is even more useful because execution is dynamic.

```text
User
 ↓
Agent
 ↓
LLM
 ↓
Tool A
 ↓
LLM
 ↓
Tool B
 ↓
LLM
 ↓
Final answer
```

The trace lets you see why the application spent time on multiple tool/model calls and where a loop or unexpected tool selection occurred.

## 6. Evaluation

Observability answers:

> What did the system do?

Evaluation answers:

> How good was the result?

LangSmith supports dataset-based evaluation workflows where a set of representative examples can be run against an application and evaluated.

```text
Evaluation Dataset
       ↓
Application version A ──→ results
Application version B ──→ results
       ↓
Compare quality
```

## 7. Dataset

A dataset is a collection of representative examples used for evaluation/testing.

For a RAG system, examples can contain:

```text
question
expected answer / reference
expected sources
metadata
```

The goal is to create a stable test set instead of judging every change from a few manual demos.

## 8. LLM-as-a-Judge

An evaluator model can score outputs according to a rubric.

Example:

```text
Input + model output + reference/evidence
                  ↓
              Judge LLM
                  ↓
              score/reason
```

Use cases include:

- response quality
- relevance
- faithfulness
- style or rubric compliance

LLM-as-a-judge itself can be imperfect, so use clear rubrics and validate important metrics against human judgment.

## 9. Offline evaluation

Run the application against a fixed dataset before deployment:

```text
Code / Prompt change
       ↓
Run evaluation dataset
       ↓
Quality metrics
       ↓
Regression check
       ↓
Deploy or reject
```

This is particularly valuable for prompt, model, retriever and reranker changes.

## 10. Online monitoring

After deployment, monitor live behavior:

```text
Production traffic
       ↓
Telemetry
       ↓
Latency / errors / cost
       ↓
quality signals / user feedback
```

Offline evaluation and online monitoring solve different problems and should complement each other.

## 11. Experiments and comparison

A useful workflow is:

```text
Baseline
   ↓
Change prompt/model/retriever
   ↓
Run same evaluation set
   ↓
Compare quality + latency + cost
```

This turns framework changes into measurable engineering experiments rather than subjective decisions.

## 12. LangSmith vs LangChain

```text
LangChain
→ build LLM applications
→ models / prompts / tools / retrieval / agents

LangSmith
→ inspect and evaluate those applications
→ traces / runs / datasets / evaluations
```

They are related products in the same ecosystem, but they solve different problems.

## 13. LangSmith vs LangGraph

```text
LangGraph
→ orchestrate stateful workflows

LangSmith
→ observe/evaluate workflows
```

A LangGraph execution can be traced in LangSmith.

## 14. LangSmith vs OpenTelemetry

```text
LangSmith
→ specialized LLM/agent observability + evaluation

OpenTelemetry
→ vendor-neutral general telemetry standard/ecosystem
```

An enterprise platform can use both.

Example:

```text
AI service
 ├── OpenTelemetry → central platform observability
 └── LangSmith     → LLM/agent traces + evaluations
```

## 15. What should be captured?

Useful telemetry includes:

```text
request / trace ID
model/provider
prompt/version identifier
tool names
retriever results or IDs
latency
TTFT
tokens
cost
errors
retries
fallbacks
feedback/evaluation scores
```

Avoid blindly capturing sensitive data. Apply redaction, access control and retention rules.

## 16. Prompt versioning

Treat prompts as versioned application artifacts.

```text
Prompt v1 → baseline
Prompt v2 → experiment
       ↓
Evaluation dataset
       ↓
Quality comparison
```

A prompt change should ideally be traceable to the application/model behavior it produced.

## 17. Production quality loop

A mature workflow looks like:

```text
Build
 ↓
Trace
 ↓
Evaluate
 ↓
Deploy
 ↓
Monitor
 ↓
Collect feedback
 ↓
Improve
 ↓
Evaluate again
```

This creates a continuous improvement loop for AI systems.

## Interview questions

### What is LangSmith?

> LangSmith is an observability and evaluation platform for LLM and agent applications. It provides tracing of runs, datasets, experiments and evaluation workflows.

### Why do we need LangSmith if we already have logs?

> Logs show application events, but LLM applications also need structured visibility into nested model/tool/retriever executions and evaluation against representative datasets. LangSmith provides that AI-specific execution and evaluation view.

### How would LangSmith help debug a RAG issue?

> I would inspect the trace to see the query, retrieved candidates, reranking, final context, model call, latency and token usage, then determine whether the failure originated in retrieval, context construction or generation.

### How would you evaluate a prompt change?

> Run the old and new versions against the same representative evaluation dataset and compare quality metrics along with latency and cost.

### What is an evaluation dataset?

> A representative collection of test cases used to measure application behavior consistently across versions.

### What is LLM-as-a-judge?

> Using another model to score an application's output against a defined rubric or reference. It is useful but should itself be validated because judge models are not infallible.

### LangSmith vs OpenTelemetry?

> LangSmith specializes in LLM/agent tracing and evaluation, while OpenTelemetry provides vendor-neutral telemetry standards for general application observability. They can coexist.

### Should you send all prompts and document content to an observability platform?

> Not blindly. I would classify telemetry, redact sensitive information, apply access control and retention policies, and only capture what is necessary for debugging and evaluation.

## Final mental model

```text
                         AI APPLICATION
                               ↓
                     LangChain / LangGraph
                               ↓
                    ┌──────────┴──────────┐
                    ↓                     ↓
                 Execution             Evaluation
                    ↓                     ↓
             Models / Tools /       Datasets / Judges
             Retrievers / Nodes           │
                    ↓                     ↓
                  Traces ─────────→ LangSmith
                    │
          ┌─────────┼──────────┐
          ↓         ↓          ↓
       Debugging  Latency     Quality
                    │
                    ↓
                Improvements
```

## Key takeaway

> **LangSmith answers two critical questions for an AI system: “What happened during this execution?” through tracing, and “How good is the system?” through evaluation and experiments.**
