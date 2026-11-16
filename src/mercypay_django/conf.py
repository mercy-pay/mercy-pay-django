import os
from typing import Any, Optional

from django.conf import settings


def setting(name: str, default: Any = None) -> Any:
    """MERCY_PAY = {"API_KEY": …, "WEBHOOK_SECRET": …} in settings, otherwise the
    MERCY_PAY_API_KEY / MERCY_PAY_WEBHOOK_SECRET environment variables."""
    configured = getattr(settings, "MERCY_PAY", {}) or {}
    if name in configured:
        return configured[name]
    return os.environ.get(f"MERCY_PAY_{name}", default)


def api_key() -> Optional[str]:
    return setting("API_KEY")


def webhook_secret() -> Optional[str]:
    return setting("WEBHOOK_SECRET")
