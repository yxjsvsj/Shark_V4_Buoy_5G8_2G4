# Shark_Sub_G030 JLCEDA Pro project

Status: **REAL JLCEDA PROJECT / SCHEMATIC DRAFTED / DRC HAS 1 WARNING / PCB EMPTY / NOT PRODUCTION READY.**

Open this folder project:

`hardware/g030_control/Shark_Sub_G030_RevA/Shark_Sub_G030_RevA.eprj3`

Project tree after opening:

- Board: `Shark_Sub_G030`
- Schematic: `G030_Control`
- Page: `01_G030_CONTROL`
- PCB: `PCB1` (empty by design)

## What is real now

- 45 components placed from the JLCEDA system library with real symbols, footprints, LCSC part numbers and 3D model links.
- 137 net-name stub wires, one per `g030_netlist_draft.csv` row.
- 32 nets.
- Netlist export `Shark_Sub_G030_RevA/g030_export.net` was compared against the CSV: **137/137 pins and 32/32 nets match; no missing or extra connections**.
- The page is A0 and contains **actual JLCEDA library symbols**, not the earlier generic candidate symbols.
- The project opens in JLCEDA Pro 4.1.78; GUI DRC was run.

## DRC result

`drc_result.json` records one `CHECKFLOATPIN` warning. It covers intentionally unused pins:

- U1: unused GPIO/oscillator/PA12 pins
- U5: NC pin 6
- U6: NC pin 4
- J2/J3/J4/J9: shield/extra mechanical pins 3/4
- J5/J6: shield pin 0

This is a warning, not a clean ERC pass. The schematic must be reviewed before calling it complete.

## Limitations

- The PCB is intentionally empty; no footprints were placed on a board and no layout exists.
- The schematic uses short net-name stubs, not fully routed wires. The netlist is correct; the drawing is not a presentation-quality routed schematic.
- Some connector symbols are the closest real library parts, not necessarily the final mechanical part:
  - J5/J6 = SH1.0-3P
  - J2-J4/J9 = SH1.0-2P
  - J8 = HDR1X5, not a 1.27mm pogo pad array
- Symbol/footprint pin mappings must still be checked against the exact purchased parts.
- No Gerber, no PCB order, no production release.

## Files

- `Shark_Sub_G030_RevA/Shark_Sub_G030_RevA.eprj3` - JLCEDA project.
- `Shark_Sub_G030_RevA/sch/G030_Control/01_G030_CONTROL.esch2` - schematic source.
- `Shark_Sub_G030_RevA/g030_schema.png` - exported schematic image.
- `Shark_Sub_G030_RevA/g030_export.net` - exported Protel netlist.
- `netlist_compare.json` - exact CSV-vs-export comparison.
- `drc_result.json` - GUI DRC warning list.
- `schematic_pinmap.csv` - Ref/Pin/PinName/Net/Package mapping.

## What to do next in JLCEDA

1. Open `Shark_Sub_G030_RevA.eprj3`.
2. Double-click `Shark_Sub_G030` -> `G030_Control` -> `01_G030_CONTROL`; the page now has content.
3. Review symbol/footprint pin mappings, especially connectors.
4. Mark unused pins NC or accept/annotate the single DRC warning.
5. Do not click `PCB1` expecting content; it is intentionally empty.
6. Only after schematic review should a PCB be imported/laid out.
