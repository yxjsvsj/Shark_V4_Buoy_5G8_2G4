# G030 component and footprint binding review

Status: **PARTIAL / RevB uses real JLCEDA library devices; connector and NC-pin review remains.**

The four-page RevB project (`Shark_Sub_G030_RevB`) uses JLCEDA system-library devices, not the generic symbols from the old generator candidate. The legacy candidate is explicitly `FOOTPRINT BLOCKED`.

## Key devices

| Ref | Library device | LCSC | Package | Pin check |
|---|---|---|---|---|
| U1 | STM32G030K8T6 | C431631 | LQFP32 | 32 pins; VDD/VDDA pin 4, VSS/VSSA pin 5, NRST pin 6, PA13/PA14 SWD |
| U2-U4 | MX113H | C2845122 | SOT-23-6 | 1 OUT2, 2 GND, 3 OUT1, 4 VCC, 5 IN1, 6 IN2 |
| U5 | MT3608 | C84817 | SOT-23-6 | 1 SW, 2 GND, 3 FB, 4 EN, 5 VIN, 6 NC |
| U6 | TLV70033DDCR | C11337 | SOT-23-5 | 1 IN, 2 GND, 3 EN, 4 NC, 5 OUT |
| Q1 | SiSS23DN-T1-GE3 | C222439 | PowerPAK 1212-8S | 1 G, 2-4 S, 5-8 D |
| D1 | SS34 | - | SMA | A/K mapping checked against symbol; PCB polarity must be marked |
| C1-C3 | T520A107M006ATE070 | C561794 | 1206/3216 | polarized tantalum; + terminal must be marked on PCB |
| L1 | SRP6060FA-220M | C2045802 | 6.6x6.4 mm | 22 uH, 5.6 A Isat, 3.8 A Irms |
| J7 | B6B-PH-K-S(LF)(SN) | C131342 | PH 2.0 mm | 1-6; 2 A at AWG24 |
| J5/J6 | SH1.0-3P | C9900019066 | SH 1.0 mm | 1-3 plus shield pin |
| J2-J4/J9 | SH1.0-2P | C9900019065 | SH 1.0 mm | 1-2 plus shield pins |
| J8 | HDR1X5 | C9900014775 | 2.54 mm | 1-5; not a 1.27 mm pogo array |

## What is verified

- Device records exist in the JLCEDA project with library symbol, footprint and 3D model references.
- The exported netlist matched the CSV 137/137.
- D1 and C1-C3 use library symbols with polarity/terminal names; the PCB footprint polarity still needs a visual check.
- The four-page project opens in JLCEDA and DRC was run.

## What is not verified

- Exact connector mechanical part numbers versus purchased parts (J5/J6/J2-J4/J9/J8 are closest library parts, not final mechanical selections).
- All NC pins are not explicitly marked no-connect; DRC has one `CHECKFLOATPIN` warning.
- Footprint pad numbering and solder-mask/assembly drawings have not been visually checked against every datasheet.
- No PCB layout or footprint placement exists.

Do not claim “all footprints verified” until the PCB is laid out and each library device is checked against the exact purchased part.
