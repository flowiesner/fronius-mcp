from mcp.server.fastmcp import FastMCP
import fronius

mcp = FastMCP("Fronius Solar")


@mcp.tool()
def solar_power_flow() -> dict:
    """
    Real-time power flow data from the Fronius Symo GEN24 inverter.

    Returns PV generation (pv_w), grid exchange (grid_w, positive = import,
    negative = export), house load (load_w), battery power (battery_w, positive
    = charging, negative = discharging), autonomy and self-consumption
    percentages, daily/yearly/total energy yields, operating mode, and battery
    standby state.
    """
    return fronius.get_power_flow()


@mcp.tool()
def solar_meter() -> dict:
    """
    Real-time data from the Fronius Smart Meter at the grid feed-in point.

    Returns current grid power (power_w), total energy consumed from grid
    (energy_consumed_wh), total energy fed into grid (energy_fed_wh), phase 1
    voltage (voltage_v), phase 1 current (current_a), and grid frequency
    (frequency_hz).
    """
    return fronius.get_meter()


@mcp.tool()
def solar_battery() -> dict:
    """
    Real-time data from the BYD Battery-Box Premium HV.

    Returns state of charge (soc_pct), DC voltage and current, cell
    temperature (temp_c), usable and design capacity in Wh, cell status,
    enabled flag, and manufacturer/model info.
    """
    return fronius.get_battery()


if __name__ == "__main__":
    mcp.run()
