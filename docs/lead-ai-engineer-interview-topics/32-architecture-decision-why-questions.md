# Topic 32 — Architecture Decision: "Why Did We Choose This?"

**Status:** Complete

## Purpose

This topic prepares project-specific interview questions that test engineering judgment rather than definitions.

For every major AI Platform component, be ready to explain:

1. What did we choose?
2. Why did we choose it?
3. What alternatives did we consider?
4. What trade-offs did we accept?
5. How would we validate the decision?
6. When would we change the decision?

> Important: Do not claim that we benchmarked a component unless the project actually contains that evidence. When the repository documents the implementation but not the historical selection process, frame the answer as the engineering rationale we would use to defend the design.

---

# 1. Parser — Why did we choose these parser options?

### Primary question

**Why did you choose LiteParse and Llama Cloud instead of using a single parser?**

### Project answer

We wanted a stable parser abstraction with different operational choices. LiteParse gives us a local/in-process option for development and testing without a cloud dependency, while Llama Cloud is the higher-quality managed option for production-style document parsing. Both are normalized into our own `ParsedDocument` model so the rest of the SDK is not coupled to vendor-specific response classes.

### Follow-ups

- Why not use Llama Cloud everywhere?
- What are the trade-offs between local and managed parsing?
- What happens if the managed parser is unavailable?
- Why normalize parser output?
- Why shouldn't AI Platform depend directly on Llama Cloud classes?
- How would you add another parser?
- How would you evaluate parser quality?

### Key trade-offs

```text
Local parser
→ low external dependency
→ easy development/testing
→ potentially lower parsing quality

Managed parser
→ stronger document understanding
→ external API/cost/latency dependency
```

### Strong answer pattern

> "I didn't want the parsing vendor to become an architectural dependency. I put both implementations behind a parser interface and normalize them into `ParsedDocument`. That lets us choose the operational profile without changing chunking, embeddings, or the platform." 

---

# 2. Markdown — Why make Markdown the primary parsed representation?

### Question

**Why did you choose Markdown as the representation passed from parsing into chunking?**

### Answer

Markdown gives us a lightweight structured representation that preserves useful document hierarchy such as headings, paragraphs, lists and tables. That structure is valuable for semantic chunking because the chunker can reason about H1/H2/H3 boundaries instead of treating the document as an unstructured string.

### Follow-ups

- Why not plain text?
- Does Markdown guarantee perfect table reconstruction?
- What if the parser loses structure?
- Why should the platform depend on `ParsedDocument` rather than parser-specific output?

### Project-specific point

The parser contract explicitly preserves text, Markdown, page information and elements, while Markdown is the primary structured representation consumed by chunking.

---

# 3. Chunking — Why semantic Markdown-aware chunking?

### Primary question

**Why did you choose semantic chunking instead of fixed-size chunking?**

### Project answer

Our documents include reports, resumes, contracts and financial statements where document structure carries meaning. Splitting purely every N characters or tokens can separate a heading from its content or split related information unnecessarily. We therefore prioritize semantic boundaries from the Markdown hierarchy and only split further when a section exceeds the size limit.

```text
Semantic boundary
       ↓
Size constraint
       ↓
Paragraph boundary
       ↓
Word boundary
       ↓
Character boundary
```

### Follow-ups

- Why not recursive character splitting?
- Why 2000 characters?
- Why not 500 tokens?
- Do we use overlap?
- Why preserve parent heading context?
- Why are tables special?
- What happens to a section larger than the limit?
- How would you prove semantic chunking is better?

### Project-specific details

The finalized strategy uses a 2000-character maximum, not a target. H1/H2 define major sections, deeper headings define subsections, parent context is preserved when large sections are split, and character splitting is the final fallback.

### Strong answer

> "The goal isn't to create equally sized strings; it is to create retrieval-oriented units of meaning. For example, a financial table under `Balance Sheet → Assets` is much more useful when the retrieved chunk retains that heading context."

### Trade-off

