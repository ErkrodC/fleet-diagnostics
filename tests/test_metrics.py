import unittest
from datetime import UTC, datetime

from prometheus_client import CollectorRegistry, generate_latest

from src.metrics import FleetMetrics
from src.models import TelemetryRecord


class FleetMetricsTests(unittest.TestCase):
    def test_exports_latest_telemetry_for_each_asset(self) -> None:
        registry = CollectorRegistry()
        metrics = FleetMetrics(registry)
        records = [
            TelemetryRecord(
                asset_id="bess-001",
                timestamp=datetime(2026, 7, 28, 12, 30, tzinfo=UTC),
                battery_temperature_c=35.2,
                state_of_charge_pct=67.5,
                is_online=True,
            ),
            TelemetryRecord(
                asset_id="bess-002",
                timestamp=datetime(2026, 7, 28, 12, 31, tzinfo=UTC),
                battery_temperature_c=48.7,
                state_of_charge_pct=8.4,
                is_online=False,
            ),
        ]

        metrics.update_telemetry(records)
        output = generate_latest(registry).decode("utf-8")

        self.assertIn(
            'fleet_battery_temperature_celsius{asset_id="bess-002"} 48.7',
            output,
        )
        self.assertIn(
            'fleet_state_of_charge_percent{asset_id="bess-001"} 67.5',
            output,
        )
        self.assertIn(
            'fleet_asset_online{asset_id="bess-001"} 1.0',
            output,
        )
        self.assertIn(
            'fleet_asset_online{asset_id="bess-002"} 0.0',
            output,
        )
        self.assertIn(
            (
                'fleet_diagnostic_finding{asset_id="bess-002",'
                'code="HIGH_BATTERY_TEMPERATURE",severity="critical"} 1.0'
            ),
            output,
        )
        self.assertIn(
            (
                'fleet_diagnostic_finding{asset_id="bess-002",'
                'code="LOW_STATE_OF_CHARGE",severity="warning"} 1.0'
            ),
            output,
        )
        self.assertIn(
            (
                'fleet_diagnostic_finding{asset_id="bess-002",'
                'code="ASSET_OFFLINE",severity="critical"} 1.0'
            ),
            output,
        )


if __name__ == "__main__":
    unittest.main()
