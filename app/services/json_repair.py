import json
import re

def repair_and_parse(text: str) -> dict | None:
    """
    Attempts to safely extract and parse JSON from LLM output.
    Never raises.
    """
    if not text:
        return None

    text = text.strip()

    # Remove markdown fences if any
    text = re.sub(r"```(?:json)?", "", text).strip()

    # Attempt direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Attempt to extract first JSON object
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None

    try:
        return json.loads(match.group())
    except Exception:
        return None
