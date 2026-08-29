# Topic 16 — RAG Hallucination, Grounding & Citations

**Status:** Complete

## Focus
Grounded generation, prompt constraints, context selection, citation generation/validation, no-answer behavior and hallucination mitigation.

## 1. What is hallucination?

A hallucination is when an LLM generates information that is unsupported, incorrect, or not grounded in the available evidence.

Example:

```text
Retrieved context:
"Q4 revenue was $25M."

Good:
→ "$25M"

Hallucination:
→ "$32M"
```

## 2. Why can RAG still hallucinate?

RAG has multiple stages and a failure at any stage can contribute to a bad answer:

```text
Document
   ↓
Parsing
   ↓
Chunking
   ↓
Embedding
   ↓
Retrieval
   ↓
Reranking
   ↓
Context
   ↓
LLM
   ↓
Answer
```

Typical failure cases:

```text
Relevant information exists
        ↓
retrieval fails to find it
        ↓
LLM doesn't see the evidence
        ↓
LLM generates anyway
```

or:

```text
Correct chunk retrieved
        ↓
bad context/prompt construction
        ↓
LLM misinterprets context
        ↓
incorrect answer
```

## 3. What is grounding?

Grounding means that the generated answer is supported by information from a trusted source or supplied context.

```text
User Query
    +
Retrieved Evidence
    ↓
   LLM
    ↓
Grounded Answer
```

### Grounding vs correctness

Grounding does not guarantee that the source itself is correct.

```text
Grounding
≠
absolute truth
```

An answer can be faithful to incorrect retrieved data.

## 4. How to reduce hallucination

Use multiple layers rather than relying only on a prompt:

- improve parsing and chunking
- improve embeddings/retrieval
- use hybrid search, RRF and reranking
- apply metadata/permission filtering
- construct concise, clearly separated context
- instruct the model to answer only from supported evidence
- use structured outputs where appropriate
- preserve provenance and citations
- evaluate retrieval and generation independently

## 5. No-answer / abstention behavior

If the evidence does not contain the answer, the system should say that the available information is insufficient rather than invent an answer.

```text
Question
   ↓
No supporting evidence
   ↓
Abstain / clearly state insufficient information
```

## 6. Citations

Citations connect generated claims back to retrieved source evidence.

A chunk should preserve provenance such as:

```text
document_id
page_number
source
metadata
```

Then:

```text
Retrieved chunk
     ↓
Answer
     ↓
Source citation
```

### Important rule

Do not rely on the LLM to invent citations. Prefer attaching citations from trusted retrieval metadata maintained by the application.

## 7. Context construction

A useful structure is:

```text
SYSTEM:
Answer using only the provided evidence.

CONTEXT:
[1] Annual Report, page 42
Revenue was $25M...

[2] Annual Report, page 43
Operating expenses were $12M...

QUESTION:
What was Q4 revenue?
```

This makes evidence boundaries explicit and allows the application to map citation IDs back to source metadata.

## 8. Retrieval failure vs generation failure

When an answer is wrong, first determine whether the correct evidence was retrieved.

### If the answer evidence was not retrieved

Investigate:

```text
parsing
chunking
embedding
vector search
keyword search
RRF
reranking
filters
```

### If the correct evidence was retrieved

Investigate:

```text
prompt
context ordering
context size
model behavior
structured output
```

## 9. Faithfulness vs answer correctness

**Faithfulness:** Is the answer supported by the provided context?

**Answer correctness:** Is the answer actually correct according to the expected/ground-truth answer?

These can diverge. Correctly repeating incorrect retrieved information can be faithful but not correct.

## 10. Context compression

If retrieval returns 20 chunks but only 5 are useful, compression/reranking can reduce the context:

```text
20 chunks
   ↓
reranking/compression
   ↓
5 useful chunks
   ↓
LLM
```

Benefits include lower token usage, lower latency and less irrelevant context.

## 11. Security and grounding

In enterprise RAG, relevance alone is not sufficient. Retrieved context must also be authorized for the caller.

```text
User
 ↓
permission / tenant filter
 ↓
retrieval
 ↓
RRF
 ↓
reranking
 ↓
LLM context
```

A highly relevant document that the user is not authorized to access must not enter the context.

# 12. How do we evaluate retrieval quality?

RAG quality should not be evaluated only from the final LLM answer. First evaluate whether retrieval is finding the right evidence.

Create a representative evaluation dataset containing:

```text
query
expected relevant document/chunk IDs
optional ground-truth answer
```

Then run the retrieval pipeline and compare the retrieved chunks with the expected relevant chunks.

### Recall@K

> **Recall@K asks: did we retrieve the relevant chunk within the top K results?**

Example:

```text
Relevant chunk = doc7
Retrieved top-5 = doc1, doc7, doc3, doc9, doc2

Recall@5 = 1 for this query
```

If the relevant chunk is not in the top K:

```text
Recall@K = 0
```

Across many queries, average these values.

