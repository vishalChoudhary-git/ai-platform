# Expense Notifications

## Responsibility

The Expense plugin decides **what** notification to send. The shared notification layer decides **how** to deliver it.

```text
ExpenseResolutionService
        ↓
ExpenseNotificationService
        ↓
EmailSender abstraction
        ↓
Mailtrap API / SDK
```

## Notification rules

The employee is notified for every completed expense decision.

The manager is notified when the decision requires manager visibility or action:

```text
approved
    → employee + manager

rejected
    → employee + manager

information_required + manager_decision
    → employee + manager

information_required + additional_information
    → employee only

information_required + additional_document
    → employee only
```

For `manager_decision`, the corresponding `ExpenseApproval(PENDING)` record is created separately by `ExpenseResolutionService`.

## Delivery behavior

Notification delivery happens **after the expense decision is committed**. A delivery failure must not roll back the persisted expense decision.

Recipient deliveries are attempted independently. One failed recipient must not prevent an attempt for the other recipient.

A configurable delay can be inserted between recipients for development/test provider rate limits:

```text
EMAIL_RECIPIENT_DELAY_SECONDS=1.1
```

## Provider configuration

The application uses the Mailtrap Python SDK/API for email delivery. No SMTP host, port, username, or password is required by the application.

```text
EMAIL_ENABLED=true
MAILTRAP_API_TOKEN=<provider token>
EMAIL_FROM_ADDRESS=no-reply@example.com
EMAIL_FROM_NAME="AI Platform"
```

Use a Mailtrap sandbox/test token for development and a production sending token for production. The application code uses the same `MailtrapEmailSender`; the environment/secret configuration determines which token is supplied.

## Production

`ENVIRONMENT=production` does not switch to SMTP. The sender remains Mailtrap API/SDK based. Production delivery therefore requires a production-capable Mailtrap sending token rather than sandbox credentials.

## Testing

Unit tests should verify:

- employee notification is always attempted
- manager notification is attempted for approved/rejected decisions
- manager notification is attempted for `manager_decision`
- manager is not notified for ordinary additional-information/document requests
- employee address is used for the employee message
- manager address is used for the manager message
- failure of one delivery does not prevent the second delivery attempt