```text
Better semantic coherence
        vs
Potentially uneven chunk sizes
        vs
More complex chunking logic
```

---

# 4. Why preserve page numbers and deterministic chunk IDs?

### Question

**Why did you keep page numbers and deterministic chunk IDs in the chunk model?**

### Answer

Page numbers support source attribution and debugging. Deterministic IDs make chunks reproducible and easier to trace across ingestion, retrieval, testing and persistence.

```text
Document
  ↓
chunk-0
chunk-1
chunk-2
```

A retrieved chunk can therefore be traced back to its document and source page.

### Follow-ups

- Why not use random UUIDs only?
- How do deterministic IDs help re-ingestion?
- What metadata should remain application-owned?

---

# 5. Embeddings — Why this embedding model?

### Primary question

**Why did you choose the current embedding model instead of a larger or different model?**

### Answer

The selection should be explained as a quality/cost/latency decision rather than simply saying that one model is "best." Our platform uses a pluggable `EmbeddingProvider`, so the architecture does not depend on one vendor. The current tested embedding output is 1536 dimensions and the platform stores it as `vector(1536)`.

### Follow-ups

- Why not use a larger embedding model?
- What does higher dimensionality buy you?
- What is the cost impact?
- How would you benchmark two embedding models?
- What happens if we change the embedding model?
- Can old and new embeddings be searched together?
- Why must query and document embeddings be compatible?
- Why abstract the embedding provider?

### Important production answer

> "I would not change an embedding model in place and assume existing vectors remain compatible. A model change normally requires a re-embedding strategy, because the vector space can change. I would evaluate retrieval quality, latency, storage and cost before migrating."

### Evaluation

Use a representative evaluation set and measure retrieval quality such as Recall@K/Precision@K, along with latency and cost.

---

# 6. PostgreSQL + pgvector — Why not Pinecone/Qdrant/Weaviate?

### Question

**Why did you choose PostgreSQL with pgvector?**

### Answer

Our platform already needs relational document metadata, permissions and application data. PostgreSQL lets us keep relational filtering and vector retrieval in one system while avoiding an additional specialized database for the current scale and architecture.

### Follow-ups

- When would you choose a dedicated vector database?
- How does permission filtering interact with retrieval?
- How would this change at very large scale?
- What are the operational trade-offs?
- Which vector index would you use?

### Trade-off

```text
PostgreSQL + pgvector
→ simpler architecture
→ relational + vector data together
→ strong filtering capabilities

Dedicated vector DB
→ specialized vector-scale features
→ potentially better fit at very large scale
→ additional operational system
```

---

# 7. Semantic Search — Why not keyword search alone?

### Question

**Why did you choose vector search?**

### Answer

Users often ask questions using different wording from the documents. Embeddings allow us to match semantic meaning rather than requiring exact term overlap.

```text
Query:
"How much money did the company make?"

Document:
"Net revenue reached $25M."
```

The wording differs but the concepts are related.

### Follow-ups

- What are the weaknesses of vector search?
- How does cosine similarity work?
- What does the similarity threshold mean?
- Is similarity a probability of correctness?

### Important project point

Our `min_similarity = 0.30` is an initial candidate-quality filter. It should not be interpreted as a probability that the result is correct.

---

# 8. Hybrid Search — Why semantic + keyword search?

### Primary question

**Why did you choose hybrid search instead of semantic search alone?**

### Project answer

The two retrieval signals solve different problems. Vector search is strong for semantic meaning and paraphrases. Keyword search is valuable for exact identifiers, names, codes, numbers, error messages and rare domain-specific terms.

```text
Vector search
→ semantic meaning

Keyword search
→ exact lexical evidence

Both
→ broader retrieval coverage
```

### Example

```text
Query:
"Why did account AC-93821 revenue decline?"
```

`AC-93821` benefits from lexical matching, while `revenue decline` benefits from semantic matching.

### Follow-ups

