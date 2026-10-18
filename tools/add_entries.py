#!/usr/bin/env python3
"""
Add page-reader results to sources/overrides.json.

PURPOSE: Reads JSON records from standard input, one per line, as
tools/read_datasafety_page.js returns them (short keys: p package, n name, d developer,
s shared, c collected, ns no data shared, nc no data collected, m page missing, u policy),
and writes them into sources/overrides.json with today's date and the source noted.
- A page with neither a Data shared nor a Data collected section and no "no data" statement
  is written with "declared": null (looked up, nothing declared).
- A missing page is skipped and named.

Copyright (c) 2026 CYBERINE LLC. All rights reserved.
"""
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OVERRIDES = ROOT / "sources" / "overrides.json"
PACKAGES = ROOT / "sources" / "packages.txt"


def main() -> int:
    today = dt.date.today().isoformat()
    over = json.loads(OVERRIDES.read_text(encoding="utf-8")) if OVERRIDES.exists() else {}
    added, skipped = [], []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("m"):
            skipped.append(r["p"])
            continue
        has_sections = r["s"] or r["c"] or r.get("ns") or r.get("nc")
        declared = {"collected": r["c"], "shared": r["s"]} if has_sections else None
        over[r["p"]] = {
            "name": r["n"],
            "developer": r.get("d"),
            "policyUrl": r.get("u"),
            "readAt": today,
            "versionCode": None,
            "source": f"Play Store Data safety page, read {today} in the browser",
            "declared": declared,
        }
        added.append(r["p"])
    OVERRIDES.write_text(json.dumps(over, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    PACKAGES.write_text("# Apps the declarations file covers, one package name per line.\n" + "\n".join(sorted(over)) + "\n")
    print(f"added {len(added)}, total {len(over)}" + (f", skipped (no page): {', '.join(skipped)}" if skipped else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
