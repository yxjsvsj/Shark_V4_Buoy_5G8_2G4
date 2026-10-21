# Round 7 thruster and MX113H review

Date: 2026-10-21. Baseline: `62098cf`.

Status: **DATASHEET REVIEW / THERMAL DERATING REQUIRED / MEASUREMENT REQUIRED.**

## 1. MX113H verified data

Source: Mixic MX113H datasheet, SOT-23-6.

| Parameter | Value |
|---|---|
| Supply | 2-8 V recommended; 8.5 V absolute max |
| Continuous output | 1 A at TA=25 C |
| Peak output | 1.5 A |
| RDS(on) | 0.4 ohm at 800 mA, VCC=6.5 V, 25 C |
| ThetaJA | 220 C/W |
| Power dissipation | 0.6 W max at 25 C |
| Thermal shutdown | 150 C typical, 20 C hysteresis |
| Logic | IN1=IN2=L standby/high-Z; H/L forward; L/H reverse; H/H brake |
| Inputs | internal ~15k pull-down |

Pinout is verified: **1 OUT2, 2 GND, 3 OUT1, 4 VCC, 5 IN1, 6 IN2**. The RevB U2-U4 mapping matches this.

## 2. Thermal reality

`P = I^2 * RDS(on)` for one conducting pair, using 0.4 ohm as the datasheet point:

| Current | Power | Rise at 220 C/W | TJ at 40 C ambient |
|---:|---:|---:|---:|
| 0.5 A | 0.10 W | 22 C | 62 C |
| 0.7 A | 0.20 W | 43 C | 83 C |
| 0.8 A | 0.26 W | 56 C | 96 C |
| 1.0 A | 0.40 W | 88 C | 128 C |
| 1.5 A | 0.90 W | 198 C | 238 C |

The 1 A continuous rating is a **25 C, 14.9 x 13.8 mm test-board** number. In a sealed 5 m hull at 40-50 C ambient, 1 A has little or no margin. The 1.5 A peak is transient-only and must never be sustained. Three motors at 1 A each are not thermally approved.

## 3. Electrical behavior

- Forward: IN1=PWM, IN2=0. Reverse: IN1=0, IN2=PWM. Coast: 0/0. Brake: 1/1.
- At 3.0 V battery, the H-bridge has less gate drive and a higher effective RDS(on); thrust at low battery will be lower than at 4.2 V. Measure at both ends.
- The MX113H has internal flyback diodes; C1-C3 (100 uF) and C4-C6 (100 nF) are still required at each VCC.
- No current sense or stall detection is present. A stalled motor can thermally shut down the driver, but a hard stall or output short can exceed the 1.5 A peak rating.
- Vertical thruster is electrically bidirectional. Whether it gives symmetric thrust depends on the propeller and duct, not just the H-bridge.

## 4. Connector and wiring

- J2-J4 are JST-SH 1 A class. MX113H peak is 1.5 A and starting current can be higher. JST-SH has no margin.
- Replace J2-J4 with JST-XH (3 A class), solder pads, or a 2 A+ locking connector after measuring the actual motor.
- Use short, twisted motor leads and a local 100 uF + 100 nF at each driver. Keep PWM loops away from the CVBS/PP wiring.
- Add a board fuse/PTC or electronic current limit for the motor bus; the pack PCM is not a substitute for board-level fault containment.

## 5. Measurement plan

1. Identify the exact thruster: winding resistance, Kv, propeller, duct, rated voltage/current.
2. Measure running current at 3.0, 3.7 and 4.2 V in water (or a dynamometer/load).
3. Measure startup inrush and locked-rotor current with a current probe; record duration.
4. Measure MX113H case temperature at 0.5, 0.7 and 1.0 A continuous in the intended enclosure.
5. Measure thrust in both directions for the vertical unit; verify symmetric authority.
6. If running current >0.7 A continuous or stall >1.2 A, change the driver or limit motor command in firmware.

## 6. Recommended design limit (until measured)

- Continuous motor current: **<=0.7 A per channel** with the current SOT-23-6 and sealed enclosure.
- Peak: **<=1.2 A** and only for a short, bounded start interval.
- If the chosen thruster needs more, use a lower-RDS(on) driver with a real thermal pad and current limit; do not simply raise the firmware limit.
- J2-J4: replace with a 2 A+ connector for the prototype.

These are design limits, not measurements. The actual thruster is still TBD.