- Why not vector search alone?
- Why not BM25 alone?
- When is keyword search better?
- Can both searches run concurrently?
- Why use RRF afterward?
- Why not simply concatenate the results?
- Why not add raw vector and keyword scores?
- How would you tune the two retrieval depths?

### Strong answer

> "Hybrid retrieval is about complementary signals. Semantic retrieval handles meaning, while lexical retrieval protects exact-match cases. In enterprise documents, identifiers and domain-specific terms are common enough that I don't want to depend on semantic similarity alone."

---

# 9. RRF — Why Reciprocal Rank Fusion?

### Question

**Why did you choose RRF to combine vector and keyword results?**

### Answer

Vector similarity scores and keyword scores can have different scales and meanings. Directly adding them can therefore be misleading unless they are normalized or calibrated. RRF combines ranked lists using rank positions, avoiding the need to make the two raw score distributions directly comparable.

```text
Vector ranked list
        +
Keyword ranked list
        ↓
       RRF
        ↓
combined candidate ranking
```

### Follow-ups

- Explain the RRF formula.
- What is the RRF constant?
- Why not concatenate lists?
- Why not normalize scores and add them?
- When would weighted fusion make sense?
- How would you tune RRF?

### Strong answer

> "RRF gives us a simple rank-based fusion mechanism. It lets both retrieval systems contribute without pretending that their raw scores have the same statistical meaning."

---

# 10. Candidate Top-K — Why retrieve 20 and return 5?

### Question

**Why do we retrieve a larger candidate set and then reduce it to the final top-K?**

### Answer

The first retrieval stage is optimized for recall. We want enough candidates so that relevant evidence is not lost early. The reranker then performs a more expensive relevance comparison and selects the best final context.

```text
Broad retrieval
20 candidates
      ↓
Fine-grained reranking
      ↓
5 final chunks
```

### Follow-ups

- Why 20?
- Why 5?
- Why not retrieve 5 directly?
- Why not retrieve 1000?
- What happens to latency as candidate count increases?
- How would you tune these values?

### Strong answer

> "The exact numbers are configuration choices, not universal constants. I would tune candidate depth and final context size against retrieval quality, answer quality, latency and cost using a representative evaluation set."

---

# 11. Reranker — Why add a reranking stage?

### Primary question

**Why did you choose reranking after hybrid retrieval?**

### Answer

Initial retrieval is optimized to efficiently produce a candidate set. A reranker can perform a more detailed query-document relevance comparison over that smaller set. This gives us a two-stage retrieval architecture: high-recall candidate generation followed by higher-precision ordering.

```text
Vector + keyword
       ↓
      RRF
       ↓
 candidate pool
       ↓
   reranker
       ↓
   final Top-K
```

### Follow-ups

- Why not send RRF results directly to the LLM?
- Why not rerank the entire database?
- Why 20 candidates?
- What is the latency cost?
- How would you prove reranking helps?
- What happens if the reranker is unavailable?

---

# 12. Nemotron Reranker — Why this model?

### Question

**Why did you choose the Nemotron reranker?**

### Project answer

Our current architecture uses `nvidia/llama-nemotron-rerank-vl-1b-v2` through OpenRouter. The important architectural decision is that the reranker sits behind a provider abstraction and operates on the small candidate pool rather than the whole corpus. This keeps the expensive relevance step bounded.

### Follow-ups

- Why not use a different reranker?
- Why a 1B-class model?
- Why use OpenRouter?
- What are the latency and cost implications?
- Does the current implementation actually send images?
- How would you benchmark rerankers?
- What would make you replace it?

### Important honesty point

The current implementation sends text candidates. The abstraction leaves room for multimodal candidates later; do not claim that the current pipeline is already multimodal.

### Replacement criteria

I would consider replacing the reranker if another model provides a meaningful improvement in ranking quality at an acceptable latency/cost level, based on evaluation data rather than model reputation alone.

---

# 13. Why not rerank before RRF?

### Question

**Why do we fuse vector and keyword results first and rerank afterward?**

### Answer

