#!/usr/bin/env python3
"""Read-only filesystem size inventory for an Unreal project.

Usage:
    python Tools/asset_budget_audit.py --project . --output AuditOutput

Outputs CSV and JSON. Does not open or modify .uasset/.umap, does not alter
asset references, and does not require Unreal Engine.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

CATEGORIES = {
    ".uasset": "Unreal asset",
    ".umap": "Unreal map",
    ".ini": "Config",
    ".uproject": "Project",
}
GENERATED = {"Saved", "Intermediate", "Binaries", "DerivedDataCache"}
LIMIT_BYTES = 20 * 1024**3
TARGET_BYTES = 5 * 1024**3

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("AuditOutput"))
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    if not (root / "L1.uproject").exists():
        parser.error("Expected L1.uproject in the project root")
    out = args.output
    if not out.is_absolute():
        out = root / out
    out = out.resolve()
    if out == root:
        parser.error("Output folder must not be the project root")
    # Capture inventory before writing any report.
    rows = []
    for f in root.rglob("*"):
        if not f.is_file() or f == out or out in f.parents or ".git" in f.relative_to(root).parts:
            continue
        rel = f.relative_to(root)
        rows.append({"path": rel.as_posix(), "bytes": f.stat().st_size,
                     "group": "generated" if rel.parts[0] in GENERATED else "source",
                     "kind": CATEGORIES.get(f.suffix.lower(), f.suffix.lower() or "(none)")})
    rows.sort(key=lambda r: r["bytes"], reverse=True)
    totals = defaultdict(int)
    for row in rows:
        totals[row["group"]] += row["bytes"]
    summary = {
        "file_count": len(rows),
        "source_bytes": totals["source"],
        "generated_bytes": totals["generated"],
        "total_bytes": sum(r["bytes"] for r in rows),
        "source_target_bytes": TARGET_BYTES,
        "source_hard_cap_bytes": LIMIT_BYTES,
        "under_hard_cap": totals["source"] <= LIMIT_BYTES,
        "note": "Disk sizes are not runtime RAM/VRAM or packaged build sizes.",
    }
    out.mkdir(parents=True, exist_ok=True)
    with (out / "asset_inventory.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "bytes", "group", "kind"])
        writer.writeheader()
        writer.writerows(rows)
    (out / "size_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Saved {out / 'asset_inventory.csv'} and {out / 'size_summary.json'}")

if __name__ == "__main__":
    main()
