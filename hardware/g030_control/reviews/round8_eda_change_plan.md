# Round 8 EDA change plan

Date: 2026-10-21. Baseline: `96515ef`.

Status: **SELECTION DEFINED / ACTUAL EDA CHANGE BLOCKED.**

This is the planned RevB change list after the 0.5 m scope change and device selection. It is not a claim that the files have been changed. The current RevB still contains MT3608, MX113H and the 2.54 mm J8.

## 1. Depth sensor J10 / MS5837-02BA

Add a 4-pin connector or sealed sensor pads:

| J10 pin | Net | MCU pin |
|---|---|---|
| 1 | +3V3 | - |
| 2 | GND | - |
| 3 | I2C1_SCL | U1.30 / PB6 |
| 4 | I2C1_SDA | U1.31 / PB7 |

- 4.7k pull-ups from SCL/SDA to +3V3.
- 100 nF + 470 nF at the sensor.
- Series 22-100 ohm optional at the MCU side.
- Address 0x76.
- At 0.5 m the absolute pressure is ~1062 mbar, inside the MS5837-02BA 300-1200 mbar range.
- The bare sensor needs the specified O-ring pressure port; a breakout board is not watertight.

Blocked by: no verified JLCEDA library symbol/footprint for the selected sensor/connector; no reliable GUI edit session.

## 2. U5: MT3608 -> TPS61022RWUR

Selected part: **TPS61022RWUR**, LCSC **C915088**, VQFN-7 2x2.

Pin mapping:

| TPS61022 pin | Net |
|---|---|
| 1 GND | GND |
| 2 SW | L1 / SW node |
| 3 VOUT | +5V |
| 4 FB | R1/R2 midpoint |
| 5 EN | VMOTOR |
| 6 MODE | GND for PFM, or +3V3 for forced PWM |
| 7 VIN | VMOTOR |
| EP | GND |

Changes:

- Remove D1 SS34 (synchronous rectifier) and the MT3608.
- L1: 1.0 uH, >=8 A saturation, low DCR.
- Input: 10 uF effective; output: >=30 uF effective for <=1.5 A.
- Feedback: verify 5.0 V with the selected divider; TPS61022 Vref is 0.6 V.
- Thermal pad, vias and copper area.
- Do not claim 1.5 A at 3.0 V until WEBENCH/bench data.

## 3. U2-U4: MX113H -> DRV8837DSGR

Selected part: **DRV8837DSGR**, LCSC **C39159**, WSON-8 2x2 with thermal pad.

Pin mapping:

| DRV8837 pin | Net |
|---|---|
| 1 VM | VMOTOR |
| 2 OUT1 | motor output 1 |
| 3 OUT2 | motor output 2 |
| 4 GND | GND |
| 5 IN2 | firmware PWM/GPIO |
| 6 IN1 | firmware PWM/GPIO |
| 7 nSLEEP | +3V3 (or a controlled enable) |
| 8 VCC | +3V3 |
| EP | GND |

- 0.1 uF at VM and VCC.
- Keep C1-C3 100 uF and C4-C6 100 nF.
- Replace J2-J4 with JST-XH 2P or solder pads.
- 1.8 A peak, 280 mohm HS+LS, 60.9 C/W; still verify sealed-hull temperature.

## 4. J8: HDR1X5 -> Tag-Connect TC2030

- 6-pad, 1.27 mm pitch, no 2.54 mm header.
- Pads: +3V3, GND, SWDIO, SWCLK, NRST, GND/spare.
- Mating cable: TC2030-IDC or TC2030-IDC-NL.
- Verify the exact pad order against the Tag-Connect drawing before layout.

## 5. J7 / cable

- Keep JST-PH 6P only if the measured 5V load is <=1 A and the 2 A peak is accepted.
- Cable: 1 m nominal, 0.8-1.2 m, 24AWG power, 28AWG signals, 75 ohm coax.
- Add series/TVS on PP and telemetry.
- Add a strain member and gland; J7 must not carry tow load.
- Estimated 24AWG drop at 1 m: 0.12/0.17/0.34 V at 0.72/1/2 A.

## 6. Power switch

No change until the hold-to-run vs self-latch decision. The current Q1/R5/SW1 circuit is hold-to-run. If self-latch is chosen, the new state machine and off-state leakage must be designed and tested.

## 7. EDA execution requirement

The actual `.esch2` change is **not done**. A real edit requires:

1. JLCEDA Pro library symbol/footprint verification for TPS61022 C915088, DRV8837 C39159, MS5837-02BA and the selected connector.
2. A GUI edit with before/after screenshots.
3. A fresh GUI Protel export.
4. A full ERC/DRC log.
5. Re-run `verify_g030_netlist.py` and all static tests.

Do not hand-edit `.esch2` and call it GUI-verified.
