#!/usr/bin/env python3
"""Upload Photon to a Raspberry Pi Pico running MicroPython."""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path


PROJECT_ITEMS = ("drivers", "gui", "color_setup.py", "battery.py", "main.py")


def build_upload_commands(project_root: Path, port: str) -> list[list[str]]:
    connect = ["connect", port]
    return [
        connect + ["fs", "cp", "-r", str(project_root / "drivers"), ":"],
        connect + ["fs", "cp", "-r", str(project_root / "gui"), ":"],
        connect
        + ["fs", "cp", str(project_root / "color_setup.py"), ":color_setup.py"],
        connect + ["fs", "cp", str(project_root / "battery.py"), ":battery.py"],
        connect + ["fs", "cp", str(project_root / "main.py"), ":main.py"],
        connect + ["soft-reset"],
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--port",
        default="auto",
        help="serial device such as /dev/cu.usbmodem101 (default: auto)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="print commands without contacting the Pico"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    missing = [name for name in PROJECT_ITEMS if not (project_root / name).exists()]
    if missing:
        print(f"Missing project files: {', '.join(missing)}", file=sys.stderr)
        return 1

    prefix = [sys.executable, "-m", "mpremote"]
    commands = build_upload_commands(project_root, args.port)
    for command in commands:
        full_command = prefix + command
        print("+", shlex.join(full_command), flush=True)
        if not args.dry_run:
            subprocess.run(full_command, check=True)

    if not args.dry_run:
        print("Photon uploaded. The Pico was soft-reset and main.py is starting.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        print(
            "Upload failed. Check the USB cable, close serial monitors, and pass --port if auto-detection is ambiguous.",
            file=sys.stderr,
        )
        raise SystemExit(error.returncode) from error
