#!/usr/bin/env python3

import csv
import hashlib
import json
import math
import re
from pathlib import Path

import schematic_geometry

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "V4_Buoy_5G8_2G4"
NETLIST = SRC / "g030_netlist_draft.csv"
BOM = SRC / "control_bom.csv"
PROJECT = HERE / "Shark_Sub_G030.eprj3"
PAGE = HERE / "sch" / "Schematic1" / "Shark_Sub_G030.esch2"
ECFG = PAGE.parent / "Schematic1.ecfg"
REPORT = HERE / "schematic_candidate_report.json"
GEOMETRY_REPORT = HERE / "geometry_report.json"
MANIFEST = HERE / "schematic_geometry_manifest.json"
PREVIEW = HERE / "schematic_candidate.svg"

BOARD_UUID = "a1b2c3d4e5f60718"
SCH_UUID = "b2c3d4e5f6071829"
PAGE_UUID = "c3d4e5f60718293a"
CLIENT = "g030-candidate"

counter = 0
ticket_counter = 1000
ids = set()


def next_ticket():
    global ticket_counter
    ticket_counter += 1
    return ticket_counter


def new_id(prefix):
    global counter
    while True:
        counter += 1
        value = hashlib.sha1(f"{prefix}:{counter}".encode()).hexdigest()[:16]
        if value not in ids:
            ids.add(value)
            return value


def line(record_type, body, ticket, record_id=None):
    outer = {"type": record_type, "ticket": ticket}
    if record_id:
        outer["id"] = record_id
    return json.dumps(outer, separators=(",", ":")) + "||" + json.dumps(body, separators=(",", ":")) + "|"


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def pin_names(ref):
    if ref == "U1":
        return {
            1: "PB9", 2: "PC14", 3: "PC15", 4: "VDD/VDDA", 5: "VSS/VSSA", 6: "NRST",
            7: "PA0", 8: "PA1", 9: "PA2", 10: "PA3", 11: "PA4", 12: "PA5",
            13: "PA6", 14: "PA7", 15: "PB0", 16: "PB1", 17: "PB2", 18: "PA8",
            19: "PA9", 20: "PC6", 21: "PA10", 22: "PA11", 23: "PA12", 24: "PA13",
            25: "PA14", 26: "PA15", 27: "PB3", 28: "PB4", 29: "PB5", 30: "PB6",
            31: "PB7", 32: "PB8",
        }
    if ref in ("U2", "U3", "U4"):
        return {1: "OUT2", 2: "GND", 3: "OUT1", 4: "VCC", 5: "IN1", 6: "IN2"}
    if ref == "U5":
        return {1: "SW", 2: "GND", 3: "FB", 4: "EN", 5: "VIN", 6: "NC"}
    if ref == "U6":
        return {1: "IN", 2: "GND", 3: "EN", 4: "NC", 5: "OUT"}
    if ref == "Q1":
        return {1: "S", 2: "S", 3: "S", 4: "G", 5: "D", 6: "D", 7: "D", 8: "D"}
    if ref == "J7":
        return {1: "+5V", 2: "GND", 3: "CVBS", 4: "GND", 5: "PP_DOWN", 6: "TELEM_UP"}
    if ref in ("J5", "J6"):
        return {1: "+5V", 2: "GND", 3: "SIG"}
    if ref == "J8":
        return {1: "+3V3", 2: "GND", 3: "SWDIO", 4: "SWCLK", 5: "NRST"}
    if ref in ("J1", "J2", "J3", "J4", "J9"):
        return {1: "1", 2: "2"}
    if ref == "D1":
        return {1: "K", 2: "A"}
    if ref == "LED1":
        return {1: "A", 2: "K"}
    if ref == "SW1":
        return {1: "1", 2: "2"}
    return {1: "1", 2: "2"}


