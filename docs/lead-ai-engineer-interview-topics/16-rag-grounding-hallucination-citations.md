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

## 12. Project-based interview question

### How would you reduce hallucination in a RAG system?

> "I'd address it at multiple layers rather than relying only on prompting. First, improve retrieval quality through good parsing, chunking, hybrid retrieval and reranking. Then construct concise context with clear source boundaries and instruct the model to answer only from supported evidence and abstain when evidence is insufficient. I'd preserve provenance so citations come from actual retrieved metadata, and I'd evaluate faithfulness, retrieval quality and answer correctness separately."

### Can RAG completely eliminate hallucination?

> "No. RAG can reduce unsupported generation by providing relevant evidence, but hallucinations can still happen because retrieval can fail, source data can be incorrect, or the model can misinterpret the supplied context."

### How would you ensure citations are trustworthy?

> "I'd attach citations from retrieval metadata rather than asking the LLM to invent source references. Each chunk should carry document and page/source identifiers, and the application should map retrieved evidence back to those sources."

### What if the answer isn't present in the documents?

> "The system should abstain or clearly state that the available evidence is insufficient rather than generating an unsupported answer."

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
- [x] project-based interview answers
