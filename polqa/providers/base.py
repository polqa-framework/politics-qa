from abc import ABC, abstractmethod

class BaseProvider(ABC):
    def __init__(self, model: str = None, temperature: float = 0.0):
        self.model = model
        self.temperature = temperature

    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError
