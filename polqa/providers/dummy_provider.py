from .base import BaseProvider

class DummyProvider(BaseProvider):
    def generate(self, prompt: str) -> str:
        # Deterministic by prompt hash, choose among A..F
        letters = ['A','B','C','D','E','F']
        idx = abs(hash(prompt)) % len(letters)
        return letters[idx]
