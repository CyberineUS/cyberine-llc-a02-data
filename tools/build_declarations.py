#!/usr/bin/env python3
"""
Build declarations.json.

PURPOSE: Reads the package list in sources/packages.txt and the hand-entered declarations in
sources/overrides.json, and writes declarations.json in format 1.
- An automatic source for Data safety declarations is not wired in. Reading Play Store pages
  automatically is against Google's terms; until counsel settles the source, or a licensed
  dataset is used, fetch_declaration() returns nothing and every entry comes from overrides.
- A package with no override is written with "declared": null and no readAt, so the app shows
  it as not on file.
- An override with "listing": "removed" records a Play Store page that no longer exists; the
  app shows that instead of a verdict.
- An override's "security" block (the four Security practices statements from the page) is
  carried through when present; the app treats a missing block as not read.
- tierByGroup gives each permission group its risk tier (1 highest) so the app's label rules
  can be tuned here without an app update; the app carries the same table as its default.

Copyright (c) 2026 CYBERINE LLC. All rights reserved.
"""
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKAGES = ROOT / "sources" / "packages.txt"
OVERRIDES = ROOT / "sources" / "overrides.json"
OUT = ROOT / "declarations.json"

TARGET_SDK = 37

# Android permission group (as the app names it) -> Play Store data types that would cover it.
DATA_TYPES_BY_GROUP = {
    "LOCATION": ["Location"],
    "CAMERA": ["Photos and videos"],
    "MICROPHONE": ["Audio"],
    "CONTACTS": ["Contacts"],
    "CALENDAR": ["Calendar"],
    "PHONE": ["Personal info", "Device or other IDs"],
    "CALL_LOG": ["Personal info"],
    "SMS": ["Messages"],
    "BODY_SENSORS": ["Health and fitness"],
    "ACTIVITY": ["Health and fitness"],
    "NEARBY_DEVICES": ["Device or other IDs"],
    "FILES_AND_MEDIA": ["Photos and videos", "Files and docs", "Audio"],
}

# Android permission group -> risk tier. 1 reaches conversations or the room, 2 personal data, 3 low on its own.
# LOCATION is the in-use tier; the app raises always-on location one step.
TIER_BY_GROUP = {
    "MICROPHONE": 1, "CAMERA": 1, "SMS": 1, "CALL_LOG": 1,
    "LOCATION": 2, "CONTACTS": 2, "PHONE": 2, "FILES_AND_MEDIA": 2, "BODY_SENSORS": 2, "CALENDAR": 2,
    "ACTIVITY": 3, "NEARBY_DEVICES": 3,
}


def fetch_declaration(package: str):
    """Automatic source. Not wired in: see the module docstring."""
    return None


def main() -> int:
    packages = [line.strip() for line in PACKAGES.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.startswith("#")]
    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8")) if OVERRIDES.exists() else {}
    apps = {}
    for package in sorted(set(packages) | set(overrides)):
        entry = overrides.get(package) or fetch_declaration(package)
        if entry is None:
            apps[package] = {"readAt": None, "declared": None}
            continue
        apps[package] = {
            "name": entry.get("name"),
            "developer": entry.get("developer"),
            "policyUrl": entry.get("policyUrl"),
            "readAt": entry["readAt"],
            "versionCode": entry.get("versionCode"),
            "listing": entry.get("listing", "present"),
            "declared": entry["declared"],
            "security": entry.get("security"),
        }
    on_file = sum(1 for a in apps.values() if a["declared"] is not None)
    document = {
        "format": 1,
        "generatedAt": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "sdk": TARGET_SDK,
        "source": {
            "declarations": "manual" if on_file else "none",
            "note": "Entries typed by hand from each app's Play Store page. No automatic source is in use.",
        },
        "dataTypesByGroup": DATA_TYPES_BY_GROUP,
        "tierByGroup": TIER_BY_GROUP,
        "apps": apps,
    }
    OUT.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name}: {len(apps)} apps, {on_file} with a declaration on file")
    return 0


if __name__ == "__main__":
    sys.exit(main())
