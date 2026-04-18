import pytest
import requests
from unittest.mock import MagicMock, patch

from fronius_mcp import client


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_host():
    """Patch config.get_host() so no real inverter is needed."""
    with patch("fronius_mcp.client.config.get_host", return_value="192.168.0.1"):
        yield


def _ok(data: dict) -> MagicMock:
    """Build a mock requests.Response wrapping Solar API data."""
    m = MagicMock()
    m.json.return_value = {
        "Head": {"Status": {"Code": 0, "Reason": ""}},
        "Body": {"Data": data},
    }
    m.raise_for_status = MagicMock()
    return m


def _api_error(code: int, reason: str) -> MagicMock:
    m = MagicMock()
    m.json.return_value = {
        "Head": {"Status": {"Code": code, "Reason": reason}},
        "Body": {"Data": {}},
    }
    m.raise_for_status = MagicMock()
    return m


# ---------------------------------------------------------------------------
# Sample payloads (realistic Solar API v1 shapes)
# ---------------------------------------------------------------------------

POWER_FLOW_DATA = {
    "Site": {
        "P_PV": 4200.0,
        "P_Grid": -1500.0,
        "P_Load": -2700.0,
        "P_Akku": 0.0,
        "rel_Autonomy": 100.0,
        "rel_SelfConsumption": 64.3,
        "E_Day": 18400.0,
        "E_Year": 5210000.0,
        "E_Total": 28000000.0,
        "Mode": "produce-and-consume",
        "BatteryStandby": False,
    }
}

METER_DATA = {
    "0": {
        "PowerReal_P_Sum": -1500.0,
        "PowerReal_P_Phase_1": -510.0,
        "PowerReal_P_Phase_2": -495.0,
        "PowerReal_P_Phase_3": -495.0,
        "EnergyReal_WAC_Sum_Consumed": 3200000.0,
        "EnergyReal_WAC_Sum_Produced": 9800000.0,
        "Voltage_AC_Phase_1": 231.2,
        "Voltage_AC_Phase_2": 230.8,
        "Voltage_AC_Phase_3": 231.5,
        "Current_AC_Phase_1": 2.21,
        "Current_AC_Phase_2": 2.14,
        "Current_AC_Phase_3": 2.14,
        "Frequency_Phase_Average": 50.01,
    }
}

BATTERY_DATA = {
    "0": {
        "Controller": {
            "StateOfCharge_Relative": 87.5,
            "Voltage_DC": 512.3,
            "Current_DC": 2.1,
            "Temperature_Cell": 23.4,
            "Capacity_Maximum": 11040,
            "DesignedCapacity": 13824,
            "Status_BatteryCell": 0,
            "Enable": 1,
            "Details": {"Manufacturer": "BYD", "Model": "HVM 13.8"},
        }
    }
}


# ---------------------------------------------------------------------------
# get_power_flow
# ---------------------------------------------------------------------------

class TestGetPowerFlow:
    def test_valid_response(self):
        with patch("requests.get", return_value=_ok(POWER_FLOW_DATA)):
            result = client.get_power_flow()
        assert result["pv_w"] == 4200.0
        assert result["grid_w"] == -1500.0
        assert result["load_w"] == 2700.0  # abs() applied
        assert result["autonomy_pct"] == 100.0
        assert result["energy_today_wh"] == 18400.0

    def test_load_abs_applied(self):
        """P_Load is always negative from the API — load_w must be positive."""
        with patch("requests.get", return_value=_ok(POWER_FLOW_DATA)):
            result = client.get_power_flow()
        assert result["load_w"] >= 0

    def test_pv_none_becomes_zero(self):
        """P_PV is null when no sun — should return 0, not None."""
        data = {**POWER_FLOW_DATA, "Site": {**POWER_FLOW_DATA["Site"], "P_PV": None}}
        with patch("requests.get", return_value=_ok(data)):
            result = client.get_power_flow()
        assert result["pv_w"] == 0

    def test_missing_site_returns_nones(self):
        with patch("requests.get", return_value=_ok({})):
            result = client.get_power_flow()
        assert result["grid_w"] is None
        assert result["pv_w"] == 0

    def test_missing_individual_fields_return_none(self):
        data = {"Site": {"P_PV": 1000.0}}
        with patch("requests.get", return_value=_ok(data)):
            result = client.get_power_flow()
        assert result["pv_w"] == 1000.0
        assert result["grid_w"] is None
        assert result["load_w"] is None