### Precision@K

> **Precision@K asks: how many of the top K retrieved results are actually relevant?**

Example:

```text
Top-5 retrieved
Relevant = 3

Precision@5 = 3/5 = 0.60
```

### MRR — Mean Reciprocal Rank

MRR focuses on how high the first relevant result appears.

```text
first relevant rank = 1
→ reciprocal rank = 1/1

first relevant rank = 4
→ reciprocal rank = 1/4
```

Average the reciprocal ranks across evaluation queries.

### NDCG@K

NDCG is useful when relevance is graded rather than simply relevant/not relevant.

For example:

```text
3 = highly relevant
2 = relevant
1 = weakly relevant
0 = irrelevant
```

It evaluates whether highly relevant results appear near the top.

### Retrieval metrics to remember

```text
Recall@K
Precision@K
MRR
NDCG@K
```

For a first interview answer, **Recall@K + MRR + NDCG@K** are particularly useful to mention, while Precision@K helps explain retrieval noise.

## 13. How do we evaluate the complete RAG pipeline?

Separate evaluation into layers:

```text
              RAG Evaluation
                    │
        ┌───────────┴───────────┐
        ↓                       ↓
 Retrieval quality        Generation quality
        │                       │
 Recall@K                  Faithfulness
 Precision@K               Answer correctness
 MRR                       Citation quality
 NDCG@K                    Relevance
```

Also track operational metrics:

```text
latency
cost
failure rate
cache hit rate
```

### A useful evaluation dataset

For each test question, keep:

```text
query
relevant chunk/document IDs
expected answer
expected citation/source
```

Then we can evaluate each stage independently instead of saying only:

> "The RAG answer looks good."

## 14. Which metrics should we track in production?

Track three categories.

### Retrieval quality

```text
Recall@K
Precision@K
MRR
NDCG@K
retrieval candidate count
reranker ranking changes
```

### Generation quality

```text
faithfulness / groundedness
answer correctness
answer relevance
citation correctness
no-answer / abstention quality
```

### System/production metrics

```text
p50/p95/p99 latency
TTFT
LLM input/output tokens
cost per request
error rate
retry/fallback rate
cache hit rate
vector-search latency
keyword-search latency
reranker latency
LLM latency
```

The important idea is:

> **Quality metrics tell us whether the system is good; operational metrics tell us whether the system is healthy and affordable.**

## 15. How do we identify where RAG quality is failing?

Use stage-level evaluation:

```text
Question
   ↓
Did parsing preserve the information?
   ↓
Did chunking preserve useful context?
   ↓
Did retrieval find the relevant chunk?
   ↓
Did RRF/reranking put it high enough?
   ↓
Did context construction preserve it?
   ↓
Did the LLM answer correctly from it?
```

This prevents changing the LLM when the real problem is retrieval.

## 16. What causes hallucinations in RAG and how can we reduce them?

Common causes:

```text
poor parsing
bad chunking
relevant chunk not retrieved
noisy/irrelevant context
insufficient evidence
prompt ambiguity
context overload
model misinterpretation
incorrect source data
```

Mitigations:

```text
better parsing/chunking
hybrid retrieval
RRF
reranking
permission filtering
context compression
clear grounding instructions
citations/provenance
abstention when evidence is insufficient
evaluation
```

Important interview point:

> **RAG reduces hallucination but does not eliminate it.**

## 17. How would you optimize latency in RAG?

First measure the full latency breakdown:

```text
query embedding
vector search
keyword search
RRF
reranker
context construction
LLM TTFT
total LLM generation
```

Then optimize the actual bottleneck.

Common techniques:

```text
parallel vector + keyword retrieval
caching
smaller candidate sets
reranking only necessary candidates
context compression
smaller prompts
batch embeddings for ingestion
model routing
streaming for better perceived latency
```

Example:

```text
Vector search ──────┐
                    ├── concurrent
Keyword search ─────┘
                    ↓
                   RRF
```

Do not assume streaming reduces total inference time; it primarily improves time-to-first-output/perceived responsiveness.

## 18. When should you choose hybrid search?

Choose hybrid search when your corpus/query mix contains both:

```text
semantic questions
+
exact lexical signals
```

Especially:

```text
IDs
codes
product names
invoice numbers
error codes
technical terms
numbers
exact phrases
```

Example:

```text
"Why did account AC-93821 revenue decline?"
```

`AC-93821` benefits from lexical retrieval while `revenue decline` benefits from semantic retrieval.

Do not automatically add hybrid search if vector retrieval already meets the required quality and the additional complexity/latency is not justified. Evaluate it against a vector-only baseline.

## 19. When should you choose a reranker?

A reranker is useful when first-stage retrieval has reasonable recall but the final ordering is not precise enough.

Typical situation:

```text
1M chunks
   ↓
vector/keyword retrieval
   ↓
50 candidates
   ↓
reranker
   ↓
Top 5
```

Choose a reranker when:

