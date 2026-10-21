#!/usr/bin/env python3

import argparse
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE / "Shark_Sub_G030_RevB"
DEFAULT_NETLIST = PROJECT / "g030_export.net"
DEFAULT_CSV = HERE.parent / "V4_Buoy_5G8_2G4" / "g030_netlist_draft.csv"
DEFAULT_REPORT = HERE / "semantic_report.json"

PIN_RE = re.compile(r"^([A-Za-z0-9]+)-(\d+)\s+(\S+)\s+(\S+)\s*$")


EXPECTED = {
    "Q1": {
        1: ("S", "VBAT"),
        2: ("S", "VBAT"),
        3: ("S", "VBAT"),
        4: ("G", "PWR_GATE"),
        5: ("D", "VMOTOR"),
        6: ("D", "VMOTOR"),
        7: ("D", "VMOTOR"),
        8: ("D", "VMOTOR"),
    },
    "D1": {1: ("K", "+5V"), 2: ("A", "SW")},
    "U5": {
        1: ("SW", "SW"),
        2: ("GND", "GND"),
        3: ("FB", "FB"),
        4: ("EN", "VMOTOR"),
        5: ("IN", "VMOTOR"),
    },
    "U6": {
        1: ("IN", "+5V"),
        2: ("GND", "GND"),
        3: ("EN", "+5V"),
        5: ("OUT", "+3V3"),
    },
    "U2": {
        1: ("OUT2", "MAIN_OUT2"),
        2: ("GND", "GND"),
        3: ("OUT1", "MAIN_OUT1"),
        4: ("VCC", "VMOTOR"),
        5: ("IN1", "MAIN_IN1"),
        6: ("IN2", "MAIN_IN2"),
    },
    "U3": {
        1: ("OUT2", "LAT_OUT2"),
        2: ("GND", "GND"),
        3: ("OUT1", "LAT_OUT1"),
        4: ("VCC", "VMOTOR"),
        5: ("IN1", "LAT_IN1"),
        6: ("IN2", "LAT_IN2"),
    },
    "U4": {
        1: ("OUT2", "VERT_OUT2"),
        2: ("GND", "GND"),
        3: ("OUT1", "VERT_OUT1"),
        4: ("VCC", "VMOTOR"),
        5: ("IN1", "VERT_IN1"),
        6: ("IN2", "VERT_IN2"),
    },
    "C1": {1: ("1", "VMOTOR"), 2: ("2", "GND")},
    "C2": {1: ("1", "VMOTOR"), 2: ("2", "GND")},
    "C3": {1: ("1", "VMOTOR"), 2: ("2", "GND")},
}

U1_EXPECTED = {
    4: ("VDD/VDDA", "+3V3"),
    5: ("VSS/VSSA", "GND"),
    6: ("NRST", "NRST"),
    7: ("PA0", "BAT_SENSE"),
    8: ("PA1", "LEAK"),
    9: ("PA2", "TELEM_UP"),
    10: ("PA3", "BUOY_RX"),
    13: ("PA6", "VERT_IN1"),
    14: ("PA7", "VERT_IN2"),
    15: ("PB0", "LED_GPIO"),
    16: ("PB1", "JAW_SERVO"),
    18: ("PA8", "MAIN_IN1"),
    19: ("PA9", "MAIN_IN2"),
    21: ("PA10", "LAT_IN1"),
    22: ("PA11[PA9]", "LAT_IN2"),
    24: ("PA13", "SWDIO"),
    25: ("BOOT0", "SWCLK"),
}

NC_PINS = {
    "U5": {6},
    "U6": {4},
    "U1": {1, 2, 3, 11, 12, 17, 20, 23, 26, 27, 28, 29, 30, 31, 32},
}


def parse_protel(text):
    pins = {}
    errors = []
    in_netlist = False
    in_block = False
    net = None
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if line == "PROTEL NETLIST 2.0":
            in_netlist = True
            continue
        if not in_netlist:
            continue
        if line == "(":
            in_block = True
            net = None
            continue
        if in_block and net is None:
            net = line
            continue
        if in_block and line == ")":
            in_block = False
            net = None
            continue
        if not in_block:
            continue
        match = PIN_RE.match(line)
        if not match:
            continue
        ref, pin_text, pin_name, pin_type = match.groups()
        pin = int(pin_text)
        key = (ref.upper(), pin)
        if key in pins:
            errors.append(f"duplicate pin {ref}.{pin}")
            continue
        pins[key] = {"net": net, "name": pin_name, "type": pin_type, "line": number}
    return pins, errors


