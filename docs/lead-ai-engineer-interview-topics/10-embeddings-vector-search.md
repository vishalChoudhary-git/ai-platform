# Topic 10 — Embeddings & Vector Search Fundamentals

**Status:** Complete

## Focus
Embeddings, semantic similarity, cosine similarity, magnitude/norm, normalization, dot product, vector dimensions, vector indexes, pgvector, metadata filters and retrieval trade-offs.

## 1. What is an embedding?

> **An embedding is a numerical representation of text that captures semantic meaning.**

Example:

```text
"How much revenue did we make?"

"What were our total sales?"
```

The wording is different, but the meaning is similar, so their embeddings should be relatively close in vector space.

```text
Text
 ↓
Embedding model
 ↓
Vector
```

The individual numbers are not interpreted directly by us; the relationship between vectors is what matters for semantic search.

## 2. Embedding dimensions

A vector's dimension is the number of numerical values it contains.

For example, a 1,536-dimensional vector contains 1,536 values:

```text
[0.12, -0.03, 0.87, ... 1536 values]
```

### Likely interview question

**How many dimensions does OpenAI `text-embedding-3-small` have?**

> The default embedding size is **1,536 dimensions**.

The embedding API also supports reducing output dimensionality with the `dimensions` parameter; reduced dimensions should be evaluated for the target retrieval task rather than assuming they will preserve identical quality.

## 3. What is magnitude?

Magnitude means the **length of a vector**.

For a simple vector:

```text
v = [3, 4]
```

its magnitude is:

```text
sqrt(3² + 4²) = 5
```

For an embedding with many dimensions, the same idea applies across all coordinates.

## 4. What is normalization?

Normalization means scaling a vector so its magnitude becomes 1 while keeping the same direction.

Example:

```text
[3, 4]
```

has magnitude 5. Divide each value by 5:

```text
[0.6, 0.8]
```

and the new magnitude is 1.

### Why normalize embeddings?

Cosine similarity is:

```text
A · B / (|A| × |B|)
```

If both vectors already have magnitude 1:

```text
A · B / (1 × 1)
= A · B
```

So for unit-normalized embeddings, dot product produces the same similarity value/ranking as cosine similarity.

### OpenAI embedding note

OpenAI's embedding FAQ states that its embeddings are normalized to length 1. For such normalized embeddings, cosine similarity and dot product give the same result for ranking. This allows a vector database configured for inner/dot product similarity to avoid separately computing vector norms for cosine similarity.

## 5. Cosine similarity vs dot product

### Cosine similarity

Measures similarity based on the angle/direction between vectors.

```text
same direction → high similarity
very different direction → lower similarity
```

### Dot product

Multiplies corresponding coordinates and sums them.

For normalized vectors, dot product and cosine similarity are equivalent for ranking.

### Interview answer

> "Our embedding vectors are normalized, so dot product can be used as an efficient equivalent to cosine similarity. The important requirement is that the query and document vectors use the same compatible embedding space and similarity configuration."

## 6. RAG query vs word-by-word embeddings

A typical RAG pipeline does **not** embed every word separately.

### Document side

```text
Document
 ↓
meaningful chunks
 ↓
embedding for each chunk
 ↓
store vectors
```

### Query side

```text
User question
 ↓
one query embedding
 ↓
compare against chunk embeddings
 ↓
top-K results
```

Example:

```text
Query:
"What was the company's Q4 revenue?"
```

The complete query is embedded as one input and compared with stored chunk vectors.

### Likely interview question

**Do you create embeddings word by word in RAG?**

> No. We normally embed meaningful document chunks and embed the user's complete query. We then perform similarity search between the query vector and the stored chunk vectors.

Keyword retrieval is different: it works with lexical terms/tokens rather than semantic vector similarity.

## 7. Vector search in the RAG pipeline

```text
Document
   ↓
Chunking
   ↓
Embedding
   ↓
Vector database
   ↓
Query embedding
   ↓
Similarity search
   ↓
Top-K chunks
```

The query and document chunks should be embedded with the same compatible model/configuration so they exist in the same vector space.

## 8. pgvector and project connection