def symbol_kind(ref):
    if ref == "U1":
        return "g030"
    if ref in ("U2", "U3", "U4"):
        return "mx113h"
    if ref == "U5":
        return "mt3608"
    if ref == "U6":
        return "tlv70033"
    if ref == "Q1":
        return "pmos"
    if ref == "J7":
        return "conn6"
    if ref == "J8":
        return "conn5"
    if ref in ("J5", "J6"):
        return "conn3"
    if ref in ("J1", "J2", "J3", "J4", "J9"):
        return "conn2"
    if ref.startswith("R"):
        return "res"
    if ref.startswith("C"):
        return "cap"
    if ref == "L1":
        return "ind"
    if ref == "D1":
        return "diode"
    if ref == "LED1":
        return "led"
    if ref == "SW1":
        return "sw"
    raise ValueError(ref)


def symbol_geometry(kind):
    if kind == "g030":
        return 100, 180, 20
    if kind in ("mx113h", "mt3608", "pmos"):
        return 60, 80, 15
    if kind == "tlv70033":
        return 55, 70, 15
    if kind == "conn6":
        return 50, 80, 15
    if kind == "conn5":
        return 50, 70, 15
    if kind == "conn3":
        return 45, 55, 15
    if kind == "conn2":
        return 40, 35, 12
    return 20, 12, 10


def pin_sides(kind, pins):
    count = len(pins)
    if kind == "g030":
        return {p: ("left" if p <= 16 else "right") for p in pins}
    if count == 2:
        return {pins[0]: "left", pins[1]: "right"}
    if count == 3:
        return {pins[0]: "left", pins[1]: "left", pins[2]: "right"}
    if count == 5:
        return {p: ("left" if i < 3 else "right") for i, p in enumerate(pins)}
    if count == 6:
        return {p: ("left" if i < 3 else "right") for i, p in enumerate(pins)}
    if count == 8:
        return {p: ("left" if i < 4 else "right") for i, p in enumerate(pins)}
    return {p: "left" for p in pins}


def pin_y_positions(side_pins, half_h):
    n = len(side_pins)
    if n == 0:
        return {}
    if n == 1:
        return {side_pins[0]: 0}
    spacing = 20 if half_h >= 80 else 10
    start = (n - 1) * spacing / 2
    return {pin: start - i * spacing for i, pin in enumerate(side_pins)}


def make_symbol(kind, ref_for_names):
    names = pin_names(ref_for_names)
    pins = sorted(names)
    half_w, half_h, pin_len = symbol_geometry(kind)
    sides = pin_sides(kind, pins)
    left = [p for p in pins if sides[p] == "left"]
    right = [p for p in pins if sides[p] == "right"]
    ys = {}
    ys.update(pin_y_positions(left, half_h))
    ys.update(pin_y_positions(right, half_h))
    geometry = {}
    for p in pins:
        side = sides[p]
        y = ys[p]
        if side == "left":
            geometry[p] = (-half_w - pin_len, y, 0)
        else:
            geometry[p] = (half_w + pin_len, y, 180)
    return {"kind": kind, "names": names, "pins": pins, "geometry": geometry, "half_w": half_w, "half_h": half_h, "pin_len": pin_len}


def symbol_uuid(kind):
    return hashlib.sha1(f"SYMBOL:{kind}".encode()).hexdigest()[:16]


def device_uuid(ref):
    return hashlib.sha1(f"DEVICE:{ref}".encode()).hexdigest()[:16]


