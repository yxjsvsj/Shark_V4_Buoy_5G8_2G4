# Shark_Sub_G030 schematic candidate

Status: **CANDIDATE .esch2 / FORMAT-VALIDATED / NOT GUI-OPENED / NOT ERC-CHECKED.**

This folder contains a generated G030 draft schematic for review. It is not a finished JLCEDA Pro schematic and must not be treated as a PCB-release artifact.

## Files

- `Shark_Sub_G030.eprj3` - folder-project index for the candidate.
- `sch/Schematic1/Shark_Sub_G030.esch2` - line-delimited JLCEDA Pro schematic candidate.
- `sch/Schematic1/Schematic1.ecfg` - copied schematic configuration template.
- `build_schematic_candidate.py` - generator and static validator.
- `schematic_candidate_report.json` - structural validation result.
- `schematic_pinmap.csv` - 137-row Ref/Pin/PinName/Net/Package mapping.
- `schematic_candidate.svg` - simple block/pin preview, not an EDA render.

## What is included

- J1 battery input, Q1 P-MOS, SW1 reed switch, R5/C14 gate network.
- MT3608 boost, L1, D1, feedback divider, C7/C8.
- TLV70033 LDO, C9/C15, G030 decoupling.
- STM32G030K8T6 with all 32 package pins.
- Three MX113H H-bridges U2-U4 and J2-J4.
- J5 servo, J6 camera CVBS, J7 six-wire buoy, J8 SWD, J9 leak.
- R7/LED1 status LED.
- Net-name labels generated from `g030_netlist_draft.csv`.

## Limitations

- Symbols are **project-local generic symbols** with the correct pin numbers and pin names. They are not manufacturer library symbols.
- Device records contain the intended footprint/package name, but there are no embedded footprint or 3D documents. Footprint binding is not verified.
- The page has no A4 drawing-sheet symbol/border.
- The file has not been opened in JLCEDA Pro. There is no GUI ERC/DRC, no PCB import, and no visual overlap check.
- The generator only proves that the file is structurally valid line-delimited JSON with the expected document and reference structure.
- The page is intentionally a net-label draft, not a fully routed presentation schematic.

## Regenerate and validate

```powershell
python hardware/g030_control/build_schematic_candidate.py
```

Expected structural result:

- 15 SYMBOL documents.
- 45 DEVICE documents.
- 1 SCH_PAGE.
- 45 components.
- 137 wires / 137 NET attributes.
- 32 nets.
- 32 netlist rows and 45 BOM refs represented.

## Required GUI pass

Open `Shark_Sub_G030.eprj3` in JLCEDA Pro and then:

1. Confirm every symbol opens and all pins are present.
2. Bind/verify the footprint for every device.
3. Run ERC and record every violation.
4. Fix/confirm the J7, Q1 and polymer-cap footprints.
5. Export a PDF/PNG and confirm the blocks are readable.
6. Only after that consider the schematic “drafted”; it is still not production-ready.

Do not generate production Gerber or order a PCB from this candidate.
