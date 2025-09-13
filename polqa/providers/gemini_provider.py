from .base import BaseProvider
import google.generativeai as genai

class GeminiProvider(BaseProvider):
    def generate(self, prompt: str) -> str:
        # API key is read from GEMINI_API_KEY automatically
        genai.configure()
        model = genai.GenerativeModel(self.model or "gemini-1.5-flash")
        resp = model.generate_content(prompt)
        try:
            return (resp.text or "").strip()
        except Exception:
            return ""