Our `ai-platform` uses PostgreSQL with pgvector for vector retrieval.

Conceptually:

```text
PostgreSQL
 ├── documents
 ├── chunks
 ├── metadata
 └── embeddings
        ↓
     pgvector
```

This allows relational metadata and vector retrieval to work together.

## 9. Metadata filtering

Production retrieval often combines semantic similarity with metadata/permission constraints.

Example filters:

```text
tenant_id = tenant-123
document_type = financial_report
year = 2025
```

The important design principle is that authorization and tenant boundaries must constrain what can be retrieved; do not retrieve unauthorized content and only filter it after retrieval.

## 10. Vector search vs keyword search

### Vector search

```text
complete query
 ↓
embedding
 ↓
semantic similarity
```

Useful when meaning matters even if exact words differ.

### Keyword search

```text
query terms
 ↓
lexical matching
```

Useful for exact names, identifiers, rare terminology and phrase matching.

Hybrid retrieval combines both signals:

```text
Vector search
      +
Keyword search
      ↓
RRF
      ↓
Reranker
```

## 11. Top-K retrieval

We usually retrieve only a limited number of candidates rather than the entire corpus.

Example:

```text
10,000 chunks
      ↓
vector / keyword retrieval
      ↓
20 candidates
      ↓
reranker
      ↓
5 final chunks
```

This controls latency, cost and context size while allowing the reranker to work on a manageable candidate set.

## 12. Changing the embedding model

If the embedding model changes, the new vectors may not be compatible with the existing vector space/index.

Typical migration thinking:

```text
new embedding model
       ↓
re-embed corpus
       ↓
new/updated index
       ↓
re-evaluate retrieval
```

Do not assume vectors from unrelated embedding models can simply be mixed.

## 13. Debugging poor vector retrieval

Inspect the pipeline in order:

```text
1. parsing
2. chunking
3. query construction
4. query embedding
5. document embeddings
6. metadata/permission filters
7. similarity metric/configuration
8. top-K
9. hybrid retrieval
10. reranking
```

Then use an evaluation dataset to determine whether the issue is isolated or systematic.

## Likely interview questions

### What is an embedding?

> A numerical representation of text that captures semantic relationships so similar meanings can be compared in vector space.

### What does embedding dimension mean?

> The number of values in the vector representation.

### How many dimensions does `text-embedding-3-small` have?

> 1,536 by default.

### What is magnitude?

> The length/norm of a vector.

### What is normalization?

> Scaling a vector so its magnitude becomes 1 while preserving its direction.

### Why can dot product replace cosine similarity for normalized OpenAI embeddings?

> Because the vector magnitudes are 1, so the normalization terms in cosine similarity become 1 and the score reduces to the dot product.

### Do you embed every word separately in RAG?

> No. We normally embed meaningful document chunks and the complete user query, then compare the query vector against chunk vectors.

### Why use pgvector?

> It gives us vector similarity search inside PostgreSQL, while keeping document and metadata relationships in the same database system.

### Why use metadata filters with vector search?

> To restrict retrieval to the correct tenant, document set, permissions or other business constraints before returning candidates.

### What happens if you change the embedding model?

> I would normally re-embed the corpus in the new vector space, update/rebuild the index as needed, and re-evaluate retrieval quality.

## Project-based interview answer

**"Explain embeddings in your AI platform."**

> "We convert document chunks and the user's query into embeddings and use those vectors for semantic retrieval. In our AI platform, embeddings are stored alongside chunk and metadata information so retrieval can combine vector similarity with metadata constraints. The semantic candidates can then be combined with keyword results using RRF and optionally reranked before the most relevant context is sent to the LLM."

## Checklist

- [x] embedding definition
- [x] semantic similarity
- [x] vector dimensions
- [x] `text-embedding-3-small` default 1,536 dimensions
- [x] magnitude / norm
- [x] normalization
- [x] cosine similarity
- [x] dot product
- [x] normalized embeddings and dot-product equivalence
- [x] complete-query vs word-by-word embedding
- [x] vector databases
- [x] pgvector
- [x] metadata filtering
- [x] top-K retrieval
- [x] embedding model migration
- [x] debugging retrieval quality
