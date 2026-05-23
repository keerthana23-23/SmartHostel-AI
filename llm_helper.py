
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import openai  # for exception classes

# Load variables from .env (OPENAI_API_KEY, USE_MOCK_AI, OPENAI_MODEL)
load_dotenv()  # reads .env and puts values into environment variables [1](https://pypi.org/project/python-dotenv/)

USE_MOCK_AI = os.getenv("USE_MOCK_AI", "false").lower() == "true"
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _mock_analyze(text: str) -> dict:
    """Rule-based fallback so the demo works even without quota."""
    t = (text or "").lower()

    # category rules
    if any(k in t for k in ["leak", "water", "pipe", "electric", "fan", "light", "repair", "switch", "socket"]):
        category = "Maintenance"
    elif any(k in t for k in ["dirty", "garbage", "smell", "clean", "washroom", "toilet", "drain"]):
        category = "Cleanliness"
    elif any(k in t for k in ["theft", "fight", "security", "unsafe", "intruder", "threat"]):
        category = "Security"
    else:
        category = "Other"

    # priority rules
    if any(k in t for k in ["urgent", "danger", "immediately", "asap", "wet floor", "fire", "shock"]):
        priority = "High"
    elif any(k in t for k in ["soon", "please", "request", "kindly"]):
        priority = "Medium"
    else:
        priority = "Low"

    summary = (text or "").strip()
    if len(summary) > 90:
        summary = summary[:87] + "..."

    suggested_action = f"Assign to {category} team and track until resolved."
    draft_reply = (
        "Hi, thanks for reporting this. "
        f"We have logged your complaint under {category} and will address it soon. "
        "We will update you once it is resolved."
    )

    return {
        "summary": summary,
        "category": category,
        "priority": priority,
        "suggested_action": suggested_action,
        "draft_reply": draft_reply,
    }


def _format_result(data: dict, header_note: str | None = None) -> str:
    """Pretty print for terminal output."""
    lines = []
    if header_note:
        lines.append(header_note)
        lines.append("")

    lines.append(f"Summary: {data.get('summary', '')}")
    lines.append(f"Category: {data.get('category', '')}")
    lines.append(f"Priority: {data.get('priority', '')}")
    lines.append(f"Suggested Action: {data.get('suggested_action', '')}")
    lines.append(f"Draft Reply: {data.get('draft_reply', '')}")
    return "\n".join(lines)


def analyze_complaint(text: str) -> str:
    """
    Returns a formatted string for the CLI.
    Uses LLM if available; falls back to mock if quota/key issues occur.
    """

    # If user explicitly wants mock mode (no billing required)
    if USE_MOCK_AI:
        data = _mock_analyze(text)
        return _format_result(data, header_note="NOTE: USE_MOCK_AI=true (running fallback mode).")

    # Create client. The OpenAI Python SDK reads OPENAI_API_KEY from env by default. [3](https://developers.openai.com/api/reference/python)
    client = OpenAI()

    system_msg = (
        "You are a hostel admin assistant. "
        "Triage complaints and return ONLY valid JSON with keys: "
        "summary, category, priority, suggested_action, draft_reply. "
        "category must be one of: Maintenance, Cleanliness, Security, Other. "
        "priority must be one of: Low, Medium, High. "
        "summary must be 1 sentence."
    )

    user_msg = f"Complaint:\n{text}\n\nReturn JSON only."

    try:
        resp = client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )

        out = (resp.output_text or "").strip()

        # Remove code fences if model adds them
        out = out.replace("```json", "").replace("```", "").strip()

        data = json.loads(out)

        # hard validation
        if data.get("category") not in ["Maintenance", "Cleanliness", "Security", "Other"]:
            data["category"] = "Other"
        if data.get("priority") not in ["Low", "Medium", "High"]:
            data["priority"] = "Medium"

        for k in ["summary", "category", "priority", "suggested_action", "draft_reply"]:
            data.setdefault(k, "")

        return _format_result(data)

    except openai.AuthenticationError:
        # Incorrect API key (401) [4](https://help.openai.com/en/articles/6882433-incorrect-api-key-provided)[5](https://bing.com/search?q=OpenAI+best+practice+store+API+key+environment+variable+OPENAI_API_KEY)
        note = (
            "NOTE: OpenAI AuthenticationError (401). "
            "Check OPENAI_API_KEY in your .env file. "
            "Do NOT use quotes around the key."
        )
        # Quotes in .env can cause issues; keep it as OPENAI_API_KEY=sk-... [8](https://github.com/openai/openai-python/discussions/1651)
        data = _mock_analyze(text)
        return _format_result(data, header_note=note + "\nUsing fallback result:")

    except openai.RateLimitError:
        # Covers 429 errors (rate limit or insufficient_quota). Your case: insufficient_quota. [6](https://fixdevs.com/blog/openai-api-not-working/)[7](https://developers.openai.com/cookbook/examples/how_to_handle_rate_limits)
        note = (
            "NOTE: OpenAI RateLimitError (429) / insufficient quota.\n"
            "This usually means your account has no credits or billing is not enabled.\n"
            "Using fallback result so the demo still works."
        )
        data = _mock_analyze(text)
        return _format_result(data, header_note=note)

    except Exception as e:
        # Any other unexpected error: still return fallback so app never crashes
        note = f"NOTE: Unexpected error from API: {e}\nUsing fallback result:"
        data = _mock_analyze(text)
        return _format_result(data, header_note=note)
