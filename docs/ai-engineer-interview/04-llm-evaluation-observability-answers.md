# 04 — LLM Evaluation & Observability — Interview Notes

## 1. Why LLM Evaluation Is Different

Traditional software often has deterministic expected outputs. LLM systems can produce multiple valid outputs, so evaluation usually measures **quality and behavior**, not exact string equality.

For production AI, evaluation should connect:

```
Change → Quality → Latency → Cost → Safety → Reliability
```

## 2. Golden Dataset

A golden dataset is a curated set of representative inputs with trusted expected behavior or reference answers.

It is used for regression testing and comparing models, prompts, retrievers, or agent versions.

A good dataset should cover normal cases, difficult cases, edge cases, and known failure cases.

## 3. Test Dataset

A test dataset is used to measure system behavior against a defined evaluation set.

Keep evaluation data stable and versioned so results remain comparable over time.

Avoid tuning repeatedly on the same final test set because it reduces confidence in the measurement.

## 4. Human Evaluation

Human evaluation is useful when quality is subjective or difficult to automate, especially for helpfulness, tone, nuanced correctness, and safety.

Use clear scoring criteria and multiple reviewers when consistency matters.

## 5. Automated Evaluation

Automated evaluation uses deterministic metrics, rules, reference comparisons, or model-based judges.

It is faster and cheaper than human review and is suitable for continuous regression testing.

The limitation is that an automated metric can miss real-world quality problems.

## 6. LLM-as-a-Judge

An LLM evaluates another model's output using a defined rubric.

It is useful for semantic quality, relevance, style, and complex reasoning tasks.

It can have bias, judge-model limitations, and sensitivity to prompt/rubric design, so it should be validated against human evaluations.

## 7. Pairwise Evaluation

Two system outputs are compared directly and the evaluator chooses which is better.

It is often easier for humans or judges than assigning an absolute score.

Useful for model or prompt A/B comparisons.

## 8. Reference-Based vs Reference-Free Evaluation

**Reference-based:** compares the output to a known reference answer.

**Reference-free:** judges the output using the input, context, policy, or rubric without requiring one exact answer.

Reference-free evaluation is useful when many answers can be valid.

## 9. Regression Testing

Regression testing checks whether a change improves or breaks previously supported behavior.

Typical regression targets:

- Retrieval quality
- Answer quality
- Tool behavior
- Safety
- Structured output
- Latency
- Cost

## 10. Retrieval Metrics

### Recall@K

Fraction of relevant items that appear in the top K retrieved results.

High recall is important when missing the right document is costly.

### Precision@K

Fraction of the top K retrieved results that are relevant.

High precision reduces irrelevant context.

### MRR

Mean Reciprocal Rank measures how early the first relevant result appears.

Higher is better.

### NDCG

Normalized Discounted Cumulative Gain measures ranking quality while giving more weight to highly relevant results near the top.

## 11. Context Metrics

### Context Relevance

Measures whether retrieved context is relevant to the query.

### Context Precision

Measures how much of the retrieved context is relevant and useful.

### Context Recall

Measures whether the retrieved context contains the information needed to answer the query.

These metrics help separate retrieval problems from generation problems.

## 12. Faithfulness

Faithfulness measures whether the answer is supported by the provided context rather than invented.

A strong RAG system should reduce unsupported claims, but faithfulness alone does not guarantee that the retrieved context itself is correct.

## 13. Answer Relevance

Answer relevance measures whether the response actually addresses the user's question.

An answer can be factually supported but still irrelevant or incomplete.

## 14. Citation Accuracy

Citation accuracy checks whether citations actually support the claims they are attached to.

For enterprise RAG, this is often more useful than simply checking whether a citation exists.

## 15. Agent Evaluation

### Task Success

Did the agent complete the user's objective correctly?

### Tool Selection Accuracy

Did it choose the correct tool for the task?

### Tool Execution Accuracy

Did it provide valid arguments and use the tool correctly?

### Planning / Trajectory Evaluation

Did the sequence of actions make sense and avoid unnecessary or unsafe steps?

Agent evaluation should measure the **trajectory**, not only the final text.

## 16. Cost per Task and Step Count

For agents, cost depends on more than output tokens.

Track:

```
Total cost = model calls + embedding calls + tool/API costs + infrastructure cost
```

Step count is a useful operational metric because unnecessary iterations increase latency and cost.

## 17. Hallucination and Factuality

**Hallucination:** the system produces unsupported or fabricated information.

**Factuality:** whether claims are actually correct.

A response can be faithful to a retrieved document but still wrong if the source itself is wrong. That is why source quality and retrieval quality also matter.

## 18. Safety, Toxicity and Bias

Evaluation should check harmful content, policy violations, unsafe actions, sensitive data exposure, and undesirable bias.

Safety tests should include adversarial and edge-case inputs, not only normal user prompts.

## 19. Structured Output Correctness

For JSON/schema-based outputs, evaluate:

- Valid schema
- Required fields
- Correct types
- Allowed values
- Semantic correctness

A syntactically valid JSON response can still contain incorrect business data.

## 20. Observability

Observability lets us understand what happened inside the AI system.

Core signals:

