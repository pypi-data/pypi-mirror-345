from abc import ABC, abstractmethod

from igbot_base.agent_response import AgentResponse

from igbot_base.exception_handler import ExceptionHandler, ReturnFailedResponseGracefully
from igbot_base.logging_adapter import get_logger
from llmmemory import LlmMemory

logger = get_logger("application")


class Agent(ABC):

    def __init__(self, name, exception_handler: ExceptionHandler = ReturnFailedResponseGracefully):
        self.__name = name
        self.__ex_handler = exception_handler

    def invoke(self, query, memory: LlmMemory) -> AgentResponse:
        try:
            return self._invoke(query, memory)
        except Exception as e:
            logger.exception("Exception occurred at %s for query %s: %s", self.describe(), query, e)
            return self.__ex_handler.handle(e)

    @abstractmethod
    def _invoke(self, query, memory: LlmMemory) -> AgentResponse:
        pass

    @abstractmethod
    def describe(self):
        pass

    def __str__(self):
        return self.describe()
