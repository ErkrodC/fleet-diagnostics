from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class TelemetryRecord:
    asset_id: str
    timestamp: datetime
    battery_temperature_c: float
    state_of_charge_pct: float
    is_online: bool


@dataclass(frozen=True, slots=True)
class DiagnosticFinding:
    asset_id: str
    code: str
    severity: Severity
    message: str
