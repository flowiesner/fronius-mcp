import json
import os
from pathlib import Path

_CONFIG_FILE = Path.home() / ".fronius-mcp.json"
_ENV_VAR = "FRONIUS_HOST"


class NotConfiguredError(RuntimeError):
    pass


def _normalize_host(raw: str) -> str:
    """Strip scheme, port, and trailing slashes so users can paste any URL format."""
    host = raw.strip()
    for prefix in ("https://", "http://"):
        if host.startswith(prefix):
            host = host[len(prefix):]
    host = host.split("/")[0].split(":")[0]
    return host


def get_host() -> str:
    if host := os.environ.get(_ENV_VAR, "").strip():
        return _normalize_host(host)
    if _CONFIG_FILE.exists():
        try:
            data = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
            if host := data.get("inverter_host", "").strip():
                return host
        except Exception:
            pass
    raise NotConfiguredError(
        "Fronius inverter IP not configured. "
        "Call the configure_inverter tool with your inverter's IP address "
        "(e.g. '192.168.178.35') to set it up."
    )


def set_host(host: str) -> None:
    data: dict = {}
    if _CONFIG_FILE.exists():
        try:
            data = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    data["inverter_host"] = host
    _CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