def emit_symbol(kind, template_ref, out, tickets):
    sym = make_symbol(kind, template_ref)
    uid = symbol_uuid(kind)
    part_id = f"SYM_{kind}.1"
    out.append(line("DOCHEAD", {"docType": "SYMBOL", "client": CLIENT, "uuid": uid}, next_ticket()))
    out.append(line("META", {"title": f"SYM_{kind}", "description": "", "tags": ["candidate"], "docType": 2, "source": ""}, next_ticket()))
    out.append(line("CANVAS", {"originX": 0, "originY": 0, "yAxisDirection": "up"}, next_ticket(), "CANVAS"))
    out.append(line("PART", {"BBOX": [-sym["half_w"], -sym["half_h"], sym["half_w"], sym["half_h"]], "title": part_id}, next_ticket(), part_id))
    out.append(line("ATTR", {"partId": part_id, "groupId": "", "locked": False, "zIndex": 1, "parentId": "", "key": "Symbol", "value": f"SYM_{kind}", "keyVisible": False, "valueVisible": False, "x": None, "y": None, "rotation": 0, "color": None, "fillColor": None, "fontFamily": None, "fontSize": None, "strikeout": False, "underline": False, "italic": False, "fontWeight": False, "align": "LEFT_BOTTOM", "version": "2.0", "yAxisDirection": "up"}, next_ticket(), new_id("attr")))
    out.append(line("ATTR", {"partId": part_id, "groupId": "", "locked": False, "zIndex": 2, "parentId": "", "key": "Designator", "value": "U?", "keyVisible": False, "valueVisible": False, "x": None, "y": None, "rotation": 0, "color": None, "fillColor": None, "fontFamily": None, "fontSize": None, "strikeout": False, "underline": False, "italic": False, "fontWeight": False, "align": "LEFT_BOTTOM", "version": "2.0", "yAxisDirection": "up"}, next_ticket(), new_id("attr")))
    out.append(line("RECT", {"partId": part_id, "groupId": "", "locked": False, "zIndex": 3, "dotX1": -sym["half_w"], "dotY1": -sym["half_h"], "dotX2": sym["half_w"], "dotY2": sym["half_h"], "radiusX": 0, "radiusY": 0, "rotation": 0, "strokeColor": "#333333", "strokeStyle": None, "fillColor": "#FFF8D8", "strokeWidth": None, "fillStyle": 1, "yAxisDirection": "up"}, next_ticket(), new_id("rect")))
    for p in sym["pins"]:
        x, y, rotation = sym["geometry"][p]
        pin_id = new_id("pin")
        out.append(line("PIN", {"partId": part_id, "groupId": "", "locked": False, "zIndex": 4, "display": True, "x": x, "y": y, "length": sym["pin_len"], "rotation": rotation, "color": None, "pinShape": "NONE", "yAxisDirection": "up"}, next_ticket(), pin_id))
        out.append(line("ATTR", {"partId": part_id, "groupId": "", "locked": False, "zIndex": 5, "parentId": pin_id, "key": "Pin Name", "value": sym["names"][p], "keyVisible": False, "valueVisible": True, "x": x, "y": y - 2, "rotation": 0, "color": None, "fillColor": None, "fontFamily": None, "fontSize": 6.75, "strikeout": False, "underline": False, "italic": False, "fontWeight": False, "align": "LEFT_BOTTOM", "version": "2.0", "yAxisDirection": "up"}, next_ticket(), new_id("attr")))
        out.append(line("ATTR", {"partId": part_id, "groupId": "", "locked": False, "zIndex": 6, "parentId": pin_id, "key": "Pin Number", "value": str(p), "keyVisible": False, "valueVisible": True, "x": x, "y": y + 2, "rotation": 0, "color": None, "fillColor": None, "fontFamily": None, "fontSize": 6.75, "strikeout": False, "underline": False, "italic": False, "fontWeight": False, "align": "RIGHT_BOTTOM", "version": "2.0", "yAxisDirection": "up"}, next_ticket(), new_id("attr")))
        out.append(line("ATTR", {"partId": part_id, "groupId": "", "locked": False, "zIndex": 7, "parentId": pin_id, "key": "Pin Type", "value": "Undefined", "keyVisible": False, "valueVisible": False, "x": x, "y": y, "rotation": 0, "color": None, "fillColor": None, "fontFamily": None, "fontSize": None, "strikeout": False, "underline": False, "italic": False, "fontWeight": False, "align": "LEFT_BOTTOM", "version": "2.0", "yAxisDirection": "up"}, next_ticket(), new_id("attr")))
    return {"uid": uid, "part_id": part_id, "geometry": sym["geometry"], "names": sym["names"], "half_w": sym["half_w"], "half_h": sym["half_h"]}


