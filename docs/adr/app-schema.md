Responsibilities
core/

Platform infrastructure.

Examples:

FastAPI lifecycle
PostgreSQL
SQLAlchemy
Registry
LLM abstraction
Embeddings
Generic ingestion
Chunking
Retrieval
Memory

Never contains Finance, GitHub, HR, etc.

features/

Business capabilities of the platform.

Example:

knowledge_base

owns

KnowledgeAsset
Document
Chunk
CRUD
Search
Citations

Later

chat

owns

ChatSession
Message
Conversation history
extensions/

Responsible for bringing external knowledge into the platform.

Examples:

Upload

Receive PDF
↓

RawDocument

Finance

Download SEC filing
↓

RawDocument

GitHub

Clone repository
↓

RawDocument

Extensions never:

Create database tables
Store embeddings
Talk to PostgreSQL
Chunk documents

They only acquire data and optionally enrich it with domain-specific metadata.