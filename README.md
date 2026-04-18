# fronius-mcp
<!-- mcp-name: io.github.flowiesner/fronius-mcp -->

[![PyPI](https://img.shields.io/pypi/v/fronius-mcp)](https://pypi.org/project/fronius-mcp/)
[![MCP Registry](https://img.shields.io/badge/MCP-Registry-blue)](https://registry.modelcontextprotocol.io/servers/io.github.flowiesner/fronius-mcp)

Real-time solar data from your Fronius inverter, directly in Claude.

Ask things like:

> *"How much solar power am I generating right now?"*
>
> *"What's my battery charge level?"*
>
> *"Am I currently importing or exporting to the grid?"*
>
> *"How much energy did I produce this year?"*
>
> *"What can you do with my solar system?"*
>
> *"Analyse my photovoltaics for me."*

Connects to the **Fronius Solar API v1** directly on your local network — no cloud account, no subscription, no data leaving your home.

---

## How it works

fronius-mcp is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server. MCP is an open standard that lets AI assistants like Claude connect to external tools and data sources. Once configured, Claude can call your inverter's local API in real time — whenever you ask a question about your solar system, Claude fetches live data and answers based on what's actually happening right now.

---

## Requirements

- A Fronius inverter on your local network with the **Solar API (JSON API) enabled**
- [Claude Desktop](https://claude.ai/download)
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) — a fast Python package manager (one-line install)

---

## Setup

### 1. Install uv

`uv` is a fast Python package manager used to run fronius-mcp without a permanent install.

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Restart your terminal after installing.

### 2. Add to Claude Desktop

Open your `claude_desktop_config.json` and add the `fronius` block inside `mcpServers`:

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

> **Tip:** If the `mcpServers` key already exists, just add the `fronius` block inside it — don't create a second `mcpServers`.

### 3. Restart Claude Desktop

Close and reopen Claude Desktop so it picks up the new server config.

### 4. Configure your inverter

In a new Claude conversation, say:

> *"Configure my Fronius inverter at 192.168.178.35"*

Claude will save your inverter's IP and confirm the connection. This is a one-time step — the address is stored in `~/.fronius-mcp.json` and persists across restarts.

**Don't know your inverter's IP?** Tell Claude: *"I want to configure my Fronius inverter but I don't know the IP."* Claude will walk you through finding it via your router, Fronius Solar.web, or the inverter's touch display — and how to enable the Solar API in the inverter's web interface if you haven't done that yet.

---

## What you can ask

Once set up, just talk to Claude naturally. Some examples:

- *"What's my current solar output?"* — live PV generation in watts
- *"How self-sufficient am I right now?"* — autonomy and self-consumption percentages
- *"Is my battery charging or discharging?"* — battery power flow and state of charge
- *"How much have I fed into the grid today?"* — energy totals from the smart meter
- *"What devices are connected to my inverter?"* — full system topology
- *"Give me a full overview of my solar system."* — Claude combines all data sources into a summary

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

Other Fronius inverters with Solar API v1 support should work. Some API endpoints behave differently across models — if something doesn't work on your hardware, open an issue.

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
