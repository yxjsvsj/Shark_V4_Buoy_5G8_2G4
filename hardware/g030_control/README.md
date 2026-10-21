# Shark_Sub_G030 JLCEDA Pro project (RevB, four pages)

Status: **REAL JLCEDA PROJECT / FOUR-PAGE SCHEMATIC DRAFT / Q1-D1 SOURCE CORRECTED / EXPORT + DRC BLOCKED / PCB EMPTY / NOT PRODUCTION READY.**

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

## Legacy generated candidate (audit fixture)

`build_schematic_candidate.py` generates `Shark_Sub_G030.eprj3` + `sch/Schematic1/Shark_Sub_G030.esch2` for the P0 geometry/metadata audit. It is **not** the primary project:

- 45 project-local generic symbols, 137 net stubs, 32 nets.
- Geometry check: 0 conflicts; report `geometry_report.json`.
- Metadata check: board/schematic/page UUIDs and `Schematic1.ecfg` pass.
- Footprint binding: **BLOCKED**; generic symbols are not real library bindings.
- GUI: not opened; no ERC.

Run:

```powershell
python hardware/g030_control/build_schematic_candidate.py
python hardware/g030_control/check_schematic_geometry.py
python hardware/g030_control/verify_g030_netlist.py
python hardware/V4_Buoy_5G8_2G4/tests/run_negative_tests.py
```

The four-page RevB project below is the real-library schematic; the legacy candidate is only for the requested generator/geometry/metadata checks.

## What is real

- 45 components placed from the JLCEDA system library with real symbols, footprints, LCSC part numbers and 3D model links.
- 137 net-name stub wires, one per `g030_netlist_draft.csv` row.
- 32 nets across the four pages.
- The provisional corrected netlist matches the CSV exactly: **137/137 pins, 32/32 nets**.
- Q1/D1 physical-pin semantics: `semantic_report.json` passes 60 critical pins and reports zero CSV mismatches.
- All four pages are A3 and have title blocks.

## Q1 and D1 correction

The real RevB `01_POWER` page had Q1.1 on PWR_GATE and Q1.4 on VBAT, and D1.1 K on SW with D1.2 A on +5V. The page source was corrected to:

- Q1.1/Q1.2/Q1.3 Source -> VBAT.
- Q1.4 Gate -> PWR_GATE.
- Q1.5-Q1.8 Drain -> VMOTOR.
- D1.1 K -> +5V.
- D1.2 A -> SW.

See `revb_q1_d1_fix.md`. JLCEDA Pro V4.1.78 was reopened and the page was visually checked: after screenshots are in `Shark_Sub_G030_RevB/01_POWER_after_q1_2026-10-21.png` and `01_POWER_after_d1_2026-10-21.png`. The GUI Protel export and full DRC log are still **BLOCKED**; do not claim the physical board is repaired.

## Round 7 reviews

- `reviews/round7_schematic_audit.md` - four-page audit and gap list.
- `reviews/limemini_limerc_reference_audit.md` - actual LimeRC schematic/source evidence.
- `reviews/round7_pin_net_matrix.csv` - 137-pin matrix.
- `reviews/round7_power_review.md` - magnetic switch and 5V options.
- `reviews/round7_thruster_review.md` - MX113H thermal/connector limits.
- `reviews/round8_scope.md` - **active 0.5 m baseline**, selected MS5837-02BA / TPS61022 / DRV8837, 1 m cable.
- `reviews/round7_depth_control.md` - historical 5 m proposal; retained, superseded.
- `reviews/round7_buoy_interface.md` - historical 5 m cable review; retained, superseded.
- `reviews/round7_eda_verification.json` - actual GUI/export/DRC status.
- `reviews/round7_blockers.md` and `reviews/round7_next_actions.md`.

The 0.5 m depth interface, J8 TC2030, TPS61022 and DRV8837 selections are **not** implemented in the actual RevB schematic yet. The old 5 m reviews are historical only.

## DRC

`drc_result.json` records only an aggregate **138 warnings**:

- 137 `NETOBJECTONGRID`.
- 1 `CHECKFLOATPIN` class.

The previous per-page 138 values were aggregate copies, not page-attributed counts. The full object/net/coordinate/rule/page log is **BLOCKED**. NC flags are **UNMARKED**.

This is **not ERC/DRC-clean**. The schematic is a draft, not a release schematic.

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
- `Shark_Sub_G030_RevB/g030_export.net` - provisional corrected Protel netlist; see `netlist_export_status.json` (not GUI regenerated).
- `Shark_Sub_G030_RevB/01_POWER_before_q1_d1.png` - before screenshot.
- `Shark_Sub_G030_RevB/01_POWER_after_q1_2026-10-21.png` - GUI after screenshot, Q1.
- `Shark_Sub_G030_RevB/01_POWER_after_d1_2026-10-21.png` - GUI after screenshot, D1.
- `Shark_Sub_G030_RevB/gui_verification.json` - GUI date/version/checks and export-blocked status.
- `revb_q1_d1_fix.md` - Q1/D1 evidence and unblock conditions.
- `package_polarity_review.md` - footprint, D1/C1-C3 polarity and J8 proposal.
- `../V4_Buoy_5G8_2G4/power_options.md` - split-MT3608 vs TPS61022.
- `semantic_report.json` - physical pin function/net and CSV comparison.
- `verify_g030_netlist.py` - semantic checker.
- `netlist_compare.json` - exact CSV-vs-export comparison.
- `drc_result.json` - aggregate DRC warning summary.
- `schematic_pinmap.csv` - Ref/Pin/PinName/Net/Package mapping.

## Open in JLCEDA

1. Close any old `Shark_Sub_G030`/`Board1` project window.
2. File -> Open -> Local project.
3. Select `Shark_Sub_G030_RevB.eprj3`.
4. Expand `Shark_Sub_G030` -> `G030_Control`.
5. Open `01_POWER`, `02_G030`, `03_MOTOR`, `04_IO` separately.

`PCB1` is expected to be empty. Do not look for the schematic inside the PCB page.
