#!/usr/bin/env python3

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NETLIST = ROOT / "g030_netlist_draft.csv"
PINOUT = ROOT / "control_pinout.csv"
RESULTS = HERE / "round7_design_test_results.json"


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def read_netmap(path):
    result = {}
    for row in read_csv(path):
        result[(row["RefDes"].strip().upper(), row["Pin"].strip())] = row["Net"].strip()
    return result


def read_pinout(path):
    return {(row["Port"].strip().upper()): row for row in read_csv(path)}


def expect(netmap, ref, pin, net):
    return netmap.get((ref, str(pin))) == net


def check_netmap(netmap, duplicate_pins=()):
    errors = []
    for ref, pin, net in duplicate_pins:
        if netmap.get((ref, pin)) not in (None, net):
            errors.append(f"{ref}.{pin} also on {net} (resource conflict)")
    for pin in ("1", "2", "3"):
        if not expect(netmap, "Q1", pin, "VBAT"):
            errors.append(f"Q1.{pin} must be VBAT")
    if not expect(netmap, "Q1", "4", "PWR_GATE"):
        errors.append("Q1.4 must be PWR_GATE")
    for pin in ("5", "6", "7", "8"):
        if not expect(netmap, "Q1", pin, "VMOTOR"):
            errors.append(f"Q1.{pin} must be VMOTOR")
    if not expect(netmap, "D1", "1", "+5V"):
        errors.append("D1.1 K must be +5V")
    if not expect(netmap, "D1", "2", "SW"):
        errors.append("D1.2 A must be SW")
    if not expect(netmap, "U1", "4", "+3V3"):
        errors.append("U1.4 must be +3V3")
    if not expect(netmap, "U1", "5", "GND"):
        errors.append("U1.5 must be GND")
    if not expect(netmap, "U4", "5", "VERT_IN1"):
        errors.append("U4.5 must be VERT_IN1")
    if not expect(netmap, "U4", "6", "VERT_IN2"):
        errors.append("U4.6 must be VERT_IN2")
    if not expect(netmap, "J7", "5", "PP_DOWN"):
        errors.append("J7.5 must be PP_DOWN / buoy-to-shark")
    if not expect(netmap, "J7", "6", "TELEM_UP"):
        errors.append("J7.6 must be TELEM_UP / shark-to-buoy")
    if not expect(netmap, "J8", "3", "SWDIO"):
        errors.append("J8.3 must be SWDIO")
    if not expect(netmap, "J8", "4", "SWCLK"):
        errors.append("J8.4 must be SWCLK")
    for key in (("U5", "6"), ("U6", "4")):
        if key in netmap:
            errors.append(f"{key[0]}.{key[1]} is NC but connected to {netmap[key]}")
    conflicts = {}
    for (ref, pin), net in netmap.items():
        if (ref, pin) in conflicts and conflicts[(ref, pin)] != net:
            errors.append(f"{ref}.{pin} on two nets")
        conflicts[(ref, pin)] = net
    return errors


def check_i2c(pinout):
    errors = []
    for port, signal in (("PB6", "I2C1_SCL"), ("PB7", "I2C1_SDA")):
        note = pinout.get(port, {}).get("Notes", "")
        if signal not in note:
            errors.append(f"{port} is not marked as {signal} candidate")
    for port in ("PA4", "PA5"):
        note = pinout.get(port, {}).get("Notes", "")
        if "NOT I2C" not in note:
            errors.append(f"{port} must be marked NOT I2C")
    return errors


def run_case(name, netmap, pinout, expected_ok, duplicate_pins=()):
    errors = check_netmap(netmap, duplicate_pins) + check_i2c(pinout)
    return {
        "name": name,
        "expected": "PASS" if expected_ok else "REJECT",
        "passed": (not errors) if expected_ok else bool(errors),
        "errors": errors,
    }


def copy_map(netmap):
    return dict(netmap)


def main():
    netmap = read_netmap(NETLIST)
    pinout = read_pinout(PINOUT)
    results = [run_case("baseline_static_rules", netmap, pinout, True)]

    swapped = copy_map(netmap)
    swapped[("Q1", "1")], swapped[("Q1", "4")] = swapped[("Q1", "4")], swapped[("Q1", "1")]
    results.append(run_case("q1_gate_source_swap", swapped, pinout, False))

    swapped = copy_map(netmap)
    swapped[("D1", "1")], swapped[("D1", "2")] = swapped[("D1", "2")], swapped[("D1", "1")]
    results.append(run_case("d1_anode_cathode_swap", swapped, pinout, False))

    wrong = copy_map(netmap)
    wrong[("U1", "4")] = "+5V"
    results.append(run_case("supply_voltage_wrong", wrong, pinout, False))

    results.append(run_case("mcu_pin_conflict", netmap, pinout, False, (("U1", "9", "BAT_SENSE"),)))

    wrong = copy_map(netmap)
    wrong[("U4", "5")], wrong[("U4", "6")] = wrong[("U4", "6")], wrong[("U4", "5")]
    results.append(run_case("vertical_motor_swap", wrong, pinout, False))

    wrong = copy_map(netmap)
    wrong[("J7", "5")], wrong[("J7", "6")] = wrong[("J7", "6")], wrong[("J7", "5")]
    results.append(run_case("j7_pp_telemetry_direction_swap", wrong, pinout, False))

    wrong = copy_map(netmap)
    wrong[("J8", "3")], wrong[("J8", "4")] = wrong[("J8", "4")], wrong[("J8", "3")]
    results.append(run_case("j8_swd_swap", wrong, pinout, False))

    wrong = copy_map(netmap)
    wrong[("U5", "6")] = "GND"
    results.append(run_case("u5_nc_missing", wrong, pinout, False))

    bad_pinout = dict(pinout)
    bad_pinout["PA4"] = dict(bad_pinout["PA4"], Notes="I2C1_SCL")
    results.append(run_case("i2c_on_pa4_rejected", netmap, bad_pinout, False))

    ok = all(item["passed"] for item in results)
    report = {
        "ok": ok,
        "category": "STATIC_NETLIST_AND_PINOUT_RULES",
        "note": "Static checks only; not GUI ERC/DRC, not footprint or physical test. I2C is a proposed PB6/PB7 interface, not present in RevB.",
        "tests": results,
    }
    RESULTS.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
