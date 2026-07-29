import argparse
from pathlib import Path

from src.diagnostics import analyze_record
from src.telemetry import load_telemetry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze fleet telemetry for diagnostic issues."
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to a JSON telemetry file."
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(f"Reading telemetry from: {args.input_file}")

    records = load_telemetry(args.input_file)
    findings = [
        finding
        for record in records
        for finding in analyze_record(record)
    ]

    print(f"Analyzed {len(records)} records: {len(findings)} findings.")
    for finding in findings:
        print(
            f"[{finding.severity.value}] {finding.asset_id} "
            f"{finding.code}: {finding.message}"
        )


if __name__ == "__main__":
    main()
