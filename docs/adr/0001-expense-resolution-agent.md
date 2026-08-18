# ADR-0001: Expense Resolution Agent and Supporting Document Model

- **Status:** Accepted
- **Date:** 2026-08-18
- **Decision owners:** AI Platform project

## Context

The AI Platform already provides document upload, document intelligence, persistent knowledge, hybrid retrieval, reranking, RAG, and the Knowledge API. The next phase is intended to demonstrate genuine agentic behavior on top of those capabilities.

A simple document question-answering use case is not sufficient because it can already be handled by the existing RAG pipeline. The first agentic application must instead accept a business goal, investigate dynamically, use search and deterministic tools, make a decision, and either complete the task or advance it to the appropriate human.

Expense resolution was selected because straightforward expenses can potentially be resolved automatically while exceptions can be advanced to a manager without forcing the employee to perform another manual approval step.

The initial solution should maximize reuse of the existing upload and knowledge infrastructure. We should not introduce web search, external financial data, document downloading, or other external discovery capabilities just to make the agent appear more autonomous.

## Decisions

### 1. Expense Resolution is the first agentic application

The agent receives the goal:

> Resolve this expense according to the applicable company policy.

The expense lifecycle is intentionally small:

- `SUBMITTED`
- `INFORMATION_REQUIRED`
- `APPROVED`

`INFORMATION_REQUIRED` means the agent cannot complete the expense autonomously and has identified a required next step. Examples include additional information, an additional document, or a manager decision.

The expense itself does not use `REJECTED` as an agent outcome. When manager intervention is needed, the manager owns the final approve/reject decision through an approval workflow. A manager rejection is represented by the approval record; the expense workflow can retain the unresolved/terminal state as the product policy evolves.

### 2. Use a dedicated Expenses plugin; reserve Finance for investment capabilities

Expense Resolution is a business workflow plugin, not the investment/financial-analysis domain. The code belongs under:

```text
app/plugins/expenses/
```

A future `app/plugins/finance/` namespace remains available for investment and financial-analysis capabilities.

### 3. One user-facing API supports both new expenses and follow-up submissions

The primary endpoint is:

```http
POST /plugins/expenses
```

For a new expense, the request contains structured expense metadata plus one or more new supporting files.

For a follow-up to an existing expense, the same endpoint accepts an optional:

```text
?expense_id=EXP-...
```

The follow-up attaches only newly supplied information/documents to the existing expense. Existing documents are not uploaded again.

The client does not submit `expense_id` when creating an expense; the system generates it.

### 4. Separate business context from document evidence

The user explicitly supplies business context that a receipt cannot be relied upon to contain:

- `employee_name`
- `employee_email`
- `manager_email`
- `category`
- `description`

`amount`, `currency`, and `expense_date` may be supplied when known. Supporting documents remain evidence that the agent can later reconcile with the claim.

A receipt/document must not be treated as the authoritative source for employee identity, manager routing, category, or business purpose.

### 5. Support multiple supporting documents from day one

An expense may have one or many supporting documents:

```text
Expense
  1 ──────── N
ExpenseDocument
             │
             └── document_id → existing Document system
```

The initial implementation may exercise one document, but the domain model supports hotel receipts, meals, taxi receipts, flight documents, and other supporting evidence without changing the core expense model.

`ExpenseDocument` uses a generic document role such as `RECEIPT` or `SUPPORTING`. Manager approval is not modeled as an approval-role document; it is a workflow entity.

### 6. Manager approval is a first-class workflow entity

When an expense requires a manager decision, the system creates an `ExpenseApproval` record:

```text
Expense
  │
  └── ExpenseApproval
       ├── approver_email
       ├── status: PENDING / APPROVED / REJECTED
       ├── reason
       ├── requested_at
       └── resolved_at
```

The manager is responsible for the approve/reject decision. The employee does not upload an approval email to self-approve the expense.

The expense workflow can therefore represent:

```text
Hotel amount exceeds policy limit
        ↓
INFORMATION_REQUIRED
        ↓
required_action = MANAGER_DECISION
        ↓
create pending manager approval
        ↓
notify manager
        ↓
wait
        ↓
manager APPROVED / REJECTED
```

A later phase may expose explicit manager decision APIs/UI and resume the expense workflow from this persisted checkpoint.

### 7. Persist decision context for resumable investigation

The expense stores the latest decision context:

```text
decision_reason
required_action
decision_evidence (JSONB)
```

Example:

```json
{
  "policy_document_id": "...",
  "policy_page": 5,
  "rule": "hotel_limit",
  "allowed_limit": 15000,
  "claimed_amount": 25000
}
```

This allows a later agent run to focus on the unresolved requirement instead of blindly re-evaluating the entire historical document set.

New evidence must still be validated against the unresolved requirement. For example, if the stored requirement is `MANAGER_DECISION`, the resumed workflow verifies the manager decision and then continues.

### 8. Reuse the existing Document service and ingestion pipeline

The Expenses plugin must not call the existing `/documents/upload` HTTP endpoint internally. It should reuse the existing application services directly:

