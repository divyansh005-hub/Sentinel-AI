import json

def format_probabilities(probs_dict: dict) -> str:
    """Format a probability dictionary into a readable string."""
    return ", ".join([f"{k}: {v:.2f}%" for k, v in probs_dict.items()])

def safe_json_dumps(data: dict) -> str:
    """Safely dump dict to JSON string."""
    try:
        return json.dumps(data)
    except TypeError:
        return "{}"

def safe_json_loads(data: str) -> dict:
    """Safely load dict from JSON string."""
    try:
        return json.loads(data)
    except (TypeError, json.JSONDecodeError):
        return {}
