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
    m = data["0"]
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
