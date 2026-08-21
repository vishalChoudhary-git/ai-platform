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
SMTP transport
```

## Notification rule

Every completed Expense decision sends a notification request to both:

```text
employee_email
manager_email
```

This is independent of the expense status.

### Approved

The employee is informed that the expense was approved. The manager is informed of the evaluated result; no approval action is required.

### Information required / manager decision

The employee is informed that additional review is required. The manager is informed that a manager decision is required.

The corresponding `ExpenseApproval` record is created separately by `ExpenseResolutionService` and is not created for ordinary approved expenses.

## Delivery behavior

Notification delivery happens **after the expense decision is committed**. A delivery failure must not roll back the persisted expense decision.

The two recipient messages are sent independently. One failed recipient must not prevent an attempt for the other recipient.

## Development configuration

The current development transport is generic SMTP and can be pointed at a sandbox such as Mailtrap.

```text
EMAIL_ENABLED=true
EMAIL_SMTP_HOST=sandbox.smtp.mailtrap.io
EMAIL_SMTP_PORT=2525
EMAIL_SMTP_USERNAME=<sandbox username>
EMAIL_SMTP_PASSWORD=<sandbox password>
EMAIL_SMTP_USE_TLS=true
EMAIL_FROM_ADDRESS=no-reply@example.com
EMAIL_FROM_NAME="AI Platform"
```

Mailtrap Email Sandbox provides SMTP credentials for a safe testing inbox; its current documentation lists `sandbox.smtp.mailtrap.io` and port `2525` as a standard test configuration. The application intentionally does not depend on Mailtrap-specific SDKs.

## Production direction

Keep `ExpenseNotificationService` independent of provider details. A future provider can replace the SMTP sender without changing Expense workflow code.

## Testing

Unit tests should verify:

- exactly two notification requests are created per decision
- employee address is used for the employee message
- manager address is used for the manager message
- approved and manager-decision statuses both notify both recipients
- failure of one delivery does not prevent the second delivery attempt
