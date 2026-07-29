import unittest
from datetime import UTC, datetime
from pathlib import Path

from src.telemetry import (
    telemetry_record_from_dict,
    load_telemetry,
)


class TelemetryRecordFromDictTests(unittest.TestCase):
    def test_converts_json_fields_to_record(self) -> None:
        data = {
            "asset_id": "bess-001",
            "timestamp": "2026-07-28T12:30:00Z",
            "battery_temperature_c": 35.2,
            "state_of_charge_pct": 67.5,
            "is_online": True,
        }

        record = telemetry_record_from_dict(data)

        self.assertEqual("bess-001", record.asset_id)
        self.assertEqual(35.2, record.battery_temperature_c)
        self.assertEqual(67.5, record.state_of_charge_pct)
        self.assertTrue(record.is_online)

    def test_converts_utc_timestamp_to_datetime(self) -> None:
        data = {
            "asset_id": "bess-001",
            "timestamp": "2026-07-28T12:30:00Z",
            "battery_temperature_c": 35.2,
            "state_of_charge_pct": 67.5,
            "is_online": True,
        }

        record = telemetry_record_from_dict(data)

        self.assertEqual(
            datetime(2026, 7, 28, 12, 30, tzinfo=UTC),
            record.timestamp,
        )

    def test_loads_sample_telemetry_data(self) -> None:
        path = "sample_data/telemetry.json"

        records = load_telemetry(Path(path))

        self.assertEqual(2, len(records))
        self.assertEqual(
            ["bess-001", "bess-002"],
            [record.asset_id for record in records],
        )
        self.assertEqual(48.7, records[1].battery_temperature_c)
        self.assertEqual(8.4, records[1].state_of_charge_pct)
        self.assertFalse(records[1].is_online)


if __name__ == "__main__":
    unittest.main()
