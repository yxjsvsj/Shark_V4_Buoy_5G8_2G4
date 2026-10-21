#!/usr/bin/env python3

import copy
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CHECKER = ROOT / "check_netlist.py"
NETLIST = ROOT / "g030_netlist_draft.csv"
BOM = ROOT / "control_bom.csv"
RESULTS = HERE / "negative_test_results.json"
G030 = ROOT.parent / "g030_control"
sys.path.insert(0, str(G030))

import schematic_geometry
import build_schematic_candidate as candidate
import check_schematic_geometry as page_geometry


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Net", "RefDes", "Pin", "Notes"])
        writer.writeheader()
        writer.writerows(rows)


def write_bom(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["Ref", "Qty", "Value/Part", "Package", "Notes"])
        writer.writeheader()
        writer.writerows(rows)


def find(rows, ref, pin):
    for row in rows:
        if row["RefDes"] == ref and row["Pin"] == str(pin):
            return row
    raise AssertionError(f"missing {ref}.{pin}")


def short_led(rows, bom):
    find(rows, "R7", 2)["Net"] = "LED_GPIO"


def swap_q1(rows, bom):
    gate = find(rows, "Q1", 1)
    source = find(rows, "Q1", 2)
    gate["Net"], source["Net"] = source["Net"], gate["Net"]


def swap_j7(rows, bom):
    find(rows, "J7", 1)["Net"] = "CVBS_VIDEO"
    find(rows, "J7", 3)["Net"] = "+5V"


def double_mcu_pin(rows, bom):
    rows.append({"Net": "+3V3", "RefDes": "U1", "Pin": "15", "Notes": "intentional duplicate"})


def missing_bom(rows, bom):
    bom[:] = [row for row in bom if row["Ref"] != "C15"]


def change_motor_power(rows, bom):
    find(rows, "U2", 4)["Net"] = "VBAT"


NETLIST_TESTS = [
    ("short_led", "R7.2 moved onto LED_GPIO (shorted series resistor)", short_led),
    ("swap_q1_gate_source", "Q1 gate and source pins exchanged", swap_q1),
    ("swap_j7_video_power", "J7 pin1/pin3 nets exchanged", swap_j7),
    ("mcu_pin_two_nets", "U1.15 added to +3V3 while still on LED_GPIO", double_mcu_pin),
    ("missing_bom_part", "C15 removed from BOM", missing_bom),
    ("change_motor_power", "U2.4 moved from VMOTOR to VBAT", change_motor_power),
]


def run_json(command):
    proc = subprocess.run(command, capture_output=True, text=True)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.returncode, None, proc.stdout.strip() + proc.stderr.strip()
    return proc.returncode, payload, None


def test_baseline():
    code, payload, parse_error = run_json([sys.executable, str(CHECKER), "--json"])
    return {
        "name": "baseline_netlist_pass",
        "category": "STRUCTURAL",
        "expected": "PASS",
        "passed": code == 0 and payload is not None and payload.get("ok") is True,
        "exitCode": code,
        "parseError": parse_error,
        "errors": [] if payload is None else payload.get("errors", []),
    }


def test_netlist_negative(name, description, mutate):
    rows = read_csv(NETLIST)
    bom = read_csv(BOM)
    mutate(rows, bom)
    with tempfile.TemporaryDirectory(prefix=f"g030_{name}_") as raw:
        temp = Path(raw)
        netlist_tmp = temp / "netlist.csv"
        bom_tmp = temp / "bom.csv"
        write_csv(netlist_tmp, rows)
        write_bom(bom_tmp, bom)
        code, payload, parse_error = run_json(
            [sys.executable, str(CHECKER), "--netlist", str(netlist_tmp), "--bom", str(bom_tmp), "--json"]
        )
    rejected = code != 0 and payload is not None and payload.get("ok") is False and bool(payload.get("errors"))
    return {
        "name": name,
        "category": "STRUCTURAL",
        "mutation": description,
        "expected": "REJECT",
        "passed": rejected,
        "exitCode": code,
        "parseError": parse_error,
        "errors": [] if payload is None else payload.get("errors", []),
    }


def load_geometry():
    manifest = json.loads((G030 / "schematic_geometry_manifest.json").read_text(encoding="utf-8"))
    return manifest["segments"], manifest["pins"]


def test_geometry_baseline():
    segments, pins = load_geometry()
    result = schematic_geometry.check(segments, pins)
    return {
        "name": "baseline_geometry_pass",
        "category": "GEOMETRY",
        "expected": "PASS",
        "passed": result["ok"] is True,
        "conflicts": result["conflicts"],
    }


