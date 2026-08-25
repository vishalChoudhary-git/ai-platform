import asyncio
import logging
from dataclasses import dataclass
from typing import Protocol

import mailtrap as mt

from app.core.config import get_settings

logger = logging.getLogger(__name__)


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
            raise RuntimeError("MAILTRAP_API_TOKEN is required when email is enabled.")

        await asyncio.to_thread(self._send_sync, message)
        logger.info(
            "MailtrapEmailSender.send: sent recipient=%s subject=%s",
            message.to,
            message.subject,
        )

    def _send_sync(self, message: EmailMessageData) -> None:
        mail = mt.Mail(
            sender=mt.Address(email=self.from_address, name=self.from_name),
            to=[mt.Address(email=message.to)],
            subject=message.subject,
            text=message.body,
            category="Expense Resolution",
        )
        client = mt.MailtrapClient(token=self.api_token)
        client.send(mail)


def get_email_sender() -> EmailSender:
    settings = get_settings()
    if not settings.email_enabled:
        logger.info(
            "get_email_sender: provider=disabled environment=%s",
            settings.environment,
        )
        return DisabledEmailSender()

    logger.info(
        "get_email_sender: provider=mailtrap environment=%s",
        settings.environment,
    )
    return MailtrapEmailSender.from_settings()
