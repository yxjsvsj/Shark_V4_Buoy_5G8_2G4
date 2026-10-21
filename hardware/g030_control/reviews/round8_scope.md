# Round 8 design baseline: 0.5 m maximum depth

Date: 2026-10-21. Baseline: `96515ef`.

Status: **ACTIVE DESIGN BASELINE. Round 7 documents are retained as historical records and are not deleted.**

## Scope change

- Maximum normal working depth: **0.5 m freshwater**.
- Design cable: **0.8-1.2 m**, nominal 1.0 m.
- The old 5 m and 7.5 m design targets in `round7_*` are **historical only**. They are superseded by this document.
- This is still a design target, not a pressure-tested capability.

## Pressure at 0.5 m

- Gauge pressure: `rho*g*h = 1000 * 9.81 * 0.5 = 4.905 kPa = 49.05 mbar`.
- Absolute pressure at 1013 mbar surface: about **1062 mbar**.
- The MS5837-02BA operating range is 300-1200 mbar, so 0.5 m is **inside** the specified range.
- Relative accuracy is about +/-2 mbar in 300-1100 mbar, which is about +/-2 cm of freshwater; the +/-0.2 m control target has an order-of-magnitude margin.
- The sensor resolution is far better than the control target; the limiting factors are calibration, mounting, surface reference, and control-loop quality.

## Selected depth interface

- Sensor: **TE MS5837-02BA01-50**, 3.3 x 3.3 x 2.75 mm, 1.5-3.6 V, I2C address 0x76.
- Bus: **STM32G030 I2C1 on PB6/PB7**.
  - PB6 = I2C1_SCL (pin 30)
  - PB7 = I2C1_SDA (pin 31)
- PA4/PA5 are **not** I2C on STM32G030 and must not be used for this sensor.
- Connector J10: 1 +3V3, 2 GND, 3 SCL/PB6, 4 SDA/PB7.
- Add 4.7k pull-ups to +3V3, 100 nF + 470 nF local decoupling, and short/protected wiring.
- The bare sensor requires the specified O-ring pressure port; the Bar02 breakout is not a 0.5 m watertight assembly by itself.

This is a **selected design**, but it is **not yet in the real RevB schematic** because the GUI/library binding is blocked.

## Selected power and driver direction

| Function | Current RevB | Selected direction | Status |
|---|---|---|---|
| 5V boost | MT3608 | TPS61022RWUR, LCSC C915088 | SELECTED, NOT IN SCHEMATIC |
| Motor drivers | 3x MX113H | 3x DRV8837DSGR, LCSC C39159 | SELECTED, NOT IN SCHEMATIC |
| Motor connectors | JST-SH 1A | JST-XH 2P or solder pads | SELECTED, NOT IN SCHEMATIC |
| Debug | HDR1X5 2.54 mm | Tag-Connect TC2030 6-pad 1.27 mm | SELECTED, NOT IN SCHEMATIC |
| Magnet switch | hold-to-run | hold-to-run vs self-latch | DECISION_REQUIRED |

Do not claim these replacements are implemented until the actual `.esch2`, BOM and footprint mapping are changed and checked.

## Cable at 0.8-1.2 m

Using 24AWG copper at 0.0842 ohm/m and a two-conductor loop:

| Length | Loop resistance | Drop at 0.72 A | Drop at 1 A | Drop at 1.5 A |
|---:|---:|---:|---:|---:|
| 0.8 m | 0.135 ohm | 0.097 V | 0.135 V | 0.202 V |
| 1.0 m | 0.168 ohm | 0.121 V | 0.168 V | 0.252 V |
| 1.2 m | 0.202 ohm | 0.145 V | 0.202 V | 0.303 V |

The 24AWG/JST-PH 2A-class cable is acceptable for the 0.5 m prototype **if** the measured load stays at or below 1 A and the buoy input has margin. It is not approved for 2 A continuous.

## Cable weight and drag estimate

- 5.5 mm OD, 1.0 m: displaced water volume ~23.8 cm3 -> ~23.8 g buoyancy.
- Estimated cable mass: 32-48 g for 1.0 m, 38-58 g for 1.2 m (measure the real cable).
- Net in-water estimate: roughly 10-30 g negative; add 10-30 g foam or choose a neutral cable.
- Drag estimate at 0.5 m/s: roughly 1 N for 1.2 m of 5.5 mm cable; at 1 m/s roughly 4 N. This is a screening estimate, not a tow test.
- The cable must have a strain member and service loop; J7 must not carry tow load.
- The buoy needs enough reserve to float the cable, antenna and connector.

## Current status

- No 0.5 m pressure test, no cable pull test, no buoyancy test.
- Actual EDA schematic still uses MT3608, MX113H and HDR1X5.
- GUI Protel export and full DRC log remain BLOCKED.
- The first powered test still requires a current-limited supply and no battery-only operation.
