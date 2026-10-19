#!/usr/bin/env python3
"""
Add page-reader results to sources/overrides.json.

PURPOSE: Reads JSON records from standard input, one per line, as
tools/read_datasafety_page.js returns them (long keys: pkg, name, developer, shared,
collected, noShared, noCollected, security, policy, missing; the earlier short keys p, n,
d, s, c, ns, nc, u, m are still accepted), and writes them into sources/overrides.json
with today's date and the source noted.
- The four Security practices statements are kept under "security" when the record has
  them; an older record without them is written with "security": null.
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


def normalise(r: dict) -> dict:
    """One shape for a record, whichever key style the page reader produced."""
    def pick(long_key, short_key, default=None):
        return r.get(long_key, r.get(short_key, default))
    return {
        "pkg": pick("pkg", "p"),
        "name": pick("name", "n"),
        "developer": pick("developer", "d"),
        "shared": pick("shared", "s", []),
        "collected": pick("collected", "c", []),
        "noShared": bool(pick("noShared", "ns", False)),
        "noCollected": bool(pick("noCollected", "nc", False)),
        "policy": pick("policy", "u"),
        "missing": bool(pick("missing", "m", False)),
        "security": r.get("security"),
    }


def main() -> int:
    today = dt.date.today().isoformat()
    over = json.loads(OVERRIDES.read_text(encoding="utf-8")) if OVERRIDES.exists() else {}
    added, skipped = [], []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        r = normalise(json.loads(line))
        if r["missing"]:
            skipped.append(r["pkg"])
            continue
        has_sections = r["shared"] or r["collected"] or r["noShared"] or r["noCollected"]
        declared = {"collected": r["collected"], "shared": r["shared"]} if has_sections else None
        over[r["pkg"]] = {
            "name": r["name"],
            "developer": r["developer"],
            "policyUrl": r["policy"],
            "readAt": today,
            "versionCode": None,
            "source": f"Play Store Data safety page, read {today} in the browser",
            "declared": declared,
            "security": r["security"],
        }
        added.append(r["pkg"])
    OVERRIDES.write_text(json.dumps(over, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    PACKAGES.write_text("# Apps the declarations file covers, one package name per line.\n" + "\n".join(sorted(over)) + "\n")
    print(f"added {len(added)}, total {len(over)}" + (f", skipped (no page): {', '.join(skipped)}" if skipped else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
