import os
from .base import BaseProvider

try:
    from xai_sdk import Client
    from xai_sdk.chat import user as xai_user
except Exception as e:
    _import_error = e
    Client = None
    xai_user = None
    xai_system = None


class XAIProvider(BaseProvider):
    """
    Provider for xAI (Grok) via xai-sdk.

    Env:
      - XAI_API_KEY: required
      - XAI_TIMEOUT_SECS: optional (default 3600)
      - POLQA_DEBUG=1: optional verbose logs

    Defaults:
      - model = "grok-4"
      - temperature = 0.0
    """

    def __init__(self, model: str = "grok-4", temperature: float = 0.0):
        super().__init__(model, temperature)

        if Client is None or xai_user is None:
            raise RuntimeError(
                "xai-sdk is not available. Install with: pip install xai-sdk"
            ) from _import_error

        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            raise ValueError(
                "Missing xAI API key. Use: polqa config apikey xai <your-key> "
                "or export XAI_API_KEY in your environment."
            )

        timeout = int(os.getenv("XAI_TIMEOUT_SECS", "3600"))
        self.client = Client(api_key=api_key, timeout=timeout)

    def generate(self, prompt: str) -> str:
        DEBUG = os.getenv("POLQA_DEBUG", "0") == "1"

        if DEBUG:
            print("[XAIProvider] Calling xAI (Grok)...")
            print(f"[XAIProvider] model={self.model}, temperature={self.temperature}")
            print(f"[XAIProvider] prompt[:200]={repr(prompt[:200])}")

        try:
            # Some xai-sdk versions might accept temperature at create-time.
            try:
                chat = self.client.chat.create(model=self.model, temperature=self.temperature)
                temp_applied = True
            except TypeError:
                chat = self.client.chat.create(model=self.model)
                temp_applied = False
                if DEBUG and self.temperature not in (None, 0.0):
                    print("[XAIProvider][WARN] SDK does not support temperature at create(); "
                          "continuing without temperature control.")

            # If you later want a system prompt, you can gate it behind an env var:
            # sys_prompt = os.getenv("XAI_SYSTEM_PROMPT")
            # if sys_prompt:
            #     chat.append(xai_system(sys_prompt))

            chat.append(xai_user(prompt))

            # IMPORTANT: .sample() in current SDK does NOT take temperature.
            response = chat.sample()

        except Exception as e:
            if DEBUG:
                print(f"[XAIProvider][ERROR] Exception while sampling: {e!r}")
            return ""

        # Quickstart indicates `response.content` holds the text.
        try:
            text = (getattr(response, "content", "") or "").strip()
        except Exception:
            text = ""

        if DEBUG:
            print(f"[XAIProvider] result_len={len(text)} result_preview={repr(text[:200])}")

        return text
