# ADR-001: AI Knowledge Platform Architecture

## Status

Accepted

---

## Context

The goal is to build a production-ready AI platform rather than a single-purpose RAG chatbot.

The platform should support multiple domains such as Finance, HR, Legal, GitHub, Notion and future integrations without changing the core application.

---
## Core Rule
The Core Platform owns infrastructure. Extensions own business knowledge.
The system will follow a **Plugin Architecture**.

# Core owns
    FastAPI
    PostgreSQL
    pgvector
    LangGraph runtime
    Memory
    LLM Gateway
    Retrieval
    Guardrails
    Registry
    Ingestion Pipeline
# Extension owns
    Finance connector
    GitHub connector
    Notion connector
    HR prompts
    Legal tools
    Domain-specific metadata
---

## Principles

- Core must not know about Finance, HR or Legal.
- Plugins depend on the Core.
- Core never depends on Plugins.
- Every plugin follows the same lifecycle.
- Everything is asynchronous.
- Everything is replaceable through interfaces.

---

## High-Level Architecture

Client

↓

FastAPI

↓

Guardrails

↓

LangGraph Runtime

↓

Retriever / Tools

↓

LLM Gateway

↓

Knowledge Store

↓

PostgreSQL + pgvector

---

## Domain Model

KnowledgeAsset

↓

Document

↓

DocumentChunk

↓

Embedding

---

## Plugin Model

Plugin

↓

Connector

↓

Parser

↓

Tools

↓

Prompts

↓

Metadata Extractor

---

## Core Modules

- API
- Registry
- Connectors
- Retrieval
- Embeddings
- LLM
- Memory
- Guardrails
- Observability

---

## Benefits

- Extensible
- Domain Independent
- Easy to maintain
- Easy to test
- Supports future connectors
- Supports multiple LLM providers

---

## Consequences

Adding a new domain should require creating a new plugin only.

No changes should be required in the Core Platform.

