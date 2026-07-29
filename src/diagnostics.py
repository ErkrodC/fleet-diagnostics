from src.models import DiagnosticFinding, Severity, TelemetryRecord


MAX_BATTERY_TEMPERATURE_C = 45.0
MIN_BATTERY_CHARGE_PCT = 10.0

CODE_HIGH_BATTERY_TEMPERATURE = "HIGH_BATTERY_TEMPERATURE"
CODE_LOW_STATE_OF_CHARGE = "LOW_STATE_OF_CHARGE"
CODE_ASSET_OFFLINE = "ASSET_OFFLINE"


def check_battery_temperature(
    record: TelemetryRecord,
) -> list[DiagnosticFinding]:
    if record.battery_temperature_c <= MAX_BATTERY_TEMPERATURE_C:
        return []

    return [
        DiagnosticFinding(
            asset_id=record.asset_id,
            code=CODE_HIGH_BATTERY_TEMPERATURE,
            severity=Severity.CRITICAL,
            message=(
                f"Battery temperature is {record.battery_temperature_c:.1f} C; "
                f"maximum is {MAX_BATTERY_TEMPERATURE_C:.1f} C."
            ),
        )
    ]


def check_state_of_charge(
    record: TelemetryRecord
) -> list[DiagnosticFinding]:
    if record.state_of_charge_pct >= MIN_BATTERY_CHARGE_PCT:
        return []

    return [
        DiagnosticFinding(
            asset_id=record.asset_id,
            code=CODE_LOW_STATE_OF_CHARGE,
            severity=Severity.WARNING,
            message=(
                f"Battery charge is {record.state_of_charge_pct:.1f}%; "
                f"warning threshold is {MIN_BATTERY_CHARGE_PCT:.1f}%."
            )
        )
    ]


def check_online_status(
    record: TelemetryRecord
) -> list[DiagnosticFinding]:
    if record.is_online: return []

    return [
        DiagnosticFinding(
            asset_id=record.asset_id,
            code=CODE_ASSET_OFFLINE,
            severity=Severity.CRITICAL,
            message=f"Asset {record.asset_id} is offline."
        )
    ]


def analyze_record(record: TelemetryRecord) -> list[DiagnosticFinding]:
    findings: list[DiagnosticFinding] = []

    findings.extend(check_battery_temperature(record))
    findings.extend(check_state_of_charge(record))
    findings.extend(check_online_status(record))

    return findings
