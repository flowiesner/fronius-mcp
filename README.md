# fronius-mcp

Real-time solar data from your Fronius inverter, directly in Claude.

Ask things like:
> *"How much solar power am I generating right now?"*
> *"What's my battery charge level?"*
> *"Am I importing or exporting to the grid?"*
> *"What can you do with my solar system?"*
> *"Analyse my photovoltaics for me."*

Connects to the **Fronius Solar API v1** on your local network — no cloud account required.

---

## Requirements

- A Fronius inverter on your local network with the **Solar API (JSON API) enabled**
- [Claude Desktop](https://claude.ai/download)
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed

---

## Setup

### 1. Add to Claude Desktop

Open your `claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "fronius": {
      "command": "uvx",
      "args": ["fronius-mcp"]
    }
  }
}
```

**Config file location:**

| Platform | Path |
|---|---|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Windows (Store app) | `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json` |

### 2. Restart Claude Desktop

### 3. Configure your inverter

In a new Claude conversation, say:

> *"Configure my Fronius inverter at 192.168.178.35"*

Claude will save your inverter's IP and confirm the connection. This is a one-time step — the address is stored in `~/.fronius-mcp.json` and persists across restarts.

**Don't know your inverter's IP?** Just ask Claude — `configure_inverter` includes step-by-step instructions for finding it via your router, Solar.web, or the inverter's display, plus how to enable the Solar API if you haven't already.

---

## Tools

| Tool | What it does |
|---|---|
| `configure_inverter` | Set your inverter's IP address — run this once on first setup |
| `solar_power_flow` | PV generation, grid exchange, house load, battery power, autonomy, energy totals |
| `solar_meter` | Grid power per phase, cumulative energy in/out, voltage, current, frequency |
| `solar_battery` | State of charge, voltage, current, temperature, capacity, status |
| `solar_devices` | All connected devices with type, bus index, and serial number |

---

## Compatible Hardware

Developed and tested on:

- **Fronius Symo GEN24 10.0 Plus**
- **BYD Battery-Box Premium HV** (13.824 kWh)
- **Fronius Smart Meter** (grid feed-in point, 3-phase)

Other Fronius inverters with Solar API v1 should work. Some endpoints behave differently across models — if something doesn't work on your hardware, open an issue.

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
