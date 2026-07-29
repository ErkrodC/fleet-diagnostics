from datetime import datetime
from pathlib import Path
from typing import Any

import json

from src.models import TelemetryRecord


def telemetry_record_from_dict(data: dict[str, Any]) -> TelemetryRecord:
    timestamp_text: str = data["timestamp"]
    if timestamp_text.endswith("Z"):
        timestamp_text = f"{timestamp_text[:-1]}+00:00"

    return TelemetryRecord(
        asset_id=data["asset_id"],
        timestamp=datetime.fromisoformat(timestamp_text),
        battery_temperature_c=data["battery_temperature_c"],
        state_of_charge_pct=data["state_of_charge_pct"],
        is_online=data["is_online"],
    )


def load_telemetry(path: Path) -> list[TelemetryRecord]:
    with path.open(encoding="utf-8") as file:
        items: list[dict[str, Any]] = json.load(file)

    return [telemetry_record_from_dict(item) for item in items]
