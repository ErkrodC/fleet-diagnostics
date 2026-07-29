# Fleet Diagnostics

![Fleet Diagnostics dashboard](./Dashboard.png)

Fleet Diagnostics is a small, production-oriented Python prototype for
observing a Battery Energy Storage System (BESS) fleet. It ingests timestamped
telemetry, evaluates deterministic fault rules, exposes Prometheus metrics, and
ships with a provisioned Grafana dashboard.

## Architecture

```text
JSON telemetry → Python diagnostics → Prometheus metrics → Grafana
                       └────────────→ CLI findings
```

Prometheus pulls current values from the exporter every five seconds and stores
them as time series. Grafana queries Prometheus and visualizes both raw
telemetry and derived diagnostic state.

## Diagnostic rules

| Code | Condition | Severity |
|---|---|---|
| `HIGH_BATTERY_TEMPERATURE` | Temperature above 45 C | Critical |
| `LOW_STATE_OF_CHARGE` | State of charge below 10% | Warning |
| `ASSET_OFFLINE` | Asset reports offline | Critical |

Rules are implemented as pure functions so they are deterministic and easy to
unit test. Threshold boundary behavior is explicitly tested.

## Quick start with Docker

Prerequisites:

- Docker Desktop with Docker Compose
- Ports 3000, 8000, and 9090 available

Start the stack:

```powershell
docker compose up -d --build
```

Open:

- Grafana dashboard: <http://localhost:3000/d/fleet-overview/fleet-overview>
- Prometheus targets: <http://localhost:9090/targets>
- Exporter metrics: <http://localhost:8000/metrics>

The local Grafana credentials are `admin` / `admin`. These credentials are only
appropriate for this local demonstration.

Edit `sample_data/telemetry.json` and allow about 20 seconds for the exporter, Prometheus, and Grafana refresh cycles.

Stop the stack:

```powershell
docker compose down
```

## Local Python usage

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the diagnostic CLI:

```powershell
python -m src.main sample_data/telemetry.json
```

Run the exporter without Docker:

```powershell
python -m src.exporter sample_data/telemetry.json --port 8000 --interval 15
```

Run the tests:

```powershell
python -m unittest discover -s tests -v
```

## Exported metrics

| Metric | Type | Labels | Meaning |
|---|---|---|---|
| `fleet_battery_temperature_celsius` | Gauge | `asset_id` | Latest temperature |
| `fleet_state_of_charge_percent` | Gauge | `asset_id` | Latest state of charge |
| `fleet_asset_online` | Gauge | `asset_id` | Online `1`, offline `0` |
| `fleet_diagnostic_finding` | Gauge | `asset_id`, `code`, `severity` | Active finding |

Gauges are used because these values can rise, fall, or clear. A "finding" metric includes the asset ID, a short problem code, and its severity. A "Finding"'s message attribute is not used as a label to keep the number of time series manageable.

## Repository layout

```text
src/
  diagnostics.py   Pure diagnostic rules
  exporter.py      Long-running Prometheus exporter
  main.py          One-shot diagnostic CLI
  metrics.py       Prometheus metric definitions
  models.py        Typed telemetry and finding models
  telemetry.py     JSON ingestion
tests/              Unit and integration tests
sample_data/        Editable demonstration telemetry
observability/      Prometheus and Grafana configuration
compose.yaml        Local three-service stack
Dockerfile          Exporter image
```

## Operations

See [RUNBOOK.md](./docs/RUNBOOK.md) for service checks, logs, connectivity
tests, resource diagnostics, common symptoms, and recovery verification.

## Current limitations

- Input structure and value ranges are not validated.
- Timestamps are parsed but telemetry staleness is not yet diagnosed.
- The exporter polls a local JSON file instead of a DAS, Modbus device, or API.
- Thresholds are compiled into the application rather than externally
  configured.
- Application logging is minimal.