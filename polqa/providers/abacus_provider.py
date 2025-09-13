import os, json, requests
from .base import BaseProvider

class AbacusProvider(BaseProvider):
    def generate(self, prompt: str) -> str:
        api_key = os.getenv("ABACUS_API_KEY")
        if not api_key:
            raise RuntimeError("ABACUS_API_KEY not set in environment.")
        url = "https://routellm.abacus.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model or "route-llm",
                   "messages": [{"role": "user", "content": prompt}],
                   "temperature": self.temperature}
        r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        if r.status_code // 100 != 2:
            return ""
        data = r.json()
        try:
            return (data["choices"][0]["message"]["content"] or "").strip()
        except Exception:
            return ""
