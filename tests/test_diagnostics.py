import unittest
from datetime import UTC, datetime

from src.diagnostics import (
    CODE_ASSET_OFFLINE,
    CODE_HIGH_BATTERY_TEMPERATURE,
    CODE_LOW_STATE_OF_CHARGE,
    analyze_record,
    check_battery_temperature,
    check_online_status,
    check_state_of_charge
)
from src.models import Severity, TelemetryRecord


def make_record(
    temperature_c: float = 30.0,
    charge_pct: float = 60.0,
    online_status: bool = True
) -> TelemetryRecord:
    return TelemetryRecord(
        asset_id="bess-001",
        timestamp=datetime(2026, 7, 20, 12, 0, tzinfo=UTC),
        battery_temperature_c=temperature_c,
        state_of_charge_pct=charge_pct,
        is_online=online_status,
    )

class BatteryTemperatureTests(unittest.TestCase):
    def test_normal_temperature_has_no_finding(self) -> None:
        record = make_record(temperature_c=35.0)

        findings = check_battery_temperature(record)

        self.assertEqual([], findings)

    def test_temperature_above_threshold_is_critical(self) -> None:
        record = make_record(temperature_c=45.1)

        findings = check_battery_temperature(record)

        self.assertEqual(1, len(findings))
        self.assertEqual(CODE_HIGH_BATTERY_TEMPERATURE, findings[0].code)
        self.assertEqual(Severity.CRITICAL, findings[0].severity)
        self.assertIn("45.1 C", findings[0].message)

    def test_temperature_at_threshold_has_no_finding(self) -> None:
        record = make_record(temperature_c=45.0)

        findings = analyze_record(record)

        self.assertEqual([], findings)


class BatteryChargeTests(unittest.TestCase):
    def test_normal_charge_has_no_finding(self) -> None:
        record = make_record(charge_pct=100.0)

        findings = check_state_of_charge(record)

        self.assertEqual([], findings)

    def test_charge_below_threshold_has_warning_finding(self) -> None:
        record = make_record(charge_pct=5.0)

        findings = check_state_of_charge(record)

        self.assertEqual(1, len(findings))
        self.assertEqual(CODE_LOW_STATE_OF_CHARGE, findings[0].code)
        self.assertEqual(Severity.WARNING, findings[0].severity)
        self.assertIn("5.0%", findings[0].message)

    def test_charge_at_threshold_has_no_finding(self) -> None:
        record = make_record(charge_pct=10.0)

        findings = check_state_of_charge(record)

        self.assertEqual([], findings)


class BatteryOnlineStatusTests(unittest.TestCase):
    def test_online_status_has_no_finding(self) -> None:
        record = make_record(online_status=True)

        findings = check_online_status(record)

        self.assertEqual([], findings)

    def test_offline_status_has_critical_finding(self) -> None:
        record = make_record(online_status=False)

        findings = check_online_status(record)

        self.assertEqual(1, len(findings))
        self.assertEqual(CODE_ASSET_OFFLINE, findings[0].code)
        self.assertEqual(Severity.CRITICAL, findings[0].severity)


class BatteryMultipleFindingsTests(unittest.TestCase):
    def test_record_can_have_multiple_findings(self) -> None:
        record = make_record(temperature_c=45.1, charge_pct=9.9, online_status=False)

        findings = analyze_record(record)

        self.assertEqual(3, len(findings))
        self.assertEqual(
            {
                CODE_HIGH_BATTERY_TEMPERATURE,
                CODE_LOW_STATE_OF_CHARGE,
                CODE_ASSET_OFFLINE,
            },
            {finding.code for finding in findings}
        )

if __name__ == "__main__":
    unittest.main()
