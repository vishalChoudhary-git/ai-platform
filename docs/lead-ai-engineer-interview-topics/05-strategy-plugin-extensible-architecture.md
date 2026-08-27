# Topic 5 — Strategy / Plugin Pattern & Extensible Architecture

**Status:** Complete

## Focus
ABC interfaces, strategy implementations, provider registries, factory selection, Open/Closed Principle and plugin-style architecture for parsers/providers.

## Completed
- Strategy pattern
- interchangeable implementations behind a common contract
- provider selection
- registry/factory concepts
- Open/Closed Principle
- project example: `BaseParser` → parser implementations
- project example: `Reranker` → reranking implementations

## Project example: `ai-document-intelligence`

The SDK defines a `BaseParser` abstraction with a common `parse()` contract. Concrete parsers such as `LiteParseParser` and `LlamaParseParser` implement that contract, while the higher-level `DocumentParser` selects the appropriate implementation based on parser tier.

```text
                 BaseParser
                     ↓
          ┌──────────┴──────────┐
          ↓                     ↓
   LiteParseParser       LlamaParseParser
          ↓                     ↓
      LiteParse             LlamaParse
```

The caller can work with the common behavior:

```python
parser.parse(source)
```

without needing to know the provider-specific parsing details.

## Project example: `ai-platform` reranker

`Reranker` is an abstraction for reranking behavior. The retrieval service depends on the contract, while a concrete implementation can use a particular model/provider.

```text
Reranker
   ↓
OpenRouter/Nemotron implementation
   ↓
future implementation(s)
```

This is a useful strategy boundary because the reranking implementation can change without changing retrieval orchestration.

## Strategy vs Factory

```text
Strategy
    → encapsulates interchangeable behavior

Factory
    → encapsulates object creation/selection
```

A single class can contain both concerns, but they are conceptually different.

## Open/Closed Principle

> Software entities should be open for extension but closed for modification.

In practice for our architecture: adding another parser or reranker implementation should ideally not require rewriting the orchestration workflow.

## Registry pattern

A simple provider registry can keep selection logic centralized:

```python
PARSERS = {
    "free": LiteParseParser,
    "premium": LlamaParseParser,
}
```

The registry becomes increasingly useful as the number of implementations grows.

## Interview questions

### Tell me about a Strategy pattern you used.

> "In our document-intelligence SDK, parsers share a `BaseParser` contract while LiteParse and LlamaParse are interchangeable implementations. In the AI platform we use a similar boundary for reranking, where retrieval depends on `Reranker` rather than one specific model/provider."

### Why not call the provider directly?

> Direct provider coupling spreads vendor-specific code through the application and makes replacement/testing harder. The abstraction keeps orchestration independent of the concrete implementation.

### What happens when you add a third implementation?

> Add the new implementation behind the existing contract and extend the selection/registration mechanism. The consuming workflow should remain unchanged.

### Strategy vs Repository?

> Repository abstracts data access/persistence. Strategy abstracts interchangeable behavior or algorithms.

### Should every class have an interface?

> No. Add abstractions where there is a meaningful boundary, implementation variation, or testing/replacement need. Over-abstraction increases complexity.

## Checklist

- [x] Strategy pattern
- [x] common contract
- [x] provider selection
- [x] registry/factory concepts
- [x] Open/Closed Principle
- [x] parser strategy example
- [x] reranker strategy example
- [x] Strategy vs Factory
- [x] Strategy vs Repository