- **Logs:** discrete events and errors
- **Metrics:** numeric measurements over time
- **Traces:** end-to-end execution path

For AI systems, tracing is especially valuable because one user request can trigger multiple model, retrieval, and tool operations.

## 21. Distributed Tracing

A trace follows one request across multiple services and operations.

Example:

```
API request
  → retrieval
  → reranker
  → LLM call
  → tool call
  → final response
```

Use a correlation/trace ID across services so the full request can be reconstructed.

## 22. AI-Specific Traces

Important trace information includes:

- Prompt/model version
- Token usage
- Retrieval query
- Retrieved document/chunk IDs
- Reranking results
- Tool calls and arguments
- Tool results/status
- LLM latency
- Total latency
- Errors
- Final outcome

Avoid logging raw sensitive data unnecessarily.

## 23. Token, Cost, Latency and Error Tracking

Track both aggregate and per-request metrics.

Examples:

- Input/output tokens
- Cost per request/task/tenant
- Time to first token
- Total response latency
- Tool latency
- Error rate
- Timeout rate
- Retry count

These metrics connect technical behavior to user experience and economics.

## 24. Evaluation Pipeline

A production evaluation pipeline can be:

```
Dataset
  ↓
Run model / RAG / agent
  ↓
Collect outputs + traces
  ↓
Calculate metrics / judge outputs
  ↓
Compare against baseline
  ↓
Quality + cost + latency gates
  ↓
Deploy or reject
```

## 25. Versioning

Version at least:

- Dataset
- Prompt
- Model
- Retrieval configuration
- Tool/schema definitions
- Evaluation logic

Without versioning, it becomes difficult to explain why quality changed.

## 26. A/B Testing

A/B testing sends comparable traffic to two variants and measures business and technical outcomes.

For LLM systems, compare quality together with latency, cost, safety, and task success—not just click-through or response preference.

## 27. Offline vs Online Evaluation

### Offline

Run a fixed dataset before deployment.

**Pros:** repeatable, controlled, cheap.

**Cons:** may not reflect real user behavior.

### Online

Evaluate on real production traffic using monitored metrics, feedback, or experiments.

**Pros:** realistic behavior.

**Cons:** harder to control and higher risk.

A mature system uses both.

## 28. Designing a Production Evaluation Strategy

Start with a small set of metrics tied to the product goal.

Example for RAG:

```
Retrieval → Recall@K + Precision@K
Generation → Faithfulness + Answer Relevance
Citations → Citation Accuracy
Production → Latency + Cost + Error Rate
```

For agents, add task success, tool accuracy, trajectory quality, step count, and unsafe-action rate.

## 29. Common Evaluation Pitfalls

- Optimizing one metric while another degrades
- Using only LLM-as-a-judge
- No versioned baseline
- Testing only easy examples
- Evaluating final answers but ignoring retrieval/tool failures
- Ignoring latency and cost
- Using a dataset that is too small or unrepresentative
- Logging too little to explain failures

## 30. Production Quality Loop

```
Observe → Evaluate → Find failure pattern → Change → Re-evaluate → Release
```

The goal is not to maximize a single score. The goal is to keep the complete system within acceptable quality, safety, latency, reliability, and cost boundaries.

## 31. Key Production Trade-offs

| Decision | Trade-off |
|---|---|
| Human vs automated evaluation | Quality/confidence vs speed/cost |
| Stronger judge model vs cheaper judge | Evaluation quality vs evaluation cost |
| More metrics vs fewer metrics | Coverage vs complexity |
| Offline vs online | Control vs realism |
| More tracing vs less tracing | Debuggability vs storage/privacy overhead |

## 32. Interview Questions

### Evaluation Fundamentals

1. Why is evaluating LLMs different from testing traditional software?
2. What is a golden dataset?
3. Human evaluation vs automated evaluation?
4. What is LLM-as-a-judge and what are its limitations?
5. Pairwise vs reference-based evaluation?
6. Why is regression testing important for LLM systems?

### RAG Evaluation

7. Explain Recall@K and Precision@K.
8. What is MRR?
9. What is NDCG and when would you use it?
10. Context precision vs context recall?
11. Faithfulness vs answer relevance?
12. How would you measure citation accuracy?
13. How would you determine whether a poor answer is caused by retrieval or generation?

### Agent Evaluation

14. How do you evaluate an agent differently from a chatbot?
15. What is task success?
16. How would you measure tool-selection accuracy?
17. How would you evaluate an agent trajectory?
18. Why should you measure step count?
19. How would you detect excessive tool usage?

### Observability

20. Logs vs metrics vs traces?
21. Why is distributed tracing important for AI systems?
22. What would you capture in an LLM trace?
23. How would you track token and cost usage per tenant?
24. What latency metrics would you monitor?
25. How would you debug a user complaint about a bad RAG answer?

### Production / Design

26. Design an evaluation pipeline for a production RAG system.
27. What quality gates would you use before deploying a new model?
28. How would you version prompts, datasets, and models?
29. Offline vs online evaluation?
30. How would you combine quality, latency, cost, and safety in release decisions?
31. What are the biggest mistakes teams make when evaluating LLM applications?