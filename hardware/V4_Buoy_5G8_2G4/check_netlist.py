#!/usr/bin/env python3

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_NETLIST = HERE / "g030_netlist_draft.csv"
DEFAULT_BOM = HERE / "control_bom.csv"

ALIASES = {
    "3V3": "+3V3",
    "+3V3": "+3V3",
    "5V": "+5V",
    "+5V": "+5V",
    "JAW": "JAW_SERVO",
    "CAM_VIDEO": "CVBS_VIDEO",
    "BUOY_TX": "TELEM_UP",
    "BUOY_RX_J7": "PP_DOWN",
    "BUOY_RX_MCU": "BUOY_RX",
}


class Checker:
    def __init__(self, netlist_path, bom_path):
        self.netlist_path = netlist_path
        self.bom_path = bom_path
        self.errors = []
        self.warnings = []
        self.rows = []
        self.nets = defaultdict(list)
        self.pin_to_net = {}
        self.refs = set()
        self.bom_refs = set()
        self.bom_rows = {}

    def error(self, message):
        self.errors.append(message)

    def load(self):
        with self.netlist_path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            required = {"Net", "RefDes", "Pin", "Notes"}
            missing = required - set(reader.fieldnames or [])
            if missing:
                self.error(f"netlist missing columns: {', '.join(sorted(missing))}")
                return
            for line_no, row in enumerate(reader, start=2):
                net = (row.get("Net") or "").strip()
                ref = (row.get("RefDes") or "").strip().upper()
                pin = (row.get("Pin") or "").strip()
                notes = (row.get("Notes") or "").strip()
                if not net or not ref or not pin:
                    self.error(f"line {line_no}: empty Net/RefDes/Pin")
                    continue
                if not pin.isdigit():
                    self.error(f"line {line_no}: non-numeric pin {pin!r}")
                self.rows.append({"line": line_no, "net": net, "ref": ref, "pin": pin, "notes": notes})
                self.nets[net].append((ref, pin, line_no))
                key = (ref, pin)
                if key in self.pin_to_net and self.pin_to_net[key] != net:
                    self.error(f"{ref}.{pin} on two nets: {self.pin_to_net[key]}, {net}")
                self.pin_to_net[key] = net
                self.refs.add(ref)

        with self.bom_path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            required = {"Ref", "Qty", "Value/Part", "Package", "Notes"}
            missing = required - set(reader.fieldnames or [])
            if missing:
                self.error(f"BOM missing columns: {', '.join(sorted(missing))}")
                return
            for row in reader:
                ref = (row.get("Ref") or "").strip().upper()
                if not ref:
                    self.error("BOM row with empty Ref")
                    continue
                self.bom_refs.add(ref)
                self.bom_rows[ref] = row

    def check_structure(self):
        seen_rows = set()
        for item in self.rows:
            key = (item["net"], item["ref"], item["pin"])
            if key in seen_rows:
                self.error(f"line {item['line']}: duplicate row {item['ref']}.{item['pin']} on {item['net']}")
            seen_rows.add(key)
        for net, nodes in sorted(self.nets.items()):
            if len(nodes) < 2:
                self.error(f"net {net!r} has fewer than two nodes")
        for ref in sorted(self.refs - self.bom_refs):
            self.error(f"netlist ref {ref} is missing from BOM")
        for ref in sorted(self.bom_refs - self.refs - {"PCB"}):
            self.error(f"BOM ref {ref} is missing from netlist")

    def check_names(self):
        for net in sorted(self.nets):
            if net in ALIASES and net != ALIASES[net]:
                self.error(f"non-canonical net {net!r}; use {ALIASES[net]!r}")

    def expect(self, ref, pin, net):
        actual = self.pin_to_net.get((ref, pin))
        if actual != net:
            self.error(f"expected {ref}.{pin} on {net!r}, found {actual!r}")

    def check_required_connections(self):
        expected = [
            ("U1", "15", "LED_GPIO"),
            ("R7", "1", "LED_GPIO"),
            ("R7", "2", "LED_A"),
            ("LED1", "1", "LED_A"),
            ("LED1", "2", "GND"),
            ("U1", "16", "JAW_SERVO"),
            ("J5", "3", "JAW_SERVO"),
            ("U1", "9", "TELEM_UP"),
            ("J7", "6", "TELEM_UP"),
            ("U1", "10", "BUOY_RX"),
            ("R8", "2", "BUOY_RX"),
            ("R8", "1", "PP_DOWN"),
            ("J7", "5", "PP_DOWN"),
            ("J6", "3", "CVBS_VIDEO"),
            ("J7", "3", "CVBS_VIDEO"),
            ("U1", "4", "+3V3"),
            ("U1", "5", "GND"),
            ("U6", "1", "+5V"),
            ("U6", "2", "GND"),
            ("U6", "5", "+3V3"),
            ("Q1", "1", "VBAT"),
            ("Q1", "2", "VBAT"),
            ("Q1", "3", "VBAT"),
            ("Q1", "4", "PWR_GATE"),
            ("Q1", "5", "VMOTOR"),
            ("Q1", "6", "VMOTOR"),
            ("Q1", "7", "VMOTOR"),
            ("Q1", "8", "VMOTOR"),
            ("D1", "1", "+5V"),
            ("D1", "2", "SW"),
            ("U2", "1", "MAIN_OUT2"),
            ("U2", "2", "GND"),
            ("U2", "3", "MAIN_OUT1"),
            ("U2", "4", "VMOTOR"),
            ("U2", "5", "MAIN_IN1"),
            ("U2", "6", "MAIN_IN2"),
            ("U3", "1", "LAT_OUT2"),
            ("U3", "2", "GND"),
            ("U3", "3", "LAT_OUT1"),
            ("U3", "4", "VMOTOR"),
            ("U3", "5", "LAT_IN1"),
            ("U3", "6", "LAT_IN2"),
            ("U4", "1", "VERT_OUT2"),
            ("U4", "2", "GND"),
            ("U4", "3", "VERT_OUT1"),
            ("U4", "4", "VMOTOR"),
            ("U4", "5", "VERT_IN1"),
            ("U4", "6", "VERT_IN2"),
            ("U5", "1", "SW"),
            ("U5", "2", "GND"),
            ("U5", "3", "FB"),
            ("U5", "4", "VMOTOR"),
            ("U5", "5", "VMOTOR"),
            ("U6", "3", "+5V"),
            ("J5", "1", "+5V"),
            ("J5", "2", "GND"),
            ("J6", "1", "+5V"),
            ("J6", "2", "GND"),
            ("J7", "1", "+5V"),
            ("J7", "2", "GND"),
            ("J7", "4", "GND"),
            ("J8", "1", "+3V3"),
        ]
        for ref, pin, net in expected:
            self.expect(ref, pin, net)

    def check_led(self):
        if len(self.nets.get("LED_GPIO", [])) != 2:
            self.error("LED_GPIO must contain exactly U1.15 and R7.1")
        if len(self.nets.get("LED_A", [])) != 2:
            self.error("LED_A must contain exactly R7.2 and LED1.1")
        for net in ("+3V3", "+5V"):
            for ref, pin, _line in self.nets.get(net, []):
                if ref == "R7":
                    self.error(f"R7.{pin} must not be on {net}")

    def check_pin_counts(self):
        expected = {
            "Q1": {1, 2, 3, 4, 5, 6, 7, 8},
            "D1": {1, 2},
            "J7": {1, 2, 3, 4, 5, 6},
            "R7": {1, 2},
            "R8": {1, 2},
            "LED1": {1, 2},
            "J5": {1, 2, 3},
            "J6": {1, 2, 3},
        }
        for ref, expected_pins in expected.items():
            actual = {int(pin) for (r, pin) in self.pin_to_net if r == ref and pin.isdigit()}
            if actual != expected_pins:
                self.error(f"{ref} pins {sorted(actual)} do not match expected {sorted(expected_pins)}")

    def check_bom(self):
        q1 = self.bom_rows.get("Q1", {})
        if "SiSS23DN" not in q1.get("Value/Part", ""):
            self.error("Q1 BOM value must be SiSS23DN-T1-GE3")
        if "PowerPAK 1212-8S" not in q1.get("Package", ""):
            self.error("Q1 BOM package must be PowerPAK 1212-8S")
        j7 = self.bom_rows.get("J7", {})
        if "JST-PH" not in j7.get("Value/Part", ""):
            self.error("J7 BOM value must be JST-PH 6P")
        if "2.0mm" not in j7.get("Package", ""):
            self.error("J7 BOM package must be 2.0mm")
        l1 = self.bom_rows.get("L1", {})
        if "Isat 5.6A" not in l1.get("Notes", "") or "Irms 3.8A" not in l1.get("Notes", ""):
            self.error("L1 BOM notes must specify Isat 5.6A and Irms 3.8A")

    def run(self):
        self.load()
        if self.errors:
            return 1
        self.check_structure()
        self.check_names()
        self.check_required_connections()
        self.check_led()
        self.check_pin_counts()
        self.check_bom()
        return 1 if self.errors else 0

    def result(self):
        return {
            "ok": not self.errors,
            "netlist": str(self.netlist_path),
            "bom": str(self.bom_path),
            "rows": len(self.rows),
            "nets": len(self.nets),
            "refs": len(self.refs),
            "errors": self.errors,
            "warnings": self.warnings,
        }


def main():
    parser = argparse.ArgumentParser(description="Structural checker for the G030 draft netlist.")
    parser.add_argument("--netlist", type=Path, default=DEFAULT_NETLIST)
    parser.add_argument("--bom", type=Path, default=DEFAULT_BOM)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    checker = Checker(args.netlist, args.bom)
    status = checker.run()
    result = checker.result()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"netlist: {result['netlist']}")
        print(f"bom: {result['bom']}")
        print(f"rows={result['rows']} nets={result['nets']} refs={result['refs']}")
        if result["warnings"]:
            print("WARNINGS:")
            for warning in result["warnings"]:
                print(f"  - {warning}")
        if result["errors"]:
            print("ERRORS:")
            for error in result["errors"]:
                print(f"  - {error}")
        else:
            print("OK: structural checks passed (not an ERC)")
    return status


if __name__ == "__main__":
    sys.exit(main())
