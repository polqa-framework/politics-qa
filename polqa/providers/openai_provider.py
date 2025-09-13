import os
from .base import BaseProvider

class OpenAIProvider(BaseProvider):
    def generate(self, prompt: str) -> str:
        try:
            from openai import OpenAI
        except Exception as e:
            raise RuntimeError("openai package not available. Install dependency and try again.") from e
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY not set in environment.")
        client = OpenAI()  # reads key from env
        model = self.model or "gpt-4o"
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )
        try:
            return (resp.choices[0].message.content or "").strip()
        except Exception:
            return ""