```text
retrieval recall is acceptable
but top-K precision needs improvement
```

Be cautious when:

```text
latency budget is extremely strict
candidate set is very large
first-stage retrieval is already sufficient
reranker cost is not justified
```

The decision should be based on evaluation:

```text
Hybrid → Top-K
        vs
Hybrid → Reranker → Top-K
```

Compare:

```text
retrieval/answer quality
latency
cost
```

## 20. How do you choose between hybrid search and reranking?

They solve different problems and can be used together.

```text
Hybrid search
→ improves candidate coverage using complementary signals

Reranker
→ improves ordering/precision of retrieved candidates
```

A common architecture is:

```text
Vector + Keyword
       ↓
      RRF
       ↓
 candidate pool
       ↓
   Reranker
       ↓
    Final Top-K
```

Use evaluation to determine whether each stage provides enough benefit to justify its cost and latency.

## 21. Project-based interview question

### How would you reduce hallucination in a RAG system?

> "I'd address it at multiple layers rather than relying only on prompting. First, improve retrieval quality through good parsing, chunking, hybrid retrieval and reranking. Then construct concise context with clear source boundaries and instruct the model to answer only from supported evidence and abstain when evidence is insufficient. I'd preserve provenance so citations come from actual retrieved metadata, and I'd evaluate faithfulness, retrieval quality and answer correctness separately."

### Can RAG completely eliminate hallucination?

> "No. RAG can reduce unsupported generation by providing relevant evidence, but hallucinations can still happen because retrieval can fail, source data can be incorrect, or the model can misinterpret the supplied context."

### How would you ensure citations are trustworthy?

> "I'd attach citations from retrieval metadata rather than asking the LLM to invent source references. Each chunk should carry document and page/source identifiers, and the application should map retrieved evidence back to those sources."

### What if the answer isn't present in the documents?

> "The system should abstain or clearly state that the available evidence is insufficient rather than generating an unsupported answer."

### How do you evaluate retrieval quality?

> "I'd build a representative evaluation set with queries and known relevant chunks, then measure metrics such as Recall@K, Precision@K, MRR and NDCG@K. I'd also inspect failure cases manually and compare retrieval configurations using the same evaluation set."

### How do you evaluate the complete RAG pipeline?

> "I'd separate retrieval evaluation from generation evaluation. For retrieval I'd measure Recall@K, MRR and NDCG. For generation I'd measure faithfulness, answer correctness, relevance and citation correctness. I'd also track latency, token usage, cost and failure rates so quality improvements don't create unacceptable operational costs."

### How would you optimize latency in RAG?

> "First I'd instrument each stage to find the bottleneck. Then I'd parallelize independent retrieval calls, optimize candidate depth and reranking, use caching and context compression, reduce unnecessary prompt tokens and use streaming to improve perceived latency. I'd re-measure both latency and quality after each change."

### When would you choose hybrid search?

> "When queries contain both semantic intent and exact lexical signals such as identifiers, codes, names, numbers or technical terms. I'd compare hybrid retrieval against vector-only retrieval on representative evaluation queries rather than adding it automatically."

### When would you choose a reranker?

> "When first-stage retrieval has enough recall but the ordering of the top candidates is not precise enough. I'd rerank a bounded candidate set and compare the quality improvement against the added latency and cost."

### Hybrid search vs reranker?

> "Hybrid search improves candidate coverage by combining different retrieval signals, while reranking improves the ordering of candidates already retrieved. They are complementary and can be used together as Vector + Keyword → RRF → Reranker → Top-K."

## Key mental model

```text
                  USER QUERY
                      │
                      ▼
                 RETRIEVAL
             ┌────────┴────────┐
             ▼                 ▼
         Vector             Keyword
             └────────┬────────┘
                      ▼
                     RRF
                      ▼
                  Reranker
                      ▼
               Authorized chunks
                      ▼
              Context construction
                      ▼
                     LLM
                      ▼
             Answer + source metadata
                      ▼
                   Citation
                      │
                      ▼
                 Evaluation
          ┌───────────┴───────────┐
          ↓                       ↓
   Retrieval quality       Generation quality
   Recall/Precision        Faithfulness
   MRR/NDCG                Correctness/Citations
```

## Checklist

- [x] hallucination definition
- [x] why RAG can still hallucinate
- [x] grounding
- [x] grounding vs correctness
- [x] retrieval vs generation failure
- [x] abstention/no-answer behavior
- [x] citations and provenance
- [x] context construction
- [x] faithfulness vs correctness
- [x] context compression
- [x] authorized retrieval
- [x] retrieval evaluation dataset
- [x] Recall@K
- [x] Precision@K
- [x] MRR
- [x] NDCG@K
- [x] generation evaluation
- [x] production RAG metrics
- [x] hallucination causes and mitigation
- [x] RAG latency optimization
- [x] when to use hybrid search
- [x] when to use reranking
- [x] hybrid vs reranker
- [x] project-based interview answers
