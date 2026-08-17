# ADR-0001: Expense Resolution Agent and Supporting Document Model

- **Status:** Accepted
- **Date:** 2026-08-17
- **Decision owners:** AI Platform project

## Context

The AI Platform already provides document upload, document intelligence, persistent knowledge, hybrid retrieval, reranking, RAG, and the Knowledge API. The next phase is intended to demonstrate genuine agentic behavior on top of those capabilities.

A simple document question-answering use case is not sufficient because it can already be handled by the existing RAG pipeline. The first agentic application must instead accept a business goal, investigate dynamically, use search and deterministic tools, make a decision, and either complete the task or advance it to a human.

Expense resolution was selected as the first domain workflow because a normal expense can potentially move from a multi-step manual approval process to an automated decision for compliant cases, while exceptions can still be escalated to a manager.

The initial solution should maximize reuse of the existing upload and knowledge infrastructure. We should not introduce web search, document downloading, market-data integrations, or other external discovery capabilities just to make the agent appear more autonomous.

## Decision

### 1. Build Expense Resolution as the first agentic application

The first agent receives the goal:

> Resolve this expense according to the applicable company policy.

The agent may reach one of three outcomes:

- `APPROVED`
- `REJECTED`
- `REVIEW_REQUIRED`

For approved or rejected requests, the system can complete the corresponding action. Requests requiring human judgment are escalated rather than forced into an automatic decision.

### 2. Use the uploaded expense documents as evidence, not as the complete business input

An expense submission contains structured business context supplied explicitly by the user. The receipt(s) and other supporting documents are evidence associated with that expense.

The system-generated `expense_id` is authoritative and is not supplied by the user.

The initial expense submission must explicitly provide:

- `employee_name`
- `employee_email`
- `manager_email`
- `category`
- `description`

The expense can reference one or more supporting documents. The initial implementation may exercise the one-document case, but the domain model must support multiple documents from the start.

Conceptually:

```text
Expense
  1 ──────── N
ExpenseDocument
             │
             └── document_id → existing Document system
```

We will use a generic `ExpenseDocument` association rather than a singular `receipt_document_id`. This supports future cases such as hotel, meal, taxi, flight, and other supporting documents without changing the core expense model.

`document_type` should not be required from the user in the initial API. The existing document pipeline provides the extracted evidence, and later the agent or classification layer may identify the document's role when needed.

### 3. Reconcile the user's claim with document evidence

The agent is not responsible for inventing missing business context from a receipt. Instead, it should use documents to verify and enrich the submitted claim where appropriate.

For example:

```text
User claim
  category = hotel
  amount   = 12,500

Receipt evidence
  merchant = ABC Hotel
  amount   = 12,500
  date     = 2026-08-15

Agent
  → verify consistency
  → continue policy investigation
```

If an important value is missing or conflicting, the agent must not silently guess. It should identify the missing or conflicting information and move the expense into an information-required or review path as appropriate.

This completeness/reconciliation step is part of the agent behavior rather than a reason to add another pre-agent workflow.

### 4. Reuse the existing Knowledge/RAG stack as an agent tool

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

The agent can invoke a knowledge-search capability to answer questions such as:

- Which expense policy applies?
- What is the reimbursement limit for this category?
- Is an exception policy available?
- What approval threshold applies?

The agent treats retrieval as an evidence/tool capability rather than as the final application itself.

### 5. Keep deterministic rules and actions outside the LLM

The LLM is responsible for interpretation, planning, tool selection, and synthesis. Deterministic operations remain application code or tools.

Examples include:

```text
check_expense_limit()
validate_receipt_presence()
validate_claim_against_evidence()
calculate_threshold()
send_email()
update_expense_status()
```

The LLM should not perform authoritative arithmetic or encode business rules solely inside prompts.

### 6. Start with a single agent; do not force multi-agent architecture

The initial Expense Resolution workflow will use one agent with tools.

A multi-agent architecture is intentionally rejected for the first milestone because the candidate responsibilities do not yet justify independent agents. Splitting policy lookup, validation, decision, and notification into separate agents would add coordination and LLM overhead without providing a demonstrated architectural benefit.

Additional agents may be introduced later only when a genuinely distinct reasoning domain or workflow requires independent specialization.

### 7. Introduce LangGraph only when stateful orchestration is justified

LangGraph is not a mandatory dependency simply because the project is agentic.

It becomes justified when the real workflow demonstrates requirements such as:

- persistent agent state
- conditional routing
- repeated investigation/tool loops
- retry or recovery
- human-in-the-loop checkpoints
- resumable execution

The initial agent should first establish the real tool-selection and investigation behavior. The implementation can then adopt LangGraph when it solves an observed orchestration problem.

LangChain remains optional and may be used where its LLM/tool/structured-output abstractions provide value, without replacing the platform's existing retrieval and RAG abstractions.

### 8. Email is an action, not another reasoning layer

The agent may select an email action after determining the expense outcome.

Examples:

```text
APPROVED
  → update status
  → notify relevant recipients

REJECTED
  → update status
  → notify employee

REVIEW_REQUIRED
  → notify manager with evidence and reason
```

`send_email()` remains a deterministic action tool. The agent decides whether the action is needed and which outcome it represents; the email integration performs the delivery.

### 9. Duplicate detection is a later enhancement

Duplicate expense detection is considered useful, but it is not required for the first milestone. It should not delay the core agent loop.

## Target workflow

The intended first workflow is:

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
                       ┌─────────────────┼─────────────────┐
                       ↓                 ↓                 ↓
                    APPROVED         REJECTED       REVIEW_REQUIRED
                       │                 │                 │
                       └─────────────────┼─────────────────┘
                                         ↓
                                       Action
                                         ↓
                                  status + email
```

The important agentic property is that the next step is not completely predetermined. The agent can choose another search or tool based on what it learns from intermediate results.

## Initial tool boundary

The minimum useful tool set is intentionally small:

```text
search_knowledge()
validate_expense_data()
check_expense_policy()
send_email()
```

A `request_missing_information()` capability may be added as the interaction model is defined. Duplicate detection is a later enhancement.

## Consequences

### Positive

- Reuses the existing upload, document intelligence, retrieval, reranking, RAG, and Knowledge layers.
- Demonstrates agentic behavior through investigation, tool selection, decision-making, and action.
- Avoids unnecessary web-search/download infrastructure in the first milestone.
- Supports one-to-many expense documents without coupling the model to a single receipt.
- Keeps financial/business rules deterministic and auditable.
- Keeps multi-agent and LangGraph complexity optional until justified.
- Enables measurable reduction in human approval work for straightforward expenses.

### Negative / trade-offs

- The agent must handle incomplete and conflicting information explicitly.
- The initial system will require a controlled policy corpus to make meaningful approval decisions.
- Email and status updates introduce external side effects that require careful failure handling and observability.
- A single-agent design may need to evolve if the domain later introduces distinct specialist workflows.

## Out of scope for the first milestone

- Web search
- External financial/market data
- Downloading external documents on behalf of the agent
- Multi-agent orchestration
- Automatic duplicate detection
- Complex enterprise identity/authorization integrations
- Building a full frontend before the backend workflow is proven

## Success criteria for the first implementation

A first end-to-end milestone is successful when the system can:

1. Accept an expense submission with one supporting document.
2. Generate the `expense_id` server-side.
3. Associate the expense with one or more document records through an `ExpenseDocument` relationship.
4. Use the existing Knowledge/RAG capability to investigate applicable policy.
5. Detect missing or conflicting information rather than guessing.
6. Perform at least one deterministic validation/calculation.
7. Produce `APPROVED`, `REJECTED`, or `REVIEW_REQUIRED`.
8. Update the expense status and execute the appropriate email action.
9. Preserve evidence/citations for the decision.
10. Log the agent's investigation/tool path sufficiently for debugging and evaluation.
