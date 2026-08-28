# Topic 12 — Chunking Strategies & Document Intelligence

**Status:** Complete

## Focus
Document parsing, normalized document representations, fixed-size, semantic and structure-aware chunking; headings, tables, overlap, metadata, provenance and chunk quality evaluation.

## Interview outcomes
Choose parsing and chunking strategies based on document type and retrieval goals, and explain their impact on recall, noise, cost and downstream RAG quality.

## 1. What is document parsing?

**Simple definition:** Document parsing is the process of taking an input document such as a PDF and converting it into structured, machine-readable information that downstream components can work with.

```text
PDF / DOCX
   ↓
Parser
   ↓
Structured document
   ↓
Chunking
   ↓
Embedding
```

Parsing answers: **What content and structure are present in the document?**

Chunking answers: **How should that content be divided into retrieval units?**

## 2. What should parsing preserve?

For RAG, preserve useful information such as:

- text/content
- headings and sections
- paragraphs/elements
- tables and their relationships
- page information
- document/source metadata
- provenance

A poor parser can lose reading order, table structure, headings or text. Once information is destroyed during parsing, retrieval cannot reliably recover it later.

## 3. Reading order

PDFs are visually laid out, but extracted text does not always follow human reading order, especially with multi-column documents. Correct reading order matters because it affects chunk quality and downstream retrieval.

## 4. Tables

Tables are especially important for financial and structured documents.

```text
| Year | Revenue | Expenses |
|------|---------|----------|
| 2024 | $20M    | $10M     |
| 2025 | $25M    | $12M     |
```

A good pipeline should preserve the relationship between headers, rows and values instead of flattening the table into ambiguous text.

**Key interview point:** Better retrieval cannot compensate for information that was destroyed during parsing.

## 5. Parsing abstraction and normalization

The SDK uses a parser abstraction so different parser implementations/providers can be used behind a common contract.

```text
Document
   ↓
Parser abstraction
   ├── lightweight parser
   └── advanced parser
   ↓
ParsedDocument
   ↓
Chunker
```

Different parser outputs should be normalized into a consistent representation so downstream chunking and embedding logic does not depend on provider-specific formats.

## 6. Chunking

**Simple definition:** Chunking is the process of splitting a document into smaller pieces that can be embedded, stored, retrieved, and passed to the LLM as context.

```text
Document
   ↓
Parse
   ↓
Chunk
   ↓
Embed
   ↓
Store
```

**Key idea:** Chunking is a retrieval optimization problem, not just a text-splitting problem.

## 7. Fixed-size chunking

Split content by a fixed number of tokens, words or characters.

Example:

```text
chunk size = 500 tokens
overlap = 50 tokens
```

Advantages: simple, predictable and fast.

Limitations: can split semantic units, headings, paragraphs or tables arbitrarily.

## 8. Semantic chunking

Split around meaningful semantic boundaries rather than only a fixed size.

```text
Fixed-size
→ split by size

Semantic
→ split by meaning
```

Semantic chunking can preserve related content better, but it may be more computationally complex and less deterministic than simple fixed-size splitting.

## 9. Structure-aware chunking

Use document structure such as:

- headings
- sections/subsections
- paragraphs
- page boundaries
- document elements

Example:

```text
Financial Results
   ├── Revenue
   ├── Expenses
   └── Cash Flow
```

A chunk can retain section context instead of treating the document as an undifferentiated string.

## 10. Table-aware chunking

For tables, preserving the logical relationship between header, row, column and value is usually more important than blindly applying token-based splitting.

For a very large table, a system may still need to split it, but it should preserve enough schema/header context so row values remain meaningful.

## 11. Overlap

Overlap is **separate from the chunking strategy**.

```text
Question 1: How do I decide where to split?
→ fixed / semantic / structure-aware / table-aware

Question 2: Do I repeat neighboring content?
→ overlap / no overlap
```

Semantic, structure-aware and table-aware chunking do **not** inherently require overlap. Overlap can be added when evaluation shows boundary context is being lost.

Trade-off:

```text
More overlap
   ↓
more chunks
   ↓
more embeddings/storage
   ↓
more redundancy/noise/cost
```

## 12. Metadata and provenance

A retrieval chunk should carry useful metadata such as:

```python
{
    "document_id": "annual-report-2025",
    "page_number": 42,
    "section": "Financial Results",
    "chunk_index": 17,
    "text": "Revenue increased...",
}
```

Metadata supports:

- citations/source attribution
- document and page identification
- metadata/permission filtering
- debugging retrieval
- auditing and traceability

## 13. Parent-child chunking

An advanced strategy is to store smaller child chunks linked to a larger parent context.

