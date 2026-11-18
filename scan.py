#!/usr/bin/env python3
"""Inventory WhatsApp media over ADB and classify reclaimable storage.

Read-only: this script never modifies the phone. It writes a Markdown report.
Requires: adb on PATH, phone connected and authorized (adb devices).
"""
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

BASE_CANDIDATES = [
    "/sdcard/Android/media/com.whatsapp/WhatsApp/Media",
    "/sdcard/WhatsApp/Media",
]
CATEGORIES = {
    "WhatsApp Images": "images",
    "WhatsApp Video": "videos",
    "WhatsApp Audio": "audio",
    "WhatsApp Voice Notes": "voice_notes",
    "WhatsApp Documents": "documents_report_only",
    ".Statuses": "status_downloads",
}
SENT_SUFFIX = "/Sent"


def adb(*args: str) -> str:
    out = subprocess.run(["adb", *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"adb {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout


def detect_base() -> str:
    for base in BASE_CANDIDATES:
        listing = adb("shell", "ls", base)
        if "WhatsApp" in listing or "Images" in listing or listing.strip():
            return base
    raise RuntimeError("WhatsApp media folder not found in known locations.")


def list_files(folder: str):
    """Yield (path, size_bytes) for every file under folder on the device."""
    raw = adb("shell", "find", folder, "-type", "f", "-exec", "stat", "-c", "%s", "{}", ";",
              "-print")
    lines = [l for l in raw.splitlines() if l.strip()]
    it = iter(lines)
    for size in it:
        path = next(it, None)
        if path is None:
            break
        try:
            yield path, int(size)
        except ValueError:
            continue


def hash_files(paths):
    """SHA-256 hashes computed on-device (fast, no multi-GB pull)."""
    hashes = {}
    for p in paths:
        h = adb("shell", "sha256sum", p).split()[0]
        hashes[p] = h
    return hashes


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def main() -> int:
    devices = adb("devices")
    if "\tdevice" not in devices:
        print("No authorized Android device found. Connect the phone, enable USB "
              "debugging, and approve the prompt on the phone.")
        return 1

    base = detect_base()
    run_dir = Path("runs") / datetime.now().strftime("%Y-%m-%d-%H%M")
    run_dir.mkdir(parents=True, exist_ok=True)

    totals = defaultdict(int)
    counts = defaultdict(int)
    all_files = []  # (path, size, category)
    for folder_name, category in CATEGORIES.items():
        folder = f"{base}/{folder_name}"
        try:
            files = list(list_files(folder))
        except RuntimeError:
            continue
        for path, size in files:
            cat = category
            if SENT_SUFFIX in path:
                cat = "sent_copies"
            totals[cat] += size
            counts[cat] += 1
            all_files.append((path, size, cat))

    # Exact duplicates by on-device hash (media only, skip report-only docs).
    hashable = [p for p, _, c in all_files if c != "documents_report_only"]
    hashes = hash_files(hashable)
    by_hash = defaultdict(list)
    size_of = {p: s for p, s, _ in all_files}
    for p, h in hashes.items():
        by_hash[h].append(p)
    dupe_bytes = 0
    dupe_files = 0
    flagged = set()  # files in the safe first pass, each counted once
    for h, paths in by_hash.items():
        if len(paths) > 1:
            dupe_files += len(paths) - 1
            dupe_bytes += size_of[paths[0]] * (len(paths) - 1)
            flagged.update(paths[1:])  # extra copies only, keep one original
    for p, s, c in all_files:
        if c in ("status_downloads", "sent_copies"):
            flagged.add(p)

    total = sum(totals.values())
    recoverable = sum(size_of[p] for p in flagged)

    lines = [
        "# CleanMyWhatsApp — Scan Report",
        f"Base: {base}",
        f"Total WhatsApp media: **{human(total)}** across {sum(len(v) for v in [counts]) and sum(counts.values())} files",
        "",
        "| Category | Files | Size |",
        "|---|---|---|",
    ]
    for cat in sorted(totals):
        lines.append(f"| {cat} | {counts[cat]} | {human(totals[cat])} |")
    lines += [
        "",
        f"Exact duplicates: {dupe_files} extra copies, **{human(dupe_bytes)}** reclaimable",
        f"Safe first pass (duplicates + status downloads + sent copies): "
        f"**~{human(recoverable)}**",
        "",
        "Nothing has been modified. Cleaning requires explicit approval per category,",
        "and every approved file is backed up to this computer and verified first.",
    ]
    report = "\n".join(lines)
    (run_dir / "report.md").write_text(report)
    (run_dir / "inventory.json").write_text(json.dumps(
        [{"path": p, "size": s, "category": c} for p, s, c in all_files], indent=1))
    print(report)
    print(f"\nReport saved to {run_dir}/report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
