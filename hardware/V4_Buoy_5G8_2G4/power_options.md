# 1S to 5V power options

Status: **DESIGN COMPARISON / MT3608 REMAINS UNQUALIFIED / NO LOAD TEST.**

No option is approved for production. Servo stall, real VTX current, motor start/stall and simultaneous 5V load remain TBD. Do not fabricate a PCB from this document.

## Baseline load

| Load | Nominal | Status |
|---|---:|---|
| Camera | 0.10 A | TBD measurement |
| Buoy VTX/receiver | 0.40 A | TBD real module current |
| Jaw servo | 0.20 A | Stall current TBD |
| TLV70033/G030 | 0.02 A | Design estimate |
| **Total** | **~0.72 A** | **Not a worst case** |

The MT3608 corrected chip-loss estimates are 63-86 C at 0.4 A, 83-129 C at 0.72 A and 106-180 C at 1 A (40 C ambient, 250 C/W). The 0.72 A case is marginal and the 1 A maximum case exceeds the junction limit.

## Option A: keep MT3608, split the 5V load

Use two independent 5 V rails:

- U5A MT3608: camera 0.10 A + jaw servo 0.20 A = **0.30 A nominal**.
- U5B MT3608: buoy VTX/receiver **0.40 A nominal**.
- Each rail has its own 22 uH inductor, SS34, 22 uF x2 output capacitors and local input capacitor.
- Do not common the two 5 V outputs at the board; join only at the load if the buoy and camera share a connector, or keep separate pins.

| Item | Estimate |
|---|---|
| Converter count | 2 |
| IC package | 2 x SOT-23-6 |
| Inductors | 2 x SRP6060FA-220M (6.6 x 6.4 mm) |
| Approximate power area | ~150 mm2 including passives and keep-out |
| Efficiency | ~84-86% per rail at 3.0 V |
| Chip loss at 0.3 A | ~0.07 W typical / ~0.14 W max |
| Chip loss at 0.4 A | ~0.09 W typical / ~0.18 W max |
| Thermal | Each rail below the 0.72 A case; still dependent on copper and sealed ambient |

Advantages: no new IC qualification, each converter is below its worst thermal point, and a single rail failure does not remove both loads.

Disadvantages: two inductors and two sets of passives; more board area; two 5 V nets; higher total quiescent loss; the servo stall remains unknown and can still overload U5A.

## Option B: replace U5 with TPS61022

TI **TPS61022** is a 1S-capable synchronous boost:

- Input 0.5-5.5 V; start-up from 1.8 V.
- Output 2.2-5.5 V, 8 A valley current limit.
- 2 x 2 mm VQFN-7, 1 MHz.
- 94.7% efficiency at 3.6 V to 5 V, 3 A (datasheet typical).
- True output disconnection in shutdown, output short-circuit and thermal shutdown.
- Reference output capability: 5 V/3 A at 3.6 V; at 3.0 V the guaranteed continuous current must be checked in WEBENCH and on the bench.

Proposed design target: **5 V/1.5 A continuous at 3.0 V**, with peak headroom for servo start. This covers the 0.72 A nominal load with margin, but does not approve an unknown servo stall.

| Item | Estimate |
|---|---|
| IC | TPS61022RWU, 2 x 2 mm VQFN-7 |
| Inductor | 1.0 uH, >= 8 A saturation, low DCR (for example 3 x 3 mm class) |
| Input/output capacitors | 10 uF input, 30 uF effective output minimum for <=1.5 A |
| Approximate power area | ~60-80 mm2 |
| Efficiency | ~90-94% at 3.6 V; verify at 3.0 V |
| Loss at 0.72 A | ~0.30-0.45 W converter, IC share lower than MT3608 |
| Thermal | RthetaJA 50.9 C/W on TI EVM; layout with thermal vias and copper |

Advantages: one converter, much smaller, higher current capability, synchronous rectification, true disconnect.

Disadvantages: new IC/footprint and compensation/layout review; 1 uH inductor and output capacitor selection are critical; still needs 3.0 V/1.5 A thermal and efficiency test; no measured servo stall.

## Recommendation

**Selected direction: Option B, TPS61022RWUR (LCSC C915088)**, with a **1.5 A continuous design target at 3.0 V**, because it removes the MT3608 thermal ceiling and reduces board area. It is not yet in the RevB schematic. Keep **Option A** as the fallback if the TPS61022 footprint or 3.0 V/1.5 A capability is not demonstrated.

Do not change the RevB schematic to TPS61022 until its JLCEDA symbol/footprint are verified. The current BOM remains MT3608 candidate and is marked BLOCKED.

## Required tests

1. Measure servo stall and three-motor startup current.
2. Measure the actual buoy VTX/receiver current.
3. Measure 5 V efficiency and IC case temperature at 3.0 V, 0.4/0.72/1.0/1.5 A.
4. Measure output ripple and transient with camera/servo switching.
5. Verify the selected inductor saturation and temperature.
6. Re-run the thermal calculation with the real enclosure ambient.
