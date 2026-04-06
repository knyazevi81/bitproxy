"""
Placeholder for VK API TURN credentials retrieval.
vk-turn-proxy handles credential exchange internally via the call link,
so this module exists for future extensibility.
"""


async def validate_call_link(raw_link: str) -> bool:
    """
    Basic validation that the raw_link looks like a VK call link.
    A real implementation could make an HTTP request to verify.
    """
    return raw_link.startswith("https://vk.com/call/") or "vk.com" in raw_link
