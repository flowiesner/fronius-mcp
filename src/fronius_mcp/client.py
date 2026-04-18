import requests

from fronius_mcp import config


def get(endpoint: str, params: dict = None) -> dict:
    host = config.get_host()
    base_url = f"http://{host}/solar_api/v1"
    r = requests.get(f"{base_url}/{endpoint}", params=params, timeout=5)
    r.raise_for_status()
    data = r.json()
    status = data["Head"]["Status"]
    if status["Code"] != 0:
        raise RuntimeError(f"API Error {status['Code']}: {status['Reason']}")
    return data["Body"]["Data"]


def get_power_flow() -> dict:
    site = get("GetPowerFlowRealtimeData.fcgi").get("Site", {})
    load = site.get("P_Load")
    return {
        "pv_w":                   site.get("P_PV") or 0,
        "grid_w":                 site.get("P_Grid"),
        "load_w":                 abs(load) if load is not None else None,
        "battery_w":              site.get("P_Akku"),
        "autonomy_pct":           site.get("rel_Autonomy"),
        "self_consumption_pct":   site.get("rel_SelfConsumption"),
        "energy_today_wh":        site.get("E_Day"),
        "energy_year_wh":         site.get("E_Year"),
        "energy_total_wh":        site.get("E_Total"),
        "mode":                   site.get("Mode"),
        "battery_standby":        site.get("BatteryStandby"),
    }


def get_meter() -> dict:
    data = get("GetMeterRealtimeData.cgi", params={"Scope": "System"})
    m = data.get("0")
    if m is None:
        return {"error": "No smart meter detected at index 0."}
    return {
        "power_w":             m.get("PowerReal_P_Sum"),
        "power_l1_w":          m.get("PowerReal_P_Phase_1"),
        "power_l2_w":          m.get("PowerReal_P_Phase_2"),
        "power_l3_w":          m.get("PowerReal_P_Phase_3"),
        "energy_consumed_wh":  m.get("EnergyReal_WAC_Sum_Consumed"),
        "energy_fed_wh":       m.get("EnergyReal_WAC_Sum_Produced"),
        "voltage_l1_v":        m.get("Voltage_AC_Phase_1"),
        "voltage_l2_v":        m.get("Voltage_AC_Phase_2"),
        "voltage_l3_v":        m.get("Voltage_AC_Phase_3"),
        "current_l1_a":        m.get("Current_AC_Phase_1"),
        "current_l2_a":        m.get("Current_AC_Phase_2"),
        "current_l3_a":        m.get("Current_AC_Phase_3"),
        "frequency_hz":        m.get("Frequency_Phase_Average"),
    }


def get_devices() -> dict:
    data = get("GetActiveDeviceInfo.cgi", params={"DeviceClass": "System"})
    result = {}
    for device_class, devices in data.items():
        if devices:
            result[device_class.lower()] = [
                {"index": idx, "serial": dev.get("Serial", "").strip()}
                for idx, dev in devices.items()
            ]
        else:
            result[device_class.lower()] = []
    return result


def get_battery() -> dict:
    data = get("GetStorageRealtimeData.cgi", params={"Scope": "System"})
    device = data.get("0")
    if device is None:
        return {"error": "No battery detected at index 0."}
    ctrl = device.get("Controller", {})
    details = ctrl.get("Details", {})
    enable = ctrl.get("Enable")
    return {
        "soc_pct":            ctrl.get("StateOfCharge_Relative"),
        "voltage_v":          ctrl.get("Voltage_DC"),
        "current_a":          ctrl.get("Current_DC"),
        "temp_c":             ctrl.get("Temperature_Cell"),
        "capacity_max_wh":    ctrl.get("Capacity_Maximum"),
        "capacity_design_wh": ctrl.get("DesignedCapacity"),
        "status":             ctrl.get("Status_BatteryCell"),
        "enabled":            bool(enable) if enable is not None else None,
        "manufacturer":       details.get("Manufacturer"),
        "model":              details.get("Model"),
    }
