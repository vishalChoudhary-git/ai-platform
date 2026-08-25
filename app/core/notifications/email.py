import asyncio
import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr
from typing import Protocol

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

MAILTRAP_SEND_URL = "https://send.api.mailtrap.io/api/send"


@dataclass(frozen=True)
class EmailMessageData:
    to: str
    subject: str
    body: str


class EmailSender(Protocol):
    async def send(self, message: EmailMessageData) -> None: ...


class DisabledEmailSender:
    async def send(self, message: EmailMessageData) -> None:
        logger.info(
            "DisabledEmailSender.send: disabled recipient=%s subject=%s",
            message.to,
            message.subject,
        )


class MailtrapEmailSender:
    def __init__(
        self,
        api_token: str,
        from_address: str,
        from_name: str,
        enabled: bool = False,
    ) -> None:
        self.api_token = api_token
        self.from_address = from_address
        self.from_name = from_name
        self.enabled = enabled

    @classmethod
    def from_settings(cls) -> "MailtrapEmailSender":
        settings = get_settings()
        return cls(
            api_token=settings.mailtrap_api_token,
            from_address=settings.email_from_address,
            from_name=settings.email_from_name,
            enabled=settings.email_enabled,
        )

    async def send(self, message: EmailMessageData) -> None:
        if not self.enabled:
            logger.info(
                "MailtrapEmailSender.send: disabled recipient=%s subject=%s",
                message.to,
                message.subject,
            )
            return
        if not self.api_token:
            raise RuntimeError("MAILTRAP_API_TOKEN is required when email is enabled outside production.")

        payload = {
            "from": {"email": self.from_address, "name": self.from_name},
            "to": [{"email": message.to}],
            "subject": message.subject,
            "text": message.body,
            "category": "Expense Resolution",
        }
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(MAILTRAP_SEND_URL, json=payload, headers=headers)
            if response.is_error:
                raise RuntimeError(
                    f"Mailtrap email delivery failed: HTTP {response.status_code} {response.text}"
                )

        logger.info(
            "MailtrapEmailSender.send: sent recipient=%s subject=%s",
            message.to,
            message.subject,
        )


class SmtpEmailSender:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        from_address: str,
        from_name: str,
        use_tls: bool = True,
        enabled: bool = False,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_address = from_address
        self.from_name = from_name
        self.use_tls = use_tls
        self.enabled = enabled

    @classmethod
    def from_settings(cls) -> "SmtpEmailSender":
        settings = get_settings()
        return cls(
            host=settings.email_smtp_host,
            port=settings.email_smtp_port,
            username=settings.email_smtp_username,
            password=settings.email_smtp_password,
            from_address=settings.email_from_address,
            from_name=settings.email_from_name,
            use_tls=settings.email_smtp_use_tls,
            enabled=settings.email_enabled,
        )

    async def send(self, message: EmailMessageData) -> None:
        if not self.enabled:
            logger.info(
                "SmtpEmailSender.send: disabled recipient=%s subject=%s",
                message.to,
                message.subject,
            )
            return

        await asyncio.to_thread(self._send_sync, message)
        logger.info(
            "SmtpEmailSender.send: sent recipient=%s subject=%s",
            message.to,
            message.subject,
        )

    def _send_sync(self, message: EmailMessageData) -> None:
        email = EmailMessage()
        email["From"] = formataddr((self.from_name, self.from_address))
        email["To"] = message.to
        email["Subject"] = message.subject
        email.set_content(message.body)

        with smtplib.SMTP(self.host, self.port, timeout=20) as server:
            if self.use_tls:
                server.starttls()
            if self.username:
                server.login(self.username, self.password)
            server.send_message(email)


def get_email_sender() -> EmailSender:
    settings = get_settings()
    if not settings.email_enabled:
        logger.info(
            "get_email_sender: provider=disabled environment=%s",
            settings.environment,
        )
        return DisabledEmailSender()

    if settings.environment.lower() == "production":
        logger.info(
            "get_email_sender: provider=smtp environment=production smtp_host=%s smtp_port=%s",
            settings.email_smtp_host,
            settings.email_smtp_port,
        )
        return SmtpEmailSender.from_settings()

    logger.info(
        "get_email_sender: provider=mailtrap environment=%s",
        settings.environment,
    )
    return MailtrapEmailSender.from_settings()