def test_page_geometry_parse():
    segments = page_geometry.load_segments(
        G030 / "sch" / "Schematic1" / "Shark_Sub_G030.esch2"
    )
    nets = {item["net"] for item in segments}
    result = schematic_geometry.check(segments, load_geometry()[1])
    return {
        "name": "geometry_page_parse",
        "category": "GEOMETRY",
        "expected": "PASS",
        "passed": len(segments) == 137 and len(nets) == 32 and result["ok"] is True,
        "segments": len(segments),
        "nets": len(nets),
        "conflicts": result["conflicts"],
    }


def geometry_negative(name, mutation):
    segments, pins = load_geometry()
    bad_segments = copy.deepcopy(segments)
    mutation(bad_segments, pins)
    result = schematic_geometry.check(bad_segments, pins)
    return {
        "name": name,
        "category": "GEOMETRY",
        "expected": "REJECT",
        "passed": result["ok"] is False,
        "conflicts": result["conflicts"][:5],
    }


def make_overlap(segments, pins):
    a = next(s for s in segments if s["net"] == "VMOTOR")
    b = next(s for s in segments if s["net"] == "GND")
    b["y1"], b["y2"] = a["y1"], a["y2"]
    b["x1"] = a["x1"] + 5
    b["x2"] = a["x2"] + 5


def make_endpoint(segments, pins):
    a = next(s for s in segments if s["net"] == "VBAT")
    b = next(s for s in segments if s["net"] == "PWR_GATE")
    b["x1"], b["y1"] = a["x2"], a["y2"]


def make_pin_contact(segments, pins):
    a = next(s for s in segments if s["net"] == "VMOTOR")
    p = next(p for p in pins if p["net"] == "GND" and p["ref"] not in (a["ref"],))
    a["x2"], a["y2"] = p["x"], p["y"]


def test_metadata_mismatch():
    with tempfile.TemporaryDirectory(prefix="g030_meta_") as raw:
        temp = Path(raw)
        project = temp / "project.eprj3"
        ecfg = temp / "Schematic1.ecfg"
        page = temp / "page.esch2"
        shutil.copyfile(G030 / "Shark_Sub_G030.eprj3", project)
        shutil.copyfile(G030 / "sch" / "Schematic1" / "Schematic1.ecfg", ecfg)
        shutil.copyfile(G030 / "sch" / "Schematic1" / "Shark_Sub_G030.esch2", page)
        text = ecfg.read_text(encoding="utf-8").replace(candidate.BOARD_UUID, "deadbeefdeadbeef")
        ecfg.write_text(text, encoding="utf-8")
        result = candidate.validate_metadata(project, ecfg, page)
    return {
        "name": "metadata_uuid_mismatch",
        "category": "METADATA",
        "expected": "REJECT",
        "passed": result["ok"] is False and bool(result["errors"]),
        "errors": result["errors"],
    }


def test_footprint_blocked():
    report = json.loads((G030 / "schematic_candidate_report.json").read_text(encoding="utf-8"))
    footprint = report.get("categories", {}).get("FOOTPRINT")
    return {
        "name": "footprint_binding_status",
        "category": "FOOTPRINT",
        "expected": "BLOCKED",
        "passed": footprint == "BLOCKED",
        "reported": footprint,
    }


def main():
    results = [test_baseline()]
    for name, description, mutate in NETLIST_TESTS:
        results.append(test_netlist_negative(name, description, mutate))
    results.append(test_geometry_baseline())
    results.append(test_page_geometry_parse())
    results.append(geometry_negative("geometry_different_net_overlap", make_overlap))
    results.append(geometry_negative("geometry_different_net_endpoint", make_endpoint))
    results.append(geometry_negative("geometry_pin_contact", make_pin_contact))
    results.append(test_metadata_mismatch())
    results.append(test_footprint_blocked())

    all_passed = all(item["passed"] for item in results)
    report = {
        "ok": all_passed,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "categories": {
            "STRUCTURAL": "PASS" if all(x["passed"] for x in results if x["category"] == "STRUCTURAL") else "FAIL",
            "GEOMETRY": "PASS" if all(x["passed"] for x in results if x["category"] == "GEOMETRY") else "FAIL",
            "METADATA": "PASS" if all(x["passed"] for x in results if x["category"] == "METADATA") else "FAIL",
            "FOOTPRINT": "BLOCKED",
            "ERC": "NOT_RUN",
        },
        "note": "Structural, geometry and metadata tests; not EDA ERC. Footprint is explicitly BLOCKED.",
        "tests": results,
    }
    RESULTS.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\r\n")
    print(json.dumps(report, indent=2))
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