def emit_device(ref, row, symbol, out, tickets):
    uid = device_uuid(ref)
    value = row.get("Value/Part", "")
    package = row.get("Package", "")
    notes = row.get("Notes", "")
    attributes = {
        "Designator": ref,
        "Value": value,
        "Footprint": package,
        "Symbol": symbol["uid"],
        "Manufacturer Part": value,
        "Supplier Part": notes,
        "Description": "G030 candidate schematic; footprint binding not GUI-verified",
    }
    out.append(line("DOCHEAD", {"docType": "DEVICE", "client": CLIENT, "uuid": uid}, next_ticket()))
    out.append(line("META", {"title": ref, "tags": ["candidate"], "source": "", "images": [], "attributes": attributes}, next_ticket(), "META"))
    return uid


def place_components(refs):
    positions = {}
    for i, ref in enumerate(refs):
        col = i % 8
        row = i // 8
        positions[ref] = (350 + col * 500, 2700 - row * 380)
    return positions


def attr(part_id, key, value, x=None, y=None, z=0):
    return line("ATTR", {"x": x, "y": y, "rotation": 0, "color": None, "fontFamily": None, "fontSize": None, "fontWeight": None, "italic": None, "underline": None, "align": None, "value": value, "keyVisible": None, "valueVisible": None, "key": key, "fillColor": None, "parentId": part_id, "zIndex": z, "locked": False, "yAxisDirection": "up"}, next_ticket(), new_id("attr"))


