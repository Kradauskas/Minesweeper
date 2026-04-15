from abc import ABC, abstractmethod

class GameEntity(ABC):

    def __init__(self, name):
        self._name = name
        self._status = "active"

    @abstractmethod
    def get_status(self):
        pass

    @abstractmethod
    def reset(self):
        pass