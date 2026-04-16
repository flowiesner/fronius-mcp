# Fronius Solar MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that exposes real-time data from a **Fronius Symo GEN24** solar system to AI assistants like Claude Desktop.

Ask your AI assistant things like:
> *"How much solar power am I generating right now?"*
> *"What's my battery charge level?"*
> *"Am I importing or exporting to the grid?"*

---

## Hardware

| Component | Details |
|---|---|
| Inverter | Fronius Symo GEN24 10.0 Plus |
| Battery | BYD Battery-Box Premium HV — 13.824 kWh |
| Smart Meter | PowerMeter #1 (grid feed-in point) |

---

## MCP Tools

Three tools are exposed to the AI assistant:

### `solar_power_flow`
Real-time power flow from the inverter.

| Field | Description |
|---|---|
| `pv_w` | PV generation in watts |
| `grid_w` | Grid exchange (positive = import, negative = export) |
| `load_w` | House load in watts |
| `battery_w` | Battery power (positive = charging, negative = discharging) |
| `autonomy_pct` | Self-sufficiency percentage |
| `self_consumption_pct` | PV self-consumption percentage |
| `energy_today_wh` | Energy yield today |
| `energy_year_wh` | Energy yield this year |
| `energy_total_wh` | Lifetime energy yield |
| `mode` | Operating mode |
| `battery_standby` | Battery standby state |

### `solar_meter`
Real-time data from the Fronius Smart Meter at the grid connection point.

| Field | Description |
|---|---|
| `power_w` | Current grid power |
| `energy_consumed_wh` | Total energy consumed from grid |
| `energy_fed_wh` | Total energy fed into grid |
| `voltage_v` | Phase 1 voltage |
| `current_a` | Phase 1 current |
| `frequency_hz` | Grid frequency |

### `solar_battery`
Real-time data from the BYD battery.

| Field | Description |
|---|---|
| `soc_pct` | State of charge (%) |
| `voltage_v` | DC voltage |
| `current_a` | DC current |
| `temp_c` | Cell temperature |
| `capacity_max_wh` | Usable capacity |
| `capacity_design_wh` | Design capacity |
| `status` | Cell status |
| `enabled` | Whether battery is enabled |
| `manufacturer` / `model` | Hardware info |

---

## Project Structure

```
fronius-mcp/
├── server.py       # FastMCP server — exposes the 3 tools
├── fronius.py      # Fronius Solar API wrapper
└── pyproject.toml  # Dependencies: mcp[cli], requests
```

---

## Setup

**Requirements:** Python ≥ 3.10, a Fronius inverter on your local network.

```bash
# Install dependencies
pip install -e .

# Test interactively via MCP Inspector (opens at localhost:5173)
mcp dev server.py
```

---

## Claude Desktop Integration

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fronius": {
      "command": "python",
      "args": ["/path/to/fronius-mcp/server.py"]
    }
  }
}
```

> **Windows (Store App):** The config lives at
> `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`

After restarting Claude Desktop, the three solar tools will be available in every conversation.

---

## Fronius Solar API

Uses the **Fronius Solar API v1** over HTTP on the local network.

| Endpoint | Status | Notes |
|---|---|---|
| `GetPowerFlowRealtimeData.fcgi` | ✅ | Primary data source |
| `GetMeterRealtimeData.cgi` | ✅ | `Scope=System`, meter index `"0"` |
| `GetStorageRealtimeData.cgi` | ✅ | `Scope=System`, controller `"0"` |
| `GetInverterRealtimeData.cgi` | ⚠️ | Returns null on GEN24 — not used |
| `GetInverterInfo.cgi` | ❌ | 404 on GEN24 — not used |

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