# ---------------------------------------------------------------------------
# get_meter
# ---------------------------------------------------------------------------

class TestGetMeter:
    def test_valid_response(self):
        with patch("requests.get", return_value=_ok(METER_DATA)):
            result = client.get_meter()
        assert result["power_w"] == -1500.0
        assert result["frequency_hz"] == 50.01
        assert result["voltage_l1_v"] == 231.2

    def test_missing_meter_returns_error(self):
        with patch("requests.get", return_value=_ok({})):
            result = client.get_meter()
        assert "error" in result
        assert "No smart meter" in result["error"]

    def test_missing_individual_fields_return_none(self):
        data = {"0": {"PowerReal_P_Sum": -800.0}}
        with patch("requests.get", return_value=_ok(data)):
            result = client.get_meter()
        assert result["power_w"] == -800.0
        assert result["power_l1_w"] is None
        assert result["frequency_hz"] is None


# ---------------------------------------------------------------------------
# get_battery
# ---------------------------------------------------------------------------

class TestGetBattery:
    def test_valid_response(self):
        with patch("requests.get", return_value=_ok(BATTERY_DATA)):
            result = client.get_battery()
        assert result["soc_pct"] == 87.5
        assert result["manufacturer"] == "BYD"
        assert result["model"] == "HVM 13.8"
        assert result["enabled"] is True

    def test_missing_battery_returns_error(self):
        with patch("requests.get", return_value=_ok({})):
            result = client.get_battery()
        assert "error" in result
        assert "No battery" in result["error"]

    def test_missing_controller_fields_return_none(self):
        data = {"0": {"Controller": {"Enable": 0, "Details": {}}}}
        with patch("requests.get", return_value=_ok(data)):
            result = client.get_battery()
        assert result["soc_pct"] is None
        assert result["enabled"] is False
        assert result["manufacturer"] is None

    def test_enable_false(self):
        data = {**BATTERY_DATA, "0": {
            **BATTERY_DATA["0"],
            "Controller": {**BATTERY_DATA["0"]["Controller"], "Enable": 0},
        }}
        with patch("requests.get", return_value=_ok(data)):
            result = client.get_battery()
        assert result["enabled"] is False


# ---------------------------------------------------------------------------
# get_devices
# ---------------------------------------------------------------------------

class TestGetDevices:
    def test_valid_response(self):
        data = {
            "Inverter": {"0": {"Serial": "12345678 "}},
            "Meter": {"0": {"Serial": "87654321"}},
            "Storage": [],
        }
        with patch("requests.get", return_value=_ok(data)):
            result = client.get_devices()
        assert result["inverter"][0]["serial"] == "12345678"  # stripped
        assert result["meter"][0]["serial"] == "87654321"
        assert result["storage"] == []

    def test_empty_system(self):
        with patch("requests.get", return_value=_ok({})):
            result = client.get_devices()
        assert result == {}


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    def test_api_error_code_raises(self):
        with patch("requests.get", return_value=_api_error(11, "Not supported")):
            with pytest.raises(RuntimeError, match="API Error 11"):
                client.get_power_flow()

    def test_http_error_raises(self):
        m = MagicMock()
        m.raise_for_status.side_effect = requests.HTTPError("404")
        with patch("requests.get", return_value=m):
            with pytest.raises(requests.HTTPError):
                client.get_power_flow()

    def test_network_timeout_raises(self):
        with patch("requests.get", side_effect=requests.Timeout):
            with pytest.raises(requests.Timeout):
                client.get_power_flow()
