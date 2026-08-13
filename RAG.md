# RAG Pipeline

## Overview

Query → RetrievalService → Hybrid Retrieval → RRF → Nemotron Reranker → Context Builder → LLM → Answer + Sources

## Responsibilities

### Retrieval
- semantic vector search
- keyword search
- RRF fusion
- Nemotron reranking

### RAG
- retrieval orchestration
- context construction
- grounded prompt
- answer generation
- source attribution

## Context Format

SOURCE [1]
Document ID: ...
Page: ...
Chunk: ...

...

## Grounding Rules

- Answer only from supplied sources
- Do not invent information
- Say when evidence is insufficient
- Cite sources using [1], [2], ...

## Configuration

OPENAI_API_KEY
RAG_LLM_MODEL

## Example

uv run python -m examples.rag.rag_example

## Current Retrieval Defaults

candidate_top_k = 20
final_top_k = 5
min_similarity = 0.30