import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096
TEMPERATURE = 0.3

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def call_baseline(prompt: str) -> str | None:
    """Send the baseline prompt and return the raw text response, or None on failure."""
    try:
        client = _get_client()
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"[llm_client] Baseline call failed: {e}")
        return None


def call_improved(system_prompt: str, user_message: str) -> str | None:
    """Send the context-engineered prompt and return the raw text response, or None on failure."""
    try:
        client = _get_client()
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"[llm_client] Improved call failed: {e}")
        return None
