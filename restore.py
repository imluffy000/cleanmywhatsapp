#!/usr/bin/env python3
"""Restore a CleanMyWhatsApp backup run back to the phone.

Usage: python3 scripts/restore.py runs/<date>
Pushes runs/<date>/backup/ back to the original device paths recorded in
runs/<date>/inventory.json. Never deletes anything.
"""
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    run_dir = Path(sys.argv[1])
    backup = run_dir / "backup"
    inventory = json.loads((run_dir / "inventory.json").read_text())
    if not backup.exists():
        print(f"No backup found at {backup}")
        return 1
    restored = 0
    for item in inventory:
        local = backup / item["path"].lstrip("/")
        if local.exists():
            subprocess.run(["adb", "push", str(local), item["path"]], check=True)
            restored += 1
    print(f"Restored {restored} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
