# RevB footprint, polarity and debug-connector review

Status: **SYMBOL/FOOTPRINT LIBRARY REVIEW / PCB NOT PLACED / PHYSICAL CHECK NOT DONE.**

The schematic uses JLCEDA system-library devices. The PCB is empty, so pad numbering, courtyard, solder mask, polarity marking and assembly orientation still require a board-level check.

## Critical devices

| Ref | Device | Package | Schematic pin mapping | Footprint / polarity check |
|---|---|---|---|---|
| Q1 | SiSS23DN-T1-GE3 | PowerPAK 1212-8S | 1-3 S, 4 G, 5-8 D | Verify pad 1-3 source, pad 4 gate, 5-8 drain, exposed pad per Vishay datasheet |
| D1 | SS34 | SMA | 1 K, 2 A | K pad must have the cathode band; D1.1 K -> +5V, D1.2 A -> SW |
| C1-C3 | T520A107M006ATE070 | 1206/3216 polymer tantalum | 1 positive, 2 negative | Pin 1/+ marking and PCB silkscreen polarity required |
| U1 | STM32G030K8T6 | LQFP32 | pin 1 orientation; VDD/VDDA 4, VSS/VSSA 5, NRST 6 | Pin-1 corner and pad-1 orientation required |
| U2-U4 | MX113H | SOT-23-6 | 1 OUT2, 2 GND, 3 OUT1, 4 VCC, 5 IN1, 6 IN2 | Verify footprint pad numbering against LCSC C2845122 |
| U5 | MT3608 | SOT-23-6 | 1 SW, 2 GND, 3 FB, 4 EN, 5 VIN, 6 NC | NC pad 6 must not be connected; thermal copper required |
| U6 | TLV70033DDCR | SOT-23-5 | 1 IN, 2 GND, 3 EN, 4 NC, 5 OUT | NC pad 4 must not be connected |
| J7 | B6B-PH-K-S | JST PH 2.0 mm | 1-6 | Verify 2 A/AWG24 contact and cable-entry orientation |
| J5/J6 | SH1.0-3P | SH 1.0 mm | 1-3 | Verify purchased part, shield pins and 1 A rating |
| J2-J4/J9 | SH1.0-2P | SH 1.0 mm | 1-2 | Verify 1 A rating and shield/mechanical pads |
| J1 | XT30PW-M36 | XT30 | 1 +, 2 - | Verify pad polarity and 30 A class |

## D1 and C1-C3 polarity

- D1 is a boost rectifier: **anode to SW, cathode to +5V**. The RevB page now follows this.
- The selected SS34 library symbol has pin 1 = K and pin 2 = A. The PCB footprint must place the cathode band on the +5V side.
- C1-C3 are polarized polymer tantalum. Pin 1 is positive and must face VMOTOR; pin 2 is negative and must face GND. A silkscreen `+` and assembly polarity are required.

## J8 debug connector

Current J8 is a **2.54 mm HDR1X5** placeholder. It does not match the intended 1.27 mm pogo interface.

Proposed replacement:

- **Tag-Connect TC2030** 6-pad, 1.27 mm pitch, no-soldered-connector footprint.
- Mating cable: **TC2030-IDC** or **TC2030-IDC-NL** (choose the cable variant with the required legs/latching).
- Use the six pads for `+3V3`, `GND`, `SWDIO`, `SWCLK`, `NRST`, and one spare/GND.
- The footprint requires a small pad array and a keep-out for the cable; there is no 2.54 mm header.

This is a real pogo-pad/cable system, but the J8 symbol and footprint have **not** been replaced in the RevB schematic yet. The BOM now flags J8 as a placeholder and lists the proposed TC2030. Do not route the PCB with the current 2.54 mm footprint.

## Not claimed

- No PCB footprint placement, no DRC-clean result, no cathode/positive-terminal physical check.
- No connector fit test.
- No J8 replacement in the actual schematic.
