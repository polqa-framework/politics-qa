# polqa/providers/claude_provider.py
import os
from anthropic import Anthropic
from .base import BaseProvider


class ClaudeProvider(BaseProvider):
    def __init__(self, model: str = "claude-3-5-sonnet-latest", temperature: float = 0.0):
        super().__init__(model, temperature)
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise ValueError(
                "Missing Claude API key. Use: polqa config apikey claude <your-key>"
            )
        self.client = Anthropic(api_key=api_key)

    def generate(self, prompt: str) -> str:
        DEBUG = os.getenv("POLQA_DEBUG", "0") == "1"

        if DEBUG:
            print("[ClaudeProvider] Llamando a Anthropic...")
            print(f"[ClaudeProvider] model={self.model}, temperature={self.temperature}")
            print(f"[ClaudeProvider] prompt[:200]={repr(prompt[:200])}")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as e:
            if DEBUG:
                print(f"[ClaudeProvider][ERROR] Exception en messages.create: {e!r}")
            return ""

        if DEBUG:
            print(f"[ClaudeProvider] type(response)={type(response)}")
            # Uso de tokens si está disponible
            usage = getattr(response, "usage", None)
            if usage:
                try:
                    in_toks = getattr(usage, "input_tokens", None)
                    out_toks = getattr(usage, "output_tokens", None)
                    print(f"[ClaudeProvider] usage: input_tokens={in_toks}, output_tokens={out_toks}")
                except Exception:
                    print(f"[ClaudeProvider] usage raw: {usage}")

            print(f"[ClaudeProvider] response has content? {bool(getattr(response, 'content', None))}")

        if not response or not response.content:
            if DEBUG:
                print("[ClaudeProvider] response vacío o sin content")
            return ""

        parts = []
        for i, block in enumerate(response.content):
            if DEBUG:
                print(f"[ClaudeProvider] block[{i}] type={getattr(block, 'type', type(block))} "
                    f"has_text_attr={hasattr(block, 'text')} value_preview={repr(getattr(block, 'text', '')[:80])}")
            # SDK moderno: objetos con .type == "text" y .text
            if hasattr(block, "type") and getattr(block, "type", None) == "text" and hasattr(block, "text"):
                parts.append(block.text or "")
            # Fallback por si llegara como dict
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))

        result = "".join(parts).strip()

        if DEBUG:
            print(f"[ClaudeProvider] result_len={len(result)} result_preview={repr(result[:200])}")

        return result