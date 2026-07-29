from prometheus_client import CollectorRegistry, Gauge, REGISTRY

from src.diagnostics import analyze_record
from src.models import TelemetryRecord


class FleetMetrics:
    def __init__(self, registry: CollectorRegistry = REGISTRY) -> None:
        self.battery_temperature = Gauge(
            "fleet_battery_temperature_celsius",
            "Latest battery temperature in degrees Celsius.",
            labelnames=["asset_id"],
            registry=registry,
        )
        self.state_of_charge = Gauge(
            "fleet_state_of_charge_percent",
            "Latest battery state of charge as a percentage.",
            labelnames=["asset_id"],
            registry=registry,
        )
        self.asset_online = Gauge(
            "fleet_asset_online",
            "Whether the asset is online (1) or offline (0).",
            labelnames=["asset_id"],
            registry=registry,
        )
        self.diagnostic_finding = Gauge(
            "fleet_diagnostic_finding",
            "Whether a diagnostic finding is currently active.",
            labelnames=["asset_id", "code", "severity"],
            registry=registry,
        )

    def update_telemetry(self, records: list[TelemetryRecord]) -> None:
        self.battery_temperature.clear()
        self.state_of_charge.clear()
        self.asset_online.clear()
        self.diagnostic_finding.clear()

        for record in records:
            labels = {"asset_id": record.asset_id}
            self.battery_temperature.labels(**labels).set(
                record.battery_temperature_c
            )
            self.state_of_charge.labels(**labels).set(
                record.state_of_charge_pct
            )
            self.asset_online.labels(**labels).set(
                1 if record.is_online else 0
            )

            for finding in analyze_record(record):
                self.diagnostic_finding.labels(
                    asset_id=finding.asset_id,
                    code=finding.code,
                    severity=finding.severity.value,
                ).set(1)