```text
Document
   ↓
Parent chunk
   ↓
Child chunks
```

Retrieve a precise child chunk, then use the parent to provide broader context.

The goal is to balance **retrieval precision** with **sufficient context**.

## 14. Choosing chunk size

There is no universal magic number such as 512 tokens.

A strong interview answer:

> Chunk size and overlap are tunable retrieval parameters. I would benchmark several configurations on representative queries and compare retrieval quality, downstream answer quality, latency and cost.

## 15. Choosing a strategy by document type

| Document type | Reasonable starting approach |
|---|---|
| Simple prose | Fixed-size may be sufficient |
| Markdown / structured text | Structure-aware |
| Financial reports | Structure-aware + table-aware |
| Legal documents | Sections/clauses/headings |
| FAQs | Keep question + answer together |
| Code | Function/class boundaries |

The strategy should be driven by document structure and retrieval requirements.

## 16. Document intelligence is more than chunking

A document-intelligence pipeline can include:

```text
Document
   ↓
Parsing
   ↓
Structure detection / normalization
   ↓
Metadata extraction
   ↓
Chunking
   ↓
Embedding
```

It is not simply `text.split()`.

## 17. Project connection — our SDK

Our SDK work includes PDF parsing, semantic Markdown chunking, structured metadata extraction and embedding generation. It also uses pluggable parser/embedding-provider architecture, multi-page document handling, table-aware chunking and deterministic chunk IDs.

The project design separates parser responsibilities from downstream chunking so the chunker can work with a normalized parsed representation.

## 18. High-value interview questions

### Tell me about chunking in your AI system.

> In our document-intelligence pipeline, parsing and chunking are separate stages. We first normalize the document into a structured representation, then generate retrieval-oriented chunks while preserving metadata such as document and page context. For structured documents, we take headings and tables into account rather than relying only on fixed-size splitting. Chunk size and overlap are tunable parameters, and I'd validate them against retrieval and end-to-end evaluation rather than assuming one universal configuration.

### Why did you separate parsing and chunking?

> Parsing extracts and normalizes document structure, while chunking decides how that structured content should be divided into retrieval units. Separating them lets us change the chunking strategy without changing the parser and lets the chunker operate on a standardized document representation.

### Why use a parser abstraction?

> We want the document pipeline to remain independent of a specific parsing implementation/provider. Different parsers have different capabilities and trade-offs, so we normalize their output into a common representation for downstream stages.

### Why semantic or structure-aware chunking over fixed-size?

> Because meaningful boundaries can preserve related information better and reduce cases where an important idea is split arbitrarily.

### Why table-aware chunking?

> Tables contain relationships between headers, rows and values. Naive text extraction can destroy those relationships, which can directly hurt retrieval and answer quality.

### Do semantic/structure-aware chunks require overlap?

> No. Overlap is an independent design choice. I'd add overlap when evaluation shows boundary context is being lost, while avoiding unnecessary redundancy.

### Why preserve page metadata?

> For source attribution, citations, filtering, debugging and traceability.

### What happens if chunks are too small?

> We can lose necessary context, create fragmented evidence and increase the number of retrieval units.

### What happens if chunks are too large?

> We increase noise, prompt size, token cost and latency, and retrieval becomes less precise.

### How would you choose chunk size?

> Empirically, by testing representative configurations and measuring retrieval metrics, downstream answer quality, latency and cost.

### How would you debug poor RAG caused by chunking?

> Inspect parser output first, then chunk boundaries, metadata/provenance and retrieval results. I would compare configurations using a representative evaluation set rather than judging chunk quality only by manually inspecting a few examples.

### Why can't retrieval fix bad parsing?

> If parsing destroyed table structure, reading order or source content, the downstream retriever has no reliable representation of the information that was lost.

## 19. Mental model

```text
             Document
                 ↓
               Parser
                 ↓
       Structured representation
                 ↓
         Metadata / provenance
                 ↓
        Chunking strategy
        ┌────────┼────────────┐
        ↓        ↓            ↓
      Fixed   Semantic   Structure-aware
                              +
                         Table-aware
                 ↓
              Chunks
                 ↓
             Embeddings
```

## Checklist

- [x] document parsing
- [x] parser abstraction
- [x] normalized parsed representation
- [x] reading order
- [x] table handling
- [x] fixed-size chunking
- [x] semantic chunking
- [x] structure-aware chunking
- [x] table-aware chunking
- [x] overlap as independent parameter
- [x] metadata/provenance
- [x] parent-child chunking
- [x] chunk-size trade-offs
- [x] chunking evaluation
- [x] project-based interview questions
