import requests

INVERTER_IP = "192.168.178.35"
BASE_URL = f"http://{INVERTER_IP}/solar_api/v1"


def get(endpoint: str, params: dict = None) -> dict:
    r = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=5)
    r.raise_for_status()
    data = r.json()
    status = data["Head"]["Status"]
    if status["Code"] != 0:
        raise RuntimeError(f"API Error {status['Code']}: {status['Reason']}")
    return data["Body"]["Data"]


def get_power_flow() -> dict:
    site = get("GetPowerFlowRealtimeData.fcgi")["Site"]
    return {
        "pv_w":                   site.get("P_PV") or 0,
        "grid_w":                 site["P_Grid"],
        "load_w":                 abs(site["P_Load"]),
        "battery_w":              site["P_Akku"],
        "autonomy_pct":           site["rel_Autonomy"],
        "self_consumption_pct":   site["rel_SelfConsumption"],
        "energy_today_wh":        site["E_Day"],
        "energy_year_wh":         site["E_Year"],
        "energy_total_wh":        site["E_Total"],
        "mode":                   site["Mode"],
        "battery_standby":        site["BatteryStandby"],
    }


def get_meter() -> dict:
    data = get("GetMeterRealtimeData.cgi", params={"Scope": "System"})
    meter = data["0"]
    return {
        "power_w":             meter.get("PowerReal_P_Sum"),
        "energy_consumed_wh":  meter.get("EnergyReal_WAC_Plus_Absolute"),
        "energy_fed_wh":       meter.get("EnergyReal_WAC_Minus_Absolute"),
        "voltage_v":           meter.get("Voltage_AC_Phase_1"),
        "current_a":           meter.get("Current_AC_Phase_1"),
        "frequency_hz":        meter.get("Frequency_Phase_Average"),
    }


def get_battery() -> dict:
    data = get("GetStorageRealtimeData.cgi", params={"Scope": "System"})
    ctrl = data["0"]["Controller"]
    return {
        "soc_pct":            ctrl["StateOfCharge_Relative"],
        "voltage_v":          ctrl["Voltage_DC"],
        "current_a":          ctrl["Current_DC"],
        "temp_c":             ctrl["Temperature_Cell"],
        "capacity_max_wh":    ctrl["Capacity_Maximum"],
        "capacity_design_wh": ctrl["DesignedCapacity"],
        "status":             ctrl["Status_BatteryCell"],
        "enabled":            bool(ctrl["Enable"]),
        "manufacturer":       ctrl["Details"]["Manufacturer"],
        "model":              ctrl["Details"]["Model"],
    }
