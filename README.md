Built and published an open-source Python package for intelligent document parsing with support for Docling, table extraction, metadata generation, and semantic chunking.

HTTP Request
    ↓
Pydantic Validation
    ↓
API
    ↓
Service
    ↓
Repository
    ↓
PostgreSQL
    ↓
Service
    ↓
Pydantic Response
    ↓
JSON Response
### Flow chart
                AI Knowledge Platform

                ┌──────────────────────┐
                │      React UI        │
                └──────────┬───────────┘
                           │
                           ▼
                    FastAPI Gateway
                           │
      ┌────────────────────┼─────────────────────┐
      ▼                    ▼                     ▼
  Authentication      Guardrails          Rate Limiter
                           │
                           ▼
                    LangGraph Runtime
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   Retriever          Tool Executor      Memory Manager
        │                  │                  │
        ▼                  ▼                  ▼
 Connector Manager   External Tools     Redis/Postgres
        │
        ▼
 Ingestion Pipeline
        │
        ▼
 PostgreSQL + pgvector

 ### ADR's
 ADR Roadmap
ADR	    Purpose
ADR-001	Platform Architecture
ADR-002	Plugin & Registry System
ADR-003	Knowledge Model & Database
ADR-004	LLM Gateway
ADR-005	Retrieval Engine
ADR-006	LangGraph Runtime
ADR-007	Guardrails
ADR-008	Observability & Evaluation