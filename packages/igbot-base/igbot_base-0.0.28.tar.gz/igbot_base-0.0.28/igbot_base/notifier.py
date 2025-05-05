from abc import ABC, abstractmethod

from pydantic import BaseModel


class Notification(BaseModel):
    data: any


class Notifier(ABC):

    @abstractmethod
    def notify(self, notification: Notification):
        pass
