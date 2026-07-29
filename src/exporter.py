import argparse
import time
from pathlib import Path

import prometheus_client

from src.metrics import FleetMetrics
from src.models import TelemetryRecord
from src.telemetry import load_telemetry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Repeatedly loads/updates telemetry data"
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the telemetry file"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to serve the telemetry data on",
        required=False
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=15,
        help="Interval in seconds between each update",
        required=False
    )

    return parser.parse_args()

def main() -> None:
    args = parse_args()

    fleet_metrics: FleetMetrics = FleetMetrics()
    prometheus_client.start_http_server(args.port)

    try:
        while True:
            telemetry: list[TelemetryRecord] = load_telemetry(args.input_file)
            fleet_metrics.update_telemetry(telemetry)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()