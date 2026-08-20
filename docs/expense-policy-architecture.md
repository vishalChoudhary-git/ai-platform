# Expense Policy Architecture

## Goal

Expense policy is authoritative business logic used by the Expense Agent. It must not be silently modified by the agent, normal users, or ordinary document updates.

## Policy identity

A policy is a versioned business artifact, not a mutable text blob.

Conceptually:

```text
Policy
├── policy_id
├── policy_name
└── versions[]
     ├── version
     ├── document_id
     ├── checksum
     ├── effective_from
     ├── effective_to
     ├── status
     ├── published_at
     └── published_by
```

A policy version points to an existing immutable `Document`.

## Immutability rule

Once a policy version is published:

- its source document cannot be replaced in place;
- its checksum cannot change;
- its parsed/normalized policy content cannot be edited in place;
- its effective dates cannot be changed in place;
- the agent has read-only access to published policy versions.

A policy change creates a **new version**.

Example:

```text
Hotel Policy v1
₹15,000 limit

        ↓ new policy publication

Hotel Policy v2
₹18,000 limit
```

Existing decisions remain explainable because they can retain the policy version/evidence used during evaluation.

## Who can change policy?

Only a future privileged policy-management workflow should be allowed to publish a new policy version. This is outside the Expense Agent.

The Expense Agent must never have tools such as:

```text
create_policy
update_policy
delete_policy
edit_policy
```

It should only be able to query published policy versions.

## Policy parsing flow

The source policy is still a document and should use the existing document platform:

```text
Policy PDF
   ↓
DocumentService / Document Intelligence
   ↓
Parsed document
   ↓
Policy normalization / chunking
   ↓
Knowledge / retrieval index
   ↓
Expense Agent policy-search tool
```

The policy source document and the parsed/indexed representation are both derived artifacts of the same immutable published version.

## Effective-date selection

When evaluating an expense, the policy lookup must eventually consider the expense date:

```text
expense.expense_date
        ↓
find published policy version effective on that date
        ↓
search only that policy version
```

This prevents a newer policy from being incorrectly applied to an older expense.

## Evidence retention

When an agent reaches a decision, the decision context should retain enough information to identify the exact policy version and retrieved evidence used.

Example:

```json
{
  "policy_id": "travel-expense",
  "policy_version": "2",
  "policy_document_id": "...",
  "policy_page": 5,
  "rule": "hotel_limit",
  "allowed_limit": 15000,
  "claimed_amount": 25000
}
```

This supports auditability and lets a later agent run resume from the unresolved rule rather than blindly searching every historical document.

## Expense-document parsing

The same principle applies to expense evidence:

```text
Expense submission
  + receipt PDF(s)
       ↓
DocumentService
       ↓
Document Intelligence
       ↓
Parsed document
       ↓
structured evidence / chunks
       ↓
Expense Agent
```

The agent should not assume receipt values are available until parsing has completed successfully.

## Testing requirement

Before testing meaningful approval/review behavior, we need at least two parsed document classes:

1. **Company policy document** — contains rules such as hotel limits and manager-approval thresholds.
2. **Expense document** — contains receipt evidence such as merchant, date, amount, and category-supporting text.

The first real end-to-end test should therefore be:

```text
Published policy PDF
        ↓
parsed/indexed policy

Expense receipt PDF
        ↓
parsed expense evidence

Expense Agent
        ↓
policy search + evidence reconciliation
        ↓
AgentDecision
```

## Out of scope here

The initial Agent Foundation does not implement the policy-management UI, privileged publication workflow, or policy database tables. This document defines the boundary those later components must preserve.
