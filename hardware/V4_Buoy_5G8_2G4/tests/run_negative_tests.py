#!/usr/bin/env python3

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


TESTS = [
    ("short_led", "R7.2 moved onto LED_GPIO (shorted series resistor)", short_led),
    ("swap_q1_gate_source", "Q1 gate and source pins exchanged", swap_q1),
    ("swap_j7_video_power", "J7 pin1/pin3 nets exchanged", swap_j7),
    ("mcu_pin_two_nets", "U1.15 added to +3V3 while still on LED_GPIO", double_mcu_pin),
    ("missing_bom_part", "C15 removed from BOM", missing_bom),
    ("change_motor_power", "U2.4 moved from VMOTOR to VBAT", change_motor_power),
]


def main():
    results = []
    with tempfile.TemporaryDirectory(prefix="g030_negative_") as temp:
        temp = Path(temp)
        for name, description, mutate in TESTS:
            rows = read_csv(NETLIST)
            bom = read_csv(BOM)
            mutate(rows, bom)
            netlist_tmp = temp / f"{name}.csv"
            bom_tmp = temp / f"{name}_bom.csv"
            write_csv(netlist_tmp, rows)
            write_bom(bom_tmp, bom)
            proc = subprocess.run(
                [sys.executable, str(CHECKER), "--netlist", str(netlist_tmp), "--bom", str(bom_tmp), "--json"],
                capture_output=True,
                text=True,
            )
            try:
                payload = json.loads(proc.stdout)
            except json.JSONDecodeError:
                payload = {"errors": [proc.stdout.strip(), proc.stderr.strip()]}
            result = {
                "name": name,
                "mutation": description,
                "rejected": proc.returncode != 0,
                "exitCode": proc.returncode,
                "errors": payload.get("errors", []),
            }
            results.append(result)

    all_rejected = all(item["rejected"] for item in results)
    report = {
        "ok": all_rejected,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "checker": str(CHECKER),
        "note": "These are structural negative tests, not EDA ERC.",
        "tests": results,
    }
    RESULTS.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if all_rejected else 1


if __name__ == "__main__":
    sys.exit(main())
