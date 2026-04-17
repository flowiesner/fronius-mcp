import socket
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from fronius_mcp import client, config
from fronius_mcp.toolsets import get_active_tools


def configure_inverter(host: str) -> str:
    """
    Configure the Fronius inverter IP address or hostname.

    Call this once to tell the MCP server where your inverter lives.
    The value is saved to ~/.fronius-mcp.json and persists across restarts.

    Args:
        host: IP address or hostname of the inverter (e.g. '192.168.178.35').
              Scheme and port are stripped automatically.

    Returns a confirmation message, or a warning if the inverter is unreachable.
    """
    normalized = config._normalize_host(host)
    config.set_host(normalized)

    try:
        socket.setdefaulttimeout(3)
        socket.getaddrinfo(normalized, 80)
        return f"Inverter configured: {normalized}. Connection check passed."
    except OSError:
        return (
            f"Inverter configured: {normalized}. "
            "Warning: could not reach the inverter right now — "
            "check the IP and that the inverter is on the same network."
        )


def solar_power_flow() -> dict:
    """
    Real-time power flow data from the Fronius Symo GEN24 inverter.

    Returns PV generation (pv_w), grid exchange (grid_w, positive = import,
    negative = export), house load (load_w), battery power (battery_w, positive
    = charging, negative = discharging), autonomy and self-consumption
    percentages, daily/yearly/total energy yields, operating mode, and battery
    standby state.
    """
    return client.get_power_flow()


def solar_meter() -> dict:
    """
    Real-time data from the Fronius Smart Meter at the grid feed-in point.

    Returns total grid power (power_w), per-phase real power (power_l1/l2/l3_w),
    total energy consumed from grid (energy_consumed_wh), total energy fed into
    grid (energy_fed_wh), per-phase voltage and current (voltage/current_l1/l2/l3),
    and grid frequency (frequency_hz). Positive power = importing from grid,
    negative = exporting to grid.
    """
    return client.get_meter()


def solar_battery() -> dict:
    """
    Real-time data from the BYD Battery-Box Premium HV.

    Returns state of charge (soc_pct), DC voltage and current, cell
    temperature (temp_c), usable and design capacity in Wh, cell status,
    enabled flag, and manufacturer/model info.
    """
    return client.get_battery()


def solar_devices() -> dict:
    """
    Lists all devices currently connected to the Fronius inverter system.

    Returns a dict with device classes (inverter, meter, storage, ohmpilot, etc.)
    as keys. Each entry is a list of connected devices with their bus index and
    serial number. Empty list means the device class is supported but nothing
    is connected. Useful for verifying system topology or diagnosing missing devices.
    """
    return client.get_devices()


_ALL_TOOLS: dict[str, Callable] = {
    "solar_power_flow": solar_power_flow,
    "solar_meter":      solar_meter,
    "solar_battery":    solar_battery,
    "solar_devices":    solar_devices,
}


def build_server() -> FastMCP:
    mcp = FastMCP("Fronius Solar")
    mcp.tool()(configure_inverter)
    active = get_active_tools()
    for name, fn in _ALL_TOOLS.items():
        if name in active:
            mcp.tool()(fn)
    return mcp
