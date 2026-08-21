import asyncio
import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr
from typing import Protocol

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmailMessageData:
    to: str
    subject: str
    body: str


class EmailSender(Protocol):
    async def send(self, message: EmailMessageData) -> None: ...


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
