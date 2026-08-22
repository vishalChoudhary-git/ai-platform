# Expense Policy Processing

```text
Policy PDF
   ↓
Document ingestion
   ↓
Parsed chunks + embeddings
   ↓
Policy rule extraction
   ↓
Normalized PolicyRule[]
   ↓
Redis policy snapshot
   ↓
PUBLISHED
```

## Important boundaries

- Shared document ingestion owns parsing, chunking, and embeddings.
- Expense policy processing owns extracting domain-specific policy rules.
- PostgreSQL/pgvector remains the durable embedding/retrieval store.
- Redis stores the normalized policy snapshot for fast access.
- A published policy version is immutable.

## Cache identity

The policy cache is keyed by content checksum so that the same policy content maps to the same cached snapshot while a new policy version/content naturally receives a new key.

```text
expense:policy:{checksum}
```

## Startup warm-up

When the application starts, published Expense policies are eligible for cache warm-up. A Redis hit avoids reprocessing. A cache miss can trigger policy processing before the policy is used by the Expense Agent.

Startup warm-up failure is logged and does not prevent the platform from starting; the policy can be processed again when needed.

## Publication

A policy is not considered published simply because a PDF upload succeeded. Processing must successfully produce a normalized rule snapshot before the policy is marked `PUBLISHED`.

```text
UPLOADED
   ↓
PROCESSING
   ↓
normalized + validated rules
   ↓
PUBLISHED
```

If processing fails, the policy returns to its uploaded state and the failure is logged.
