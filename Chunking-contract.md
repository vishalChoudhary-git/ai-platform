Chunk
├── id: str
├── text: str
└── metadata: ChunkMetadata

ChunkMetadata
├── page_number: int
├── section: str | None
├── heading: str | None
└── element_type: ElementType


Frontend
    │
    ▼
FastAPI

    │
    ├───────────────┐
    ▼               ▼

PostgreSQL       Cloudflare R2
(pgvector)       (PDF Storage)

    ▲
    │

Embedding Service

    ▲
    │

ChunkService

    ▲
    │

AI Document Intelligence SDK
(Docling)

    ▲
    │

PDF Upload
