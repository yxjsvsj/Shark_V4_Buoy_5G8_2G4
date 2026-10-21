#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import schematic_geometry

HERE = Path(__file__).resolve().parent
DEFAULT_PAGE = HERE / "sch" / "Schematic1" / "Shark_Sub_G030.esch2"
DEFAULT_MANIFEST = HERE / "schematic_geometry_manifest.json"
DEFAULT_REPORT = HERE / "geometry_report.json"


def read_records(path):
    records = []
    with path.open(encoding="utf-8", newline="") as handle:
        for number, raw in enumerate(handle, start=1):
            parts = raw.rstrip("\r\n").split("||")
            if len(parts) != 2:
                raise ValueError(f"{path}:{number}: expected one || separator")
            records.append((json.loads(parts[0]), json.loads(parts[1].rstrip("|\r\n"))))
    return records


def load_segments(path):
    records = read_records(path)
    net_by_wire = {}
    for outer, inner in records:
        if outer["type"] == "ATTR" and inner.get("key") == "NET":
            net_by_wire[inner.get("parentId")] = inner.get("value")
    segments = []
    for outer, inner in records:
        if outer["type"] != "LINE":
            continue
        net = net_by_wire.get(inner.get("lineGroup"))
        if net:
            segments.append(
                {
                    "ref": "LINE",
                    "pin": outer.get("id"),
                    "net": net,
                    "x1": inner["startX"],
                    "y1": inner["startY"],
                    "x2": inner["endX"],
                    "y2": inner["endY"],
                }
            )
    return segments


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--page", type=Path, default=DEFAULT_PAGE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    segments = load_segments(args.page)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = schematic_geometry.check(segments, manifest["pins"])
    result["page"] = str(args.page)
    result["manifest"] = str(args.manifest)
    result["note"] = "Geometry parsed from .esch2 LINE/NET records; pin coordinates from the generated manifest. Not EDA ERC."
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
