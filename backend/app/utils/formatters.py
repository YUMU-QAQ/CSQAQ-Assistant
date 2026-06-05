"""Price formatting utilities."""
from typing import Optional

def format_price_yuan(value: Optional[float]) -> str:
    """Format a price in CNY yuan."""
    if value is None:
        return "N/A"
    if value >= 10000:
        return f"¥{value:,.0f}"
    elif value >= 1000:
        return f"¥{value:,.1f}"
    elif value >= 1:
        return f"¥{value:.2f}"
    else:
        return f"¥{value:.4f}"


def format_pct(value: Optional[float]) -> str:
    """Format a percentage change."""
    if value is None:
        return "N/A"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def format_volume(value: Optional[int]) -> str:
    """Format a volume number."""
    if value is None:
        return "N/A"
    if value >= 100000000:
        return f"{value / 100000000:.1f}亿"
    elif value >= 10000:
        return f"{value / 10000:.1f}万"
    return f"{value:,}"