def main():
    netlist = read_csv(NETLIST)
    bom_rows = [row for row in read_csv(BOM) if row["Ref"] != "PCB"]
    bom = {row["Ref"]: row for row in bom_rows}
    refs = [row["Ref"] for row in bom_rows]
    nets = {}
    for row in netlist:
        nets[(row["RefDes"], int(row["Pin"]))] = row["Net"]

    tickets = [1000]
    body = []
    symbols = {}
    devices = {}

    kinds = {ref: symbol_kind(ref) for ref in refs}
    for kind in sorted(set(kinds.values())):
        template_ref = next(ref for ref in refs if kinds[ref] == kind)
        symbols[kind] = emit_symbol(kind, template_ref, body, tickets)
    for ref in refs:
        devices[ref] = emit_device(ref, bom[ref], symbols[kinds[ref]], body, tickets)

    positions = place_components(refs)
    component_ids = {}
    component_pins = {}
    geometry_pins = []

    body.append(line("DOCHEAD", {"docType": "SCH_PAGE", "client": CLIENT, "uuid": PAGE_UUID, "updateTime": 0, "version": "candidate", "editVersion": "candidate", "user": {}}, next_ticket()))
    body.append(line("META", {"title": "Shark_Sub_G030", "schematic": SCH_UUID, "source": "", "zIndex": 1}, next_ticket(), "META"))
    body.append(line("CANVAS", {"originX": 0, "originY": 0, "yAxisDirection": "up"}, next_ticket(), "CANVAS"))

    titles = [
        (80, 1120, "POWER / PROTECTION"),
        (80, 550, "STM32G030"),
        (620, 790, "3x MX113H + MOTOR CONNECTORS"),
        (80, 300, "SERVO / CAMERA / BUOY / SWD / LEAK"),
        (1450, 1120, "PASSIVES (net-label connected)"),
    ]
    for x, y, value in titles:
        body.append(line("TEXT", {"partId": "", "groupId": 0, "locked": False, "zIndex": 20, "positionX": x, "positionY": y, "rotation": 0, "value": value, "color": "#004080", "fillColor": None, "fontFamily": None, "fontSize": 18, "strikeout": False, "underline": False, "italic": False, "fontWeight": True, "vAlign": 0, "hAlign": 0}, next_ticket(), new_id("text")))

    for ref in refs:
        kind = kinds[ref]
        sym = symbols[kind]
        x, y = positions[ref]
        cid = new_id("component")
        component_ids[ref] = cid
        body.append(line("COMPONENT", {"partId": sym["part_id"], "x": x, "y": y, "rotation": 0, "isMirror": False, "attrs": {"Footprints": "[]", "Devices": "[]", "DeviceName": None, "FootprintName": None, "pinClass": {}, "differentialPairClass": {}, "Symbols": "[]"}, "zIndex": 1, "yAxisDirection": "up"}, next_ticket(), cid))
        body.append(attr(cid, "Symbol", sym["uid"], z=2))
        body.append(attr(cid, "Device", devices[ref], z=3))
        body.append(attr(cid, "Designator", ref, x=x + 8, y=y + sym["half_h"] + 12, z=4))
        body.append(attr(cid, "Name", "={Value}", x=x, y=y + sym["half_h"] + 24, z=5))
        body.append(attr(cid, "Value", bom[ref].get("Value/Part", ""), z=6))
        body.append(attr(cid, "Footprint", bom[ref].get("Package", ""), z=7))
        component_pins[ref] = {}
        for pin, (px, py, rotation) in sym["geometry"].items():
            ax, ay = x + px, y + py
            if rotation == 0:
                lx, ly = ax - 30, ay
            else:
                lx, ly = ax + 30, ay
            component_pins[ref][pin] = (ax, ay, lx, ly)
            geometry_pins.append({"ref": ref, "pin": pin, "x": ax, "y": ay, "net": nets.get((ref, pin))})

    geometry_segments = []
    wire_count = 0
    for row in netlist:
        ref = row["RefDes"]
        pin = int(row["Pin"])
        net = row["Net"]
        ax, ay, lx, ly = component_pins[ref][pin]
        wid = new_id("wire")
        body.append(line("WIRE", {"zIndex": 10}, next_ticket(), wid))
        body.append(line("LINE", {"fillColor": None, "fillStyle": None, "strokeColor": None, "strokeStyle": None, "strokeWidth": None, "startX": ax, "startY": ay, "endX": lx, "endY": ly, "lineGroup": wid, "yAxisDirection": "up"}, next_ticket(), new_id("line")))
        body.append(line("ATTR", {"x": lx, "y": ly, "rotation": 0, "color": None, "fontFamily": None, "fontSize": 6.5, "fontWeight": None, "italic": None, "underline": None, "align": None, "value": net, "keyVisible": False, "valueVisible": True, "key": "NET", "fillColor": None, "parentId": wid, "zIndex": 11, "locked": False, "yAxisDirection": "up"}, next_ticket(), new_id("attr")))
        geometry_segments.append({"ref": ref, "pin": pin, "net": net, "x1": ax, "y1": ay, "x2": lx, "y2": ly})
        wire_count += 1

    PAGE.parent.mkdir(parents=True, exist_ok=True)
    with PAGE.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(body) + "\n")
    ecfg_records = [
        line("DOCHEAD", {"docType": "SCH", "client": CLIENT, "uuid": SCH_UUID, "updateTime": 0, "version": "candidate", "editVersion": "candidate", "user": {}}, next_ticket()),
        line("META", {"title": "Schematic1", "source": "", "board": BOARD_UUID, "zIndex": None}, next_ticket(), "META"),
    ]
    ECFG.write_text("\n".join(ecfg_records) + "\n", encoding="utf-8", newline="\n")

    project = json.loads((HERE.parent / "f407_buoy" / "Shark_V4_Buoy_F407_RevA.eprj3").read_text(encoding="utf-8"))
    project["name"] = "Shark_Sub_G030"
    project["content"] = "G030 control board candidate schematic. Generated from g030_netlist_draft.csv; GUI open and ERC not performed."
    project["created_at"] = "2026-10-20 00:00:00"
    project["updated_at"] = "2026-10-20 00:00:00"
    project["default_sheet"] = PAGE_UUID
    project["pcb_count"] = 0
    project["format"] = "folder"
    project["boards"] = []
    project["profile"]["boards"] = {BOARD_UUID: {"uuid": BOARD_UUID, "title": "Shark_Sub_G030", "zIndex": 1}}
    project["profile"]["schematics"] = {SCH_UUID: {"uuid": SCH_UUID, "name": "Schematic1", "board": BOARD_UUID, "source": "", "version": "candidate", "updateTime": 0}}
    project["profile"]["sheets"] = {PAGE_UUID: {"uuid": PAGE_UUID, "title": "Shark_Sub_G030", "schematic_uuid": SCH_UUID, "zIndex": 1, "source": "", "version": "candidate", "updateTime": 0}}
    project["profile"]["pcbs"] = {}
    project["profile"]["panels"] = {}
    project["config"]["defaultSheet"] = PAGE_UUID
    PROJECT.write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8", newline="\n")

    structural = validate(netlist, refs, wire_count)
    geometry = schematic_geometry.check(geometry_segments, geometry_pins)
    metadata = validate_metadata()
    GEOMETRY_REPORT.write_text(json.dumps(geometry, indent=2) + "\n", encoding="utf-8", newline="\n")
    MANIFEST.write_text(
        json.dumps(
            {
                "page": str(PAGE),
                "boardUuid": BOARD_UUID,
                "schematicUuid": SCH_UUID,
                "pageUuid": PAGE_UUID,
                "pins": geometry_pins,
                "segments": geometry_segments,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    report = {
        "ok": structural["ok"] and geometry["ok"] and metadata["ok"],
        "status": "CANDIDATE_BLOCKED_FOOTPRINT" if structural["ok"] and geometry["ok"] and metadata["ok"] else "FAILED",
        "categories": {
            "STRUCTURAL": "PASS" if structural["ok"] else "FAIL",
            "GEOMETRY": "PASS" if geometry["ok"] else "FAIL",
            "METADATA": "PASS" if metadata["ok"] else "FAIL",
            "FOOTPRINT": "BLOCKED",
            "ERC": "NOT_RUN",
        },
        "structural": structural,
        "geometry": geometry,
        "metadata": metadata,
        "footprint": {
            "status": "BLOCKED",
            "reason": "Project-local generic symbols and footprint strings are not verified JLCEDA library bindings.",
        },
        "erc": {"status": "NOT_RUN", "reason": "No GUI ERC/DRC has been run for this candidate."},
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    with (HERE / "schematic_pinmap.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\r\n")
        writer.writerow(["Ref", "Pin", "PinName", "Net", "Package"])
        for row in netlist:
            ref = row["RefDes"]
            pin = int(row["Pin"])
            writer.writerow([ref, pin, pin_names(ref).get(pin, ""), row["Net"], bom[ref].get("Package", "")])
    write_preview(positions, kinds, component_pins, netlist)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


def validate(netlist, refs, wire_count):
    errors = []
    records = []
    with PAGE.open(encoding="utf-8", newline="") as handle:
        for number, raw in enumerate(handle, start=1):
            if not raw.endswith("|\n") and not raw.endswith("|"):
                errors.append(f"line {number}: missing trailing |")
            parts = raw.rstrip("\n").split("||")
            if len(parts) != 2:
                errors.append(f"line {number}: expected one || separator")
                continue
            try:
                outer = json.loads(parts[0])
                inner = json.loads(parts[1].rstrip("|"))
            except json.JSONDecodeError as exc:
                errors.append(f"line {number}: JSON error {exc}")
                continue
            records.append((outer, inner))
    doc_types = {}
    current_doc = None
    doc_ids = set()
    for outer, inner in records:
        if outer["type"] == "DOCHEAD":
            doc_types[inner["docType"]] = doc_types.get(inner["docType"], 0) + 1
            current_doc = inner["uuid"]
            doc_ids = set()
            continue
        record_id = outer.get("id")
        if record_id:
            key = (current_doc, record_id)
            if key in doc_ids:
                errors.append(f"duplicate record id in document {current_doc}: {record_id}")
            doc_ids.add(key)
    components = [(outer, inner) for outer, inner in records if outer["type"] == "COMPONENT"]
    attrs = [(outer, inner) for outer, inner in records if outer["type"] == "ATTR"]
    part_ids = {outer.get("id") for outer, inner in records if outer["type"] == "PART"}
    symbol_uuids = {inner["uuid"] for outer, inner in records if outer["type"] == "DOCHEAD" and inner.get("docType") == "SYMBOL"}
    device_uuids = {inner["uuid"] for outer, inner in records if outer["type"] == "DOCHEAD" and inner.get("docType") == "DEVICE"}
    refs_seen = set()
    net_names = set()
    net_attrs = 0
    for outer, inner in attrs:
        if inner.get("key") == "NET":
            net_attrs += 1
            net_names.add(inner.get("value"))
    for outer, inner in components:
        if inner.get("partId") not in part_ids:
            errors.append(f"component {outer.get('id')} references unknown part {inner.get('partId')}")
        child_attrs = {a.get("key"): a.get("value") for ao, a in attrs if a.get("parentId") == outer.get("id")}
        if child_attrs.get("Symbol") not in symbol_uuids:
            errors.append(f"component {outer.get('id')} has invalid Symbol reference")
        if child_attrs.get("Device") not in device_uuids:
            errors.append(f"component {outer.get('id')} has invalid Device reference")
        if child_attrs.get("Designator"):
            refs_seen.add(child_attrs["Designator"])
    if refs_seen != set(refs):
        errors.append(f"designators mismatch: missing {sorted(set(refs) - refs_seen)}, extra {sorted(refs_seen - set(refs))}")
    if doc_types.get("SCH_PAGE") != 1:
        errors.append("expected exactly one SCH_PAGE")
    if wire_count != len(netlist):
        errors.append(f"wire count {wire_count} != netlist rows {len(netlist)}")
    if net_attrs != wire_count:
        errors.append(f"NET attributes {net_attrs} != wires {wire_count}")
    expected_nets = {row["Net"] for row in netlist}
    if net_names != expected_nets:
        errors.append(f"net names mismatch: missing {sorted(expected_nets - net_names)}, extra {sorted(net_names - expected_nets)}")
    if len(components) != len(refs):
        errors.append(f"component count {len(components)} != BOM refs {len(refs)}")
    return {
        "ok": not errors,
        "status": "FORMAT_OK_NOT_GUI_VERIFIED" if not errors else "FAILED",
        "page": str(PAGE),
        "project": str(PROJECT),
        "records": len(records),
        "docTypes": doc_types,
        "components": len(components),
        "wires": wire_count,
        "netAttributes": net_attrs,
        "nets": len(net_names),
        "netlistRows": len(netlist),
        "refs": len(refs),
        "errors": errors,
        "note": "Candidate .esch2 only. It has not been opened in JLCEDA Pro; no ERC/DRC and no footprint binding verification.",
    }


def read_records(path):
    records = []
    with path.open(encoding="utf-8", newline="") as handle:
        for number, raw in enumerate(handle, start=1):
            parts = raw.rstrip("\r\n").split("||")
            if len(parts) != 2:
                raise ValueError(f"{path}:{number}: expected one || separator")
            records.append((json.loads(parts[0]), json.loads(parts[1].rstrip("|\r\n"))))
    return records


def validate_metadata(project_path=PROJECT, ecfg_path=ECFG, page_path=PAGE):
    errors = []
    project = json.loads(project_path.read_text(encoding="utf-8"))
    ecfg = read_records(ecfg_path)
    page = read_records(page_path)
    ecfg_head = next((inner for outer, inner in ecfg if outer["type"] == "DOCHEAD"), {})
    ecfg_meta = next((inner for outer, inner in ecfg if outer["type"] == "META"), {})
    page_head = {}
    page_meta = {}
    for index, (outer, inner) in enumerate(page):
        if outer["type"] == "DOCHEAD" and inner.get("docType") == "SCH_PAGE":
            page_head = inner
            for later_outer, later_inner in page[index + 1:]:
                if later_outer["type"] == "DOCHEAD":
                    break
                if later_outer["type"] == "META":
                    page_meta = later_inner
                    break
            break
    if ecfg_head.get("uuid") != SCH_UUID:
        errors.append(f"ecfg schematic uuid {ecfg_head.get('uuid')} != {SCH_UUID}")
    if ecfg_meta.get("title") != "Schematic1":
        errors.append(f"ecfg title {ecfg_meta.get('title')} != Schematic1")
    if ecfg_meta.get("board") != BOARD_UUID:
        errors.append(f"ecfg board {ecfg_meta.get('board')} != {BOARD_UUID}")
    if page_head.get("uuid") != PAGE_UUID:
        errors.append(f"page uuid {page_head.get('uuid')} != {PAGE_UUID}")
    if page_meta.get("schematic") != SCH_UUID:
        errors.append(f"page schematic {page_meta.get('schematic')} != {SCH_UUID}")
    boards = project.get("profile", {}).get("boards", {})
    if BOARD_UUID not in boards:
        errors.append("project profile missing board uuid")
    schematics = project.get("profile", {}).get("schematics", {})
    if schematics.get(SCH_UUID, {}).get("board") != BOARD_UUID:
        errors.append("project schematic board mismatch")
    if schematics.get(SCH_UUID, {}).get("name") != "Schematic1":
        errors.append("project schematic name mismatch")
    sheets = project.get("profile", {}).get("sheets", {})
    if sheets.get(PAGE_UUID, {}).get("schematic_uuid") != SCH_UUID:
        errors.append("project sheet schematic mismatch")
    if project.get("default_sheet") != PAGE_UUID:
        errors.append("project default_sheet mismatch")
    if project.get("config", {}).get("defaultSheet") != PAGE_UUID:
        errors.append("project config.defaultSheet mismatch")
    return {
        "ok": not errors,
        "boardUuid": BOARD_UUID,
        "schematicUuid": SCH_UUID,
        "pageUuid": PAGE_UUID,
        "schematicName": "Schematic1",
        "ecfg": str(ecfg_path),
        "page": str(page_path),
        "project": str(project_path),
        "errors": errors,
    }


def write_preview(positions, kinds, pins, netlist):
    width, height = 4200, 3000
    scale = 0.5
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width*scale}" height="{height*scale}" viewBox="0 0 {width} {height}">']
    out.append('<rect width="4200" height="3000" fill="#ffffff"/>')
    for ref, (x, y) in positions.items():
        kind = kinds[ref]
        half_w = {"g030": 50, "mx113h": 30, "mt3608": 30, "tlv70033": 27.5, "pmos": 30, "conn6": 25, "conn5": 25, "conn3": 22.5, "conn2": 20}.get(kind, 10)
        half_h = {"g030": 90, "mx113h": 40, "mt3608": 40, "tlv70033": 35, "pmos": 40, "conn6": 40, "conn5": 35, "conn3": 27.5, "conn2": 17.5}.get(kind, 6)
        out.append(f'<rect x="{x-half_w}" y="{1200-y-half_h}" width="{2*half_w}" height="2*half_h" fill="#fff8d8" stroke="#333" stroke-width="1"/>')
        out.append(f'<text x="{x}" y="{1200-y+4}" font-size="9" text-anchor="middle" fill="#004080">{ref}</text>')
        for pin, (ax, ay, lx, ly) in pins[ref].items():
            out.append(f'<line x1="{ax}" y1="{1200-ay}" x2="{lx}" y2="{1200-ly}" stroke="#666" stroke-width="0.7"/>')
    out.append("</svg>")
    PREVIEW.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
