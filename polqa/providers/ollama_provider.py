from .base import BaseProvider
from ollama import chat
from ollama import ChatResponse
import re


class OllamaProvider(BaseProvider):
    def generate(self, prompt: str) -> str:
        resp: ChatResponse = chat(
            model=self.model, 
            messages=[
                {
                    'role': 'user',
                    'content': f'{prompt}',
                },
            ],
            options={'temperature': self.temperature},
        )
        try:
            s = re.sub(r"<think>.*?</think>", "", resp.message.content, flags=re.DOTALL | re.IGNORECASE)
            # print(f"prompt= {prompt} \n ans= {s}")
            return s.strip()
        except Exception:
            return ""