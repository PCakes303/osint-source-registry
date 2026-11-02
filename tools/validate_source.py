#!/usr/bin/env python3
"""Validate a source record against the published schema and business rules."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "schemas/source-record.schema.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        for error in errors:
            print(f"ERROR: {list(error.absolute_path)}: {error.message}", file=sys.stderr)
        return 1
    print("OK: source record conforms to the published JSON Schema.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
