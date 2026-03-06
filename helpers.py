import re


def clean_text(text: str) -> str:
    """Strip extra whitespace from a string."""
    return re.sub(r"\s+", " ", text).strip()


def extract_price(text: str) -> float | None:
    """Pull the first dollar amount from a string."""
    match = re.search(r"\$?([\d,]+(?:\.\d{1,2})?)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None


def format_currency(amount: float) -> str:
    return f"${amount:,.2f}"


def truncate(text: str, max_len: int = 200) -> str:
    return text if len(text) <= max_len else text[:max_len] + "…"
