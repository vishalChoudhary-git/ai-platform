from types import SimpleNamespace

from app.core.notifications.email import (
    DisabledEmailSender,
    MailtrapEmailSender,
    SmtpEmailSender,
    get_email_sender,
)


def test_email_sender_is_disabled_when_email_disabled(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.core.notifications.email.get_settings",
        lambda: SimpleNamespace(email_enabled=False, environment="development"),
    )

    assert isinstance(get_email_sender(), DisabledEmailSender)


def test_non_production_uses_mailtrap(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.core.notifications.email.get_settings",
        lambda: SimpleNamespace(
            email_enabled=True,
            environment="development",
            mailtrap_api_token="token",
            email_from_address="no-reply@example.com",
            email_from_name="AI Platform",
        ),
    )

    assert isinstance(get_email_sender(), MailtrapEmailSender)


def test_production_uses_smtp(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.core.notifications.email.get_settings",
        lambda: SimpleNamespace(
            email_enabled=True,
            environment="production",
            email_smtp_host="smtp.example.com",
            email_smtp_port=587,
            email_smtp_username="user",
            email_smtp_password="password",
            email_smtp_use_tls=True,
            email_from_address="no-reply@example.com",
            email_from_name="AI Platform",
        ),
    )

    assert isinstance(get_email_sender(), SmtpEmailSender)