def retarget(text, moves):
    lines = text.splitlines(keepends=True)
    blocks = []
    current = None
    for index, line in enumerate(lines):
        if line.strip() == "(":
            current = {"header": index, "net": lines[index + 1].strip(), "end": None}
            blocks.append(current)
        elif line.strip() == ")" and current is not None:
            current["end"] = index
            current = None
    if not blocks:
        raise ValueError("no netlist blocks")
    pin_lines = {}
    for block in blocks:
        for index in range(block["header"], block["end"]):
            match = PIN_RE.match(lines[index].strip())
            if match:
                key = (match.group(1).upper(), int(match.group(2)))
                if key in moves:
                    pin_lines[key] = lines[index]
                    lines[index] = None
    for key in moves:
        if key not in pin_lines:
            raise ValueError(f"pin {key[0]}.{key[1]} not found")
    for key, target_net in moves.items():
        block = next((b for b in blocks if b["net"] == target_net), None)
        if block is None:
            raise ValueError(f"net {target_net} not found")
        lines[block["end"]] = pin_lines[key].rstrip("\r\n") + "\r\n" + lines[block["end"]]
    return "".join(line for line in lines if line is not None)


def read_csv_map(path):
    rows = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            ref = (row.get("RefDes") or "").strip().upper()
            pin = (row.get("Pin") or "").strip()
            net = (row.get("Net") or "").strip()
            if ref and pin.isdigit():
                rows[(ref, int(pin))] = net
    return rows


def verify(text, csv_path=None):
    pins, errors = parse_protel(text)
    warnings = []
    checked = 0
    for ref, expected in EXPECTED.items():
        for pin, (function, net) in expected.items():
            checked += 1
            actual = pins.get((ref, pin))
            if actual is None:
                errors.append(f"missing {ref}.{pin} ({function} -> {net})")
                continue
            if not actual["name"].endswith("-" + function):
                errors.append(
                    f"{ref}.{pin} function {function!r} does not match exported {actual['name']!r}"
                )
            if actual["net"] != net:
                errors.append(
                    f"{ref}.{pin} function {function} expected net {net!r}, found {actual['net']!r}"
                )
    for pin, (function, net) in U1_EXPECTED.items():
        checked += 1
        actual = pins.get(("U1", pin))
        if actual is None:
            errors.append(f"missing U1.{pin} ({function} -> {net})")
            continue
        if not actual["name"].endswith("-" + function):
            errors.append(
                f"U1.{pin} function {function!r} does not match exported {actual['name']!r}"
            )
        if actual["net"] != net:
            errors.append(
                f"U1.{pin} function {function} expected net {net!r}, found {actual['net']!r}"
            )
    for ref, nc_pins in NC_PINS.items():
        for pin in nc_pins:
            actual = pins.get((ref, pin))
            if actual is not None:
                errors.append(f"NC pin {ref}.{pin} is connected to {actual['net']!r}")
    if any(pins.get((ref, pin)) is None for ref, nc_pins in NC_PINS.items() for pin in nc_pins):
        warnings.append("NC pins are absent from the netlist but no explicit EDA NC flags were verified")

    csv_mismatches = []
    if csv_path is not None:
        csv_map = read_csv_map(csv_path)
        export_map = {key: value["net"] for key, value in pins.items()}
        for key in sorted(set(csv_map) | set(export_map)):
            if csv_map.get(key) != export_map.get(key):
                csv_mismatches.append(
                    {
                        "ref": key[0],
                        "pin": key[1],
                        "csv": csv_map.get(key),
                        "export": export_map.get(key),
                    }
                )
    return {
        "ok": not errors and not csv_mismatches,
        "releaseReady": False,
        "blockers": [
            "JLCEDA Pro GUI netlist re-export not performed",
            "DRC full log, grid alignment and explicit NC flags not completed",
            "PCB footprint cathode marking and first-power test not performed",
        ],
        "q1D1": {
            "Q1": "PASS" if not any(item.startswith("Q1.") for item in errors) else "FAIL",
            "D1": "PASS" if not any(item.startswith("D1.") for item in errors) else "FAIL",
        },
        "pinsParsed": len(pins),
        "netsParsed": len({value["net"] for value in pins.values()}),
        "pinsChecked": checked,
        "errors": errors,
        "warnings": warnings,
        "ncStatus": "UNMARKED" if warnings else "CHECKED",
        "csvMismatches": csv_mismatches,
        "csvPins": None if csv_path is None else len(read_csv_map(csv_path)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--netlist", type=Path, default=DEFAULT_NETLIST)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(args.netlist.read_text(encoding="utf-8", errors="replace"), args.csv)
    result["netlist"] = str(args.netlist)
    result["csv"] = str(args.csv)
    result["note"] = "Semantic physical-pin check; not EDA ERC/DRC. Export file must be GUI-regenerated before release."
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
