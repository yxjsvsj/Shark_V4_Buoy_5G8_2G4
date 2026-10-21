# Shark_Sub_G030 JLCEDA Pro project (RevB, four pages)

Status: **REAL JLCEDA PROJECT / FOUR-PAGE SCHEMATIC DRAFT / DRC HAS 138 WARNINGS / PCB EMPTY / NOT PRODUCTION READY.**

Open:

`hardware/g030_control/Shark_Sub_G030_RevB/Shark_Sub_G030_RevB.eprj3`

Project tree:

- Board: `Shark_Sub_G030`
- Schematic: `G030_Control`
- Pages:
  - `01_POWER`
  - `02_G030`
  - `03_MOTOR`
  - `04_IO`
- PCB: `PCB1` (empty by design)

## What is real

- 45 components placed from the JLCEDA system library with real symbols, footprints, LCSC part numbers and 3D model links.
- 137 net-name stub wires, one per `g030_netlist_draft.csv` row.
- 32 nets across the four pages.
- Exported netlist matches the CSV exactly: **137/137 pins, 32/32 nets, no missing or extra connections**.
- All four pages are A3 and have title blocks.

## DRC

`drc_result.json` records **138 warnings**:

- 137 `NETOBJECTONGRID` warnings from the net-name stubs.
- 1 `CHECKFLOATPIN` warning for intentionally unused U1/U5/U6 pins and connector shield/extra pins.

This is **not ERC-clean**. The schematic is a netlist-valid draft, not a release schematic.

## Limitations

- The PCB is empty; no footprint placement or layout.
- The schematic uses short net-name stubs, not fully routed presentation wiring.
- J5/J6 use `SH1.0-3P`; J2-J4/J9 use `SH1.0-2P`; J8 uses `HDR1X5`, not a 1.27mm pogo array. Verify against purchased parts.
- The MT3608 5V rail is still BLOCKED by thermal analysis; see `../V4_Buoy_5G8_2G4/power_budget.md`.
- No Gerber, no PCB order, no production release.

## Files

- `Shark_Sub_G030_RevB/Shark_Sub_G030_RevB.eprj3` - JLCEDA project.
- `Shark_Sub_G030_RevB/sch/G030_Control/01_POWER.esch2` ... `04_IO.esch2` - four page sources.
- `Shark_Sub_G030_RevB/01_POWER.png` ... `04_IO.png` - exported page images.
- `Shark_Sub_G030_RevB/g030_export.net` - exported Protel netlist.
- `netlist_compare.json` - exact CSV-vs-export comparison.
- `drc_result.json` - DRC warning summary.
- `schematic_pinmap.csv` - Ref/Pin/PinName/Net/Package mapping.

## Open in JLCEDA

1. Close any old `Shark_Sub_G030`/`Board1` project window.
2. File -> Open -> Local project.
3. Select `Shark_Sub_G030_RevB.eprj3`.
4. Expand `Shark_Sub_G030` -> `G030_Control`.
5. Open `01_POWER`, `02_G030`, `03_MOTOR`, `04_IO` separately.

`PCB1` is expected to be empty. Do not look for the schematic inside the PCB page.