RRF gives us a unified candidate pool from complementary retrieval systems. The reranker then operates once on that fused pool. This avoids independently performing expensive reranking for each retrieval branch and lets the reranker compare candidates coming from both signals.

```text
Vector ──┐
         ├→ RRF → candidate pool → reranker
Keyword ─┘
```

---

# 14. Why metadata/permission filtering matters

### Question

**Why isn't permission filtering something we can do after retrieval?**

### Answer

In a multi-tenant or enterprise system, unauthorized chunks should never enter the candidate set that can reach the RAG/LLM layer. Authorization is therefore part of the retrieval boundary, not merely a UI concern.

### Follow-ups

- Where should tenant filtering happen?
- Can the LLM enforce permissions?
- What if a reranker sees unauthorized chunks?
- How do document metadata and application metadata differ?

### Strong answer

> "The LLM is not an authorization system. Access control must be enforced before retrieved content is exposed to downstream generation."

---

# 15. Why keep retrieval outside the SDK?

### Question

**Why doesn't the Document Intelligence SDK perform vector retrieval?**

### Answer

The SDK is intentionally responsible for document preprocessing: parsing, normalized representation, chunking and embeddings. Retrieval depends on application concerns such as persistence, permissions, tenant filtering, search strategy, ranking and domain requirements. Keeping those concerns in AI Platform prevents the SDK from being coupled to PostgreSQL or a particular retrieval architecture.

```text
SDK
→ parse
→ chunk
→ embed
→ ProcessedDocument

AI Platform
→ persist
→ retrieve
→ filter
→ fuse
→ rerank
→ RAG
```

### Follow-ups

- Why not put pgvector inside the SDK?
- Why is this separation useful for reuse?
- What happens if the platform changes databases?
- Why can the SDK still expose an EmbeddingProvider for query text?

---

# 16. Why PostgreSQL stores the embedding with document chunks?

### Question

**Why didn't we create a separate embedded-chunks table?**

### Answer

The SDK's `EmbeddedChunk` is a processing model, not necessarily a persistence model. The platform can flatten the embedding onto its existing `document_chunks` record, keeping the chunk text, metadata, page information and vector together.

```text
EmbeddedChunk
    ↓
DocumentChunk + embedding
    ↓
document_chunks
```

This keeps the persistence model simple while preserving the SDK boundary.

---

# 17. RAG — Why separate RAG from retrieval?

### Question

**Why don't we put retrieval logic directly inside RAG?**

### Answer

Retrieval and generation have different responsibilities. Retrieval finds and ranks evidence; RAG orchestrates retrieval, builds context, applies grounded prompting, calls the LLM and returns source attribution. Keeping them separate allows the retrieval engine to be reused by knowledge APIs and future agents.

```text
Retrieval
→ evidence

RAG
→ evidence → context → grounded generation
```

### Follow-ups

- Why does RAG need a no-evidence path?
- Why return citations?
- Why shouldn't the LLM invent source metadata?

---

# 18. Why don't we call the LLM when retrieval returns zero chunks?

### Question

**Why return a no-evidence response instead of asking the LLM anyway?**

### Answer

If the application promises grounded answers over supplied documents, calling the LLM without evidence increases the chance of unsupported answers. Our current behavior is to return a no-information response and skip the LLM when retrieval returns no chunks.

```text
Retrieval
   ↓
[]
   ↓
No information found
   ↓
No LLM call
```

---

# 19. Why citations are application-owned

### Question

**Why shouldn't the LLM generate document IDs and page numbers itself?**

### Answer

Source metadata is authoritative application data. The LLM can indicate which retrieved context supports an answer, but the application should map those references to trusted document/chunk/page metadata rather than allowing the model to invent identifiers.

---

# 20. Why use abstractions/providers?

### Question

**Why did you introduce parser, embedding and reranker abstractions instead of directly calling vendors?**

### Answer

The abstractions isolate vendor-specific infrastructure from the core workflow. They allow us to swap providers, test with mocks, control configuration and avoid spreading vendor-specific code throughout the platform.

