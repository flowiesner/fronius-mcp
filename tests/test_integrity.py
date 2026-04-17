import os

from fronius_mcp.server import _ALL_TOOLS, build_server
from fronius_mcp.toolsets import TOOLSETS, get_active_tools


def test_all_toolset_tools_are_implemented():
    """Every tool name listed in TOOLSETS must have an entry in _ALL_TOOLS."""
    defined = set(_ALL_TOOLS.keys())
    for group, tools in TOOLSETS.items():
        for tool in tools:
            assert tool in defined, f"'{tool}' in group '{group}' has no implementation in _ALL_TOOLS"


def test_active_tools_are_subset_of_defined():
    active = get_active_tools()
    defined = set(_ALL_TOOLS.keys())
    assert active <= defined, f"Active tools not in _ALL_TOOLS: {active - defined}"


def test_server_builds_without_error():
    mcp = build_server()
    assert mcp is not None


def test_default_active_tools():
    """Realtime group must be active by default (no env var set)."""
    active = get_active_tools()
    assert "solar_power_flow" in active
    assert "solar_meter" in active
    assert "solar_battery" in active


def test_configure_inverter_always_registered():
    """configure_inverter must be in the tool list even when no toolset is active."""
    env_backup = os.environ.pop("FRONIUS_TOOLSETS", None)
    try:
        os.environ["FRONIUS_TOOLSETS"] = "nonexistent"
        mcp = build_server()
        tool_names = {t.name for t in mcp._tool_manager.list_tools()}
        assert "configure_inverter" in tool_names, "configure_inverter must always be registered"
        assert "solar_power_flow" not in tool_names
    finally:
        if env_backup is None:
            os.environ.pop("FRONIUS_TOOLSETS", None)
        else:
            os.environ["FRONIUS_TOOLSETS"] = env_backup
