from abc import ABC, abstractmethod


class Tool(ABC):

    def __init__(
            self,
            name: str):
        self._name = name

    def get_name(self):
        return self._name

    @abstractmethod
    def get_function(self):
        pass

    @abstractmethod
    def get_definition(self):
        pass

    @abstractmethod
    def describe(self):
        pass

    def __str__(self):
        return self.describe()