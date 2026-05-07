import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"
HAIKU_MODEL = "claude-haiku-4-5-20251001"
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


def enhance_feature(description: str, business_objective: str = "", intended_user: str = "") -> dict | None:
    """Enhance description, business objective, and intended user as a unit. Infers missing fields."""
    import json as _json
    try:
        client = _get_client()
        message = client.messages.create(
            model=MODEL,
            max_tokens=512,
            temperature=0.4,
            system=(
                "You are a business analyst specializing in specialty insurance software delivery. "
                "Given a feature's fields, return improved versions of all three. Rules:\n"
                "- description: improve clarity, specificity, and completeness. Preserve all original intent. Do not invent constraints.\n"
                "- business_objective: if provided, sharpen it to one concise sentence. If empty, infer from the description.\n"
                "- intended_user: if provided, normalize to a short role name (e.g. 'Broker', 'Underwriter'). If empty, infer from the description.\n"
                "Return only a valid JSON object with exactly these keys: description, business_objective, intended_user. "
                "No preamble, no explanation."
            ),
            messages=[{"role": "user", "content": (
                f"Description: {description}\n"
                f"Business Objective: {business_objective or 'Not provided'}\n"
                f"Intended User: {intended_user or 'Not provided'}"
            )}],
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return _json.loads(raw.strip())
    except Exception as e:
        print(f"[llm_client] enhance_feature failed: {e}")
        return None


def suggest_fanout_context(feature_name: str, feature_description: str) -> dict | None:
    """Infer business objective, intended user, business rules, and notes from a feature description."""
    import json as _json
    try:
        client = _get_client()
        message = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=256,
            temperature=0.3,
            system=(
                "You are an expert Business Analyst specializing in specialty insurance delivery workflows. "
                "Given a feature name and description, infer the most likely values for four planning fields. "
                "Return only a valid JSON object with exactly these keys: "
                "business_objective, intended_user, business_rules, notes. "
                "Formatting rules: "
                "- business_objective: one concise sentence. "
                "- intended_user: short role name only (e.g. 'Broker', 'Underwriter'). "
                "- business_rules: if multiple rules exist, format as a markdown numbered list with each item on its own line (e.g. '1. Rule one\\n2. Rule two'). "
                "- notes: if multiple notes exist, format as a markdown bulleted list with each item on its own line (e.g. '- Note one\\n- Note two'). "
                "If a field cannot be reasonably inferred, return an empty string. "
                "Do not include any text outside the JSON."
            ),
            messages=[{
                "role": "user",
                "content": f"Feature: {feature_name}\nDescription: {feature_description}"
            }],
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return _json.loads(raw.strip())
    except Exception as e:
        print(f"[llm_client] suggest_fanout_context failed: {e}")
        return None


def call_fanout(system_prompt: str, user_message: str) -> str | None:
    """Send the fan-out decomposition prompt."""
    FANOUT_MAX_TOKENS = 4096
    try:
        client = _get_client()
        message = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=FANOUT_MAX_TOKENS,
            temperature=TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text
    except Exception as e:
        print(f"[llm_client] Fan-out call failed: {e}")
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


def call_risk_expansion(system_prompt: str, user_message: str) -> str | None:
    """Send the risk expansion analysis prompt. Returns structured risk/edge case analysis."""
    RISK_MAX_TOKENS = 2048
    try:
        client = _get_client()
        message = client.messages.create(
            model=MODEL,
            max_tokens=RISK_MAX_TOKENS,
            temperature=TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return message.content[0].text
    except Exception as e:
        print(f"[llm_client] Risk expansion call failed: {e}")
        return None
