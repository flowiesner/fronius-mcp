import os

# Maps group name → list of tool names belonging to that group.
# New tools must be added here before they can be activated.
TOOLSETS: dict[str, list[str]] = {
    "realtime": [
        "solar_power_flow",
        "solar_meter",
        "solar_battery",
        "solar_devices",
    ],
    # history toolset intentionally omitted:
    # GetArchiveData.cgi returns 404 on the GEN24, and the Solar.web cloud API
    # requires a manual developer account request — too much friction for users.
}

_DEFAULT_TOOLSETS = {"realtime"}


def get_active_tools() -> set[str]:
    """Return the set of tool names enabled via FRONIUS_TOOLSETS env var.

    FRONIUS_TOOLSETS is a comma-separated list of group names, e.g.
    "realtime,history". Defaults to {"realtime"} when unset.
    """
    raw = os.environ.get("FRONIUS_TOOLSETS", "")
    groups = {s.strip() for s in raw.split(",") if s.strip()} or _DEFAULT_TOOLSETS
    active: set[str] = set()
    for group in groups:
        active.update(TOOLSETS.get(group, []))
    return active