```text
Core workflow
      ↓
 abstraction
   /     |     \
Provider A  B  C
```

### Follow-ups

- Isn't this over-engineering?
- When should you avoid an abstraction?
- How does this help testing?
- How does it support the Open/Closed Principle?

### Strong answer

> "I use abstractions where the implementation is a genuine variability point—parsers, embeddings and reranking providers are exactly that. I wouldn't create an interface for every class just for the sake of abstraction."

---

# 21. The ultimate interviewer challenge

Be ready for:

### "Your architecture works. What would you change if you had to reduce latency by 50%?"

Think through the pipeline:

```text
Parsing
→ ingestion-time, usually not query critical

Embedding
→ cache query embeddings where appropriate

Vector + keyword
→ run concurrently

RRF
→ inexpensive

Reranker
→ likely expensive query-time stage

LLM
→ often another major latency/cost component
```

Possible investigation order:

1. Measure each stage.
2. Remove speculation.
3. Optimize the actual bottleneck.
4. Consider reducing candidate count.
5. Consider a faster reranker.
6. Consider caching where safe.
7. Preserve retrieval quality while optimizing.

---

# 22. "How would you prove your architecture is better?"

Never answer only with intuition.

Build an evaluation set containing representative queries:

```text
semantic queries
exact identifier queries
mixed queries
financial/table queries
no-answer queries
permission-filtered queries
```

Then compare configurations:

```text
A: vector only
B: keyword only
C: vector + keyword
D: hybrid + RRF
E: hybrid + RRF + reranker
```

Measure:

- Recall@K
- Precision@K
- ranking quality
- answer groundedness
- citation correctness
- latency
- token usage
- infrastructure/API cost

### Strong answer

> "I would treat each architectural component as a hypothesis and validate it against representative evaluation queries. The best architecture is not the one with the most components; it is the one that gives the required quality at acceptable latency and cost."

---

# 23. Rapid-fire "Why?" Questions

Use these for mock interviews:

1. Why LiteParse?
2. Why Llama Cloud?
3. Why a parser abstraction?
4. Why normalize parser output?
5. Why Markdown?
6. Why semantic chunking?
7. Why 2000 characters?
8. Why preserve parent headings?
9. Why preserve page numbers?
10. Why deterministic chunk IDs?
11. Why embeddings?
12. Why the current embedding model?
13. Why 1536 dimensions?
14. Why PostgreSQL + pgvector?
15. Why cosine similarity?
16. Why semantic search?
17. Why keyword search?
18. Why hybrid search?
19. Why RRF?
20. Why not add raw scores?
21. Why retrieve 20 candidates?
22. Why rerank?
23. Why rerank after RRF?
24. Why Nemotron?
25. Why OpenRouter?
26. Why final top-K of 5?
27. Why metadata filtering?
28. Why permission filtering before generation?
29. Why keep retrieval outside the SDK?
30. Why separate retrieval and RAG?
31. Why no LLM call when there is no evidence?
32. Why application-owned citations?
33. Why provider abstractions?
34. Why not build everything with one vendor?
35. What would make you replace each component?
36. How would you prove each decision was correct?

---

# Final Interview Mental Model

When asked **"Why did you choose X?"**, don't start with a definition.

Use:

```text
Requirement
    ↓
Problem
    ↓
Options
    ↓
Decision
    ↓
Trade-off
    ↓
Validation
    ↓
When I would change it
```

### Example

> "We needed retrieval that worked for both natural-language questions and exact identifiers. Vector search handles semantic similarity, but exact IDs and rare technical terms are better served by lexical retrieval. So we chose hybrid retrieval and fused the results with RRF because the score scales are different. We then rerank a bounded candidate set to improve final ordering. I'd validate that decision with retrieval-quality, answer-quality, latency and cost measurements, and I'd change it if the evaluation showed that the additional complexity wasn't providing enough benefit."

That is the style of answer expected from a production-minded AI Engineer rather than a purely theoretical RAG answer.
