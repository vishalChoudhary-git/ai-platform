# Expense API examples

These examples exercise the Expense Resolution domain API before agent orchestration is added.

## Endpoint

```text
POST /plugins/expenses
```

The endpoint accepts `multipart/form-data`:

- `expense`: JSON string containing the expense business context.
- `files`: one or more new supporting documents.

For follow-up submissions, pass the existing business ID:

```text
POST /plugins/expenses?expense_id=EXP-...
```

Only new information/documents need to be supplied. Existing documents remain associated with the expense.

## Prerequisites

1. Start the API locally.
2. Have at least one test PDF available, for example `hotel-receipt.pdf`.
3. Apply the current database migration locally:

```bash
uv run alembic upgrade head
```

## Scenario 1 — Normal hotel expense

Use the request in `scenarios/auto_approval.json` with `hotel-receipt.pdf`.

At the current domain-only milestone, the expected initial status is `submitted`. Later, the agent should be able to evaluate this type of request and auto-approve it when policy permits.

## Scenario 2 — Hotel exceeds the policy limit

Use the request in `scenarios/manager_review.json` with `hotel-over-limit.pdf`.

At the future agent milestone, the expected path is:

```text
SUBMITTED
  ↓
policy check
  ↓
INFORMATION_REQUIRED
required_action = MANAGER_DECISION
  ↓
ExpenseApproval(PENDING)
```

The manager will then approve or reject the approval request; the employee does not upload an approval email to self-approve the expense.

## Scenario 3 — Missing supporting document

Use the request in `scenarios/missing_document.json` without a file, or with only the documents you currently have.

The current API requires at least one new document when creating a new expense. Future agent behavior can use `INFORMATION_REQUIRED` when additional evidence is needed after submission.

## Scenario 4 — Multiple documents

Use `scenarios/multi_document.json` with:

```text
hotel-receipt.pdf
meal-receipt.pdf
taxi-receipt.pdf
```

The same expense should receive three `ExpenseDocument` associations.

## Follow-up to an existing expense

After creating an expense, copy its `expense_id` from the response and call the follow-up request in `append_expense.http`.

Example future scenario:

```text
EXP-2026-ABC123
  ↓
INFORMATION_REQUIRED
  ↓
user adds corrected receipt
  ↓
POST /plugins/expenses?expense_id=EXP-2026-ABC123
  ↓
new document is appended
  ↓
existing documents are not re-uploaded
```

## Postman

`postman_collection.json` contains the same create and follow-up requests with a `base_url` and `expense_id` collection variable.
