from abc import ABC

from pydantic import BaseModel, field_validator


class Notification(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or blank")
        return v


class Notifier(ABC):

    def notify(self, notification: Notification):
        pass
