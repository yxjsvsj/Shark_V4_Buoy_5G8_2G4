# RevB Q1 / D1 physical-pin correction

Status: **SOURCE CORRECTED / GUI VISUAL PASS / GUI EXPORT AND DRC BLOCKED / DO NOT POWER OR FABRICATE.**

This file records the fifth-round fix in the real RevB project, not only in the generator fixture.

## Evidence

- Baseline: `abe8bc3e3f010765ddc304744eabf1a2dc9dec09`.
- Before export: `Shark_Sub_G030_RevB/g030_export.net` at `abe8bc3`.
- Before screenshot: `Shark_Sub_G030_RevB/01_POWER_before_q1_d1.png` (copied from the existing `01_POWER.png`).
- After screenshots: `01_POWER_after_q1_2026-10-21.png` and `01_POWER_after_d1_2026-10-21.png`; JLCEDA Pro V4.1.78 reopened and visually checked on 2026-10-21.
- Corrected page: `Shark_Sub_G030_RevB/sch/G030_Control/01_POWER.esch2`.
- Export status: `Shark_Sub_G030_RevB/netlist_export_status.json`.

## Q1: Vishay SiSS23DN-T1-GE3

The Vishay PowerPAK 1212-8S pinout is:

| Pin | Function |
|---|---|
| 1, 2, 3 | Source |
| 4 | Gate |
| 5, 6, 7, 8 | Drain |

The RevB page had `Q1.1` on `PWR_GATE` and `Q1.4` on `VBAT`. Because pins 1-3 are internally the same Source, closing SW1 could short VBAT to GND. The page was corrected by swapping the net labels on the Q1.1 and Q1.4 wires:

| Pin | Before | After |
|---|---|---|
| Q1.1 Source | PWR_GATE | VBAT |
| Q1.2 Source | VBAT | VBAT |
| Q1.3 Source | VBAT | VBAT |
| Q1.4 Gate | VBAT | PWR_GATE |
| Q1.5-Q1.8 Drain | VMOTOR | VMOTOR |

R5 remains VBAT-to-PWR_GATE, SW1 remains PWR_GATE-to-GND, and C14 remains across PWR_GATE and VBAT (gate-source).

## D1: SS34

The selected JLCEDA SS34 symbol defines pin 1 as K and pin 2 as A. The RevB page had K on SW and A on +5V, which is the wrong direction for a boost converter.

| Pin | Before | After |
|---|---|---|
| D1.1 K | SW | +5V |
| D1.2 A | +5V | SW |

The SMA footprint cathode marking still requires a PCB footprint check; no PCB is placed.

## Verification

`verify_g030_netlist.py` parses the Protel netlist, checks physical pin number, exported pin function and net, and compares all 137 pins with the corrected CSV. It reports 60 critical pins checked, 137 parsed pins, 32 nets, and zero CSV mismatches on the corrected provisional export.

The fixture `tests/fixtures/g030_export_abe8bc3_wrong.net` fails with exactly:

- Q1.1 Source expected VBAT, found PWR_GATE.
- Q1.4 Gate expected PWR_GATE, found VBAT.
- D1.1 K expected +5V, found SW.
- D1.2 A expected SW, found +5V.

## Unblock conditions

1. Re-open the actual RevB project and confirm the edited `01_POWER` page visually; this has been done, but repeat after any further edit.
2. Re-run ERC/DRC and export the GUI netlist.
3. Run `verify_g030_netlist.py` against that GUI export and require `ok: true`, zero CSV mismatches, and no Q1/D1 errors.
4. Verify the SS34 footprint cathode marking on the PCB.
5. First power-up only with a current-limited supply, no motors, servo, camera or buoy; check for battery short and measure 5V/3.3V rails.