```text
Expense API
   ↓
ExpenseService
   ├── DocumentService.ingest()
   └── IngestionService.process_document()
```

The existing document platform remains responsible for checksum-based identity, storage, document records, and asynchronous processing.

### 9. Reuse Knowledge/RAG as an agent capability

The agent does not implement its own retrieval system.

The existing stack remains responsible for:

```text
Document Intelligence
        ↓
Persistent Knowledge
        ↓
Hybrid Retrieval
        ↓
Reranking
        ↓
RAG / Knowledge API
```

The future Expense Agent will consume a knowledge-search capability to investigate policies and rules.

### 10. Keep deterministic rules and actions outside the LLM

The LLM is responsible for interpretation, planning, tool selection, and synthesis. Deterministic operations remain application code or tools.

Examples include:

```text
validate_expense_data()
check_expense_policy()
calculate_threshold()
update_expense_status()
send_email()
```

The LLM should not perform authoritative arithmetic or encode business rules solely in prompts.

### 11. Start with a single agent; do not force multi-agent architecture

The initial Expense Resolution workflow will use one agent with tools.

A multi-agent architecture is intentionally deferred because the candidate responsibilities do not yet justify independent agents. Additional agents may be introduced only when a genuinely distinct reasoning domain or workflow requires independent specialization.

### 12. Introduce LangGraph only when stateful orchestration is justified

LangGraph is not a mandatory dependency simply because the project is agentic.

It becomes justified when the real workflow demonstrates requirements such as:

- persistent agent state
- conditional routing
- repeated investigation/tool loops
- retry or recovery
- human-in-the-loop checkpoints
- resumable execution

The current domain model is intentionally designed to support those future requirements through persisted decision context and approval state.

LangChain remains optional and may be used where its LLM/tool/structured-output abstractions provide value, without replacing the platform's existing retrieval/RAG abstractions.

### 13. Email is an action, not another reasoning layer

When the agent or workflow determines that a human action is required, email will be a deterministic action tool/provider. The provider remains replaceable; Ethereal, Mailpit, Resend, or another provider can be selected later.

### 14. Duplicate detection is a later enhancement

Duplicate expense detection is useful but is not required for the first milestone and should not delay the core agent loop.

## Target workflow

```text
User submits expense + supporting document(s)
                    ↓
             Expense Agent
                    ↓
        Build / validate expense context
                    ↓
          Do I have enough information?
              /                 \
            NO                   YES
            ↓                     ↓
     identify missing       search applicable
       information              policy
                                  ↓
                         validate / calculate
                                  ↓
                       need more investigation?
                           /             \
                         YES             NO
                         ↓                ↓
                   search/tool        decision
                                         ↓
                              ┌──────────┴──────────┐
                              ↓                     ↓
                      INFORMATION_REQUIRED     APPROVED
                              ↓
                       required_action
                              │
             ┌────────────────┼────────────────┐
             ↓                ↓                ↓
      ADDITIONAL_INFO   ADDITIONAL_DOC   MANAGER_DECISION
                                               ↓
                                        ExpenseApproval
                                               ↓
                                            wait/resume
```

The important agentic property is that the next step is not completely predetermined. The agent can choose another search or tool based on intermediate results and persist the unresolved requirement for later continuation.

## Initial domain boundary

The minimum useful domain model consists of:

```text
Expense
ExpenseDocument
ExpenseApproval
```

The first submission API intentionally focuses on domain persistence and document association. Agent orchestration, email execution, and manager decision APIs are subsequent milestones.

## Consequences

### Positive

- Reuses the existing upload, document intelligence, retrieval, reranking, RAG, and Knowledge layers.
- Provides a clean domain boundary for Expense Resolution.
- Supports one-to-many documents from day one.
- Supports follow-up documents without re-uploading existing documents.
- Persists the unresolved decision context required for resumable agentic workflows.
- Gives manager approval a first-class workflow representation.
- Keeps financial/business rules deterministic and auditable.
- Avoids unnecessary web-search/download infrastructure.
- Keeps multi-agent and LangGraph complexity optional until justified.

### Negative / trade-offs

- Follow-up processing requires careful state-transition rules.
- Persisted decision evidence introduces a second source of context that must remain consistent with the current policy corpus.
- Email and approval actions introduce external side effects that require idempotency and observability when implemented.

## Out of scope for the first milestone

- Expense Agent implementation
- LangGraph
- Multi-agent orchestration
- Email provider integration
- Duplicate detection
- Web search
- External financial/market data
- External document downloading
- Complex enterprise identity/authorization integrations
- Full frontend approval workflow

## Success criteria for the domain foundation

1. Accept a new expense and one or more new supporting files in one API request.
2. Generate the `expense_id` server-side.
3. Persist one-to-many `ExpenseDocument` associations.
4. Allow the same endpoint to append new documents to an existing expense via optional `expense_id`.
5. Preserve existing platform documents without re-uploading them.
6. Persist expense status, decision reason, required action, and evidence context.
7. Persist manager approval state independently from supporting documents.
8. Keep existing Document Intelligence and Knowledge/RAG boundaries intact.
