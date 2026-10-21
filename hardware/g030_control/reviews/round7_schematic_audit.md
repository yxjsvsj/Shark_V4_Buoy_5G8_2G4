# Round 7 RevB schematic audit

Date: 2026-10-21. Baseline: `62098cf`. Project: `hardware/g030_control/Shark_Sub_G030_RevB/Shark_Sub_G030_RevB.eprj3`.

Status: **TEXT PAGE + PARTIAL GUI VISUAL / GUI EXPORT BLOCKED / PCB EMPTY / NOT READY.**

## Scope and evidence limits

- All four `.esch2` files were parsed: 137 pins, 32 nets, 45 RefDes.
- JLCEDA Pro V4.1.78 was opened and 01_POWER was checked visually for Q1 and D1; 02_G030 and 04_IO were also displayed during the session. 03_MOTOR was not individually captured.
- `g030_export.net` is the **provisional** file from round 6, not a fresh GUI export. It is not used as proof of GUI connectivity.
- No PCB is placed. Footprint pad numbering and physical polarity remain unverified.
- `round7_pin_net_matrix.csv` contains the 137-row RefDes/pin/net/package/risk/status table.
- Page pin counts: 01_POWER 47, 02_G030 38, 03_MOTOR 36, 04_IO 16. High-risk rows: 77; medium: 18; low: 42.

## Actual conclusions

### Confirmed correct

- Q1.1/2/3 Source -> VBAT; Q1.4 Gate -> PWR_GATE; Q1.5-8 Drain -> VMOTOR. Confirmed visually in the GUI and in the corrected page.
- D1.1 K -> +5V; D1.2 A -> SW. Confirmed visually in the GUI.
- R5 is VBAT-to-PWR_GATE, SW1 PWR_GATE-to-GND, C14 across gate-source.
- U1.4 VDD/VDDA -> +3V3; U1.5 VSS/VSSA -> GND; U1.6 NRST -> NRST; U1.24/25 SWDIO/SWCLK.
- U2-U4 pin map matches the Mixic MX113H datasheet: 1 OUT2, 2 GND, 3 OUT1, 4 VCC, 5 IN1, 6 IN2.
- J7.5 is the buoy-to-shark PP path through R8 to U1.10 (USART2_RX); J7.6 is the shark-to-buoy telemetry path from U1.9 (USART2_TX).

### Real problems / gaps

| ID | Problem | Evidence | Status |
|---|---|---|---|
| R7-01 | J8 is a 2.54 mm HDR1X5 in the actual schematic, not the intended 1.27 mm pogo interface | RevB 02_G030 page; BOM placeholder | **NOT FIXED in schematic** |
| R7-02 | LimeRC PP default is inverted and output-disabled until the receiver setting is applied | `nrfMessage.c` calls `ChangeCodecTo(PP, true, false)`; XOR U7 on schematic | **CONFIGURATION GATE** |
| R7-03 | No depth sensor, no depth-control interface, no depth fail-safe | RevB netlist has no pressure sensor; PA4/PA5 are not I2C | **MISSING / PROPOSED** |
| R7-04 | PA4/PA5 cannot be I2C on STM32G030; they are SPI/TIM pins | STM32G030 datasheet Table 13 | **VERIFIED constraint** |
| R7-05 | 5 m buoy cable is not designed; current assumptions are 50 cm and J7 PH 2 A | control_board, J7 notes | **BLOCKED** |
| R7-06 | MX113H 1 A continuous / 1.5 A peak in SOT-23-6, 0.4 ohm, 220 C/W; three units in a sealed hull have no thermal margin | MX113H datasheet | **MEASUREMENT/DERATING REQUIRED** |
| R7-07 | J2-J4 are JST-SH 1 A class but motor peak is 1.5 A | BOM and schematic | **NOT READY** |
| R7-08 | U5 MT3608 cannot be called capable at 0.72/1 A; TPS61022 is only a candidate | power_budget/options | **POWER BLOCKED** |
| R7-09 | U5.6 and U6.4 are absent from the netlist but no explicit NC flag is visible; CHECKFLOATPIN warning remains | netlist/DRC | **NC UNMARKED** |
| R7-10 | No reverse-polarity protection, no battery protection IC/MOSFET in the schematic; protected pack is assumed | 01_POWER | **ASSUMPTION** |
| R7-11 | PP/UART and CVBS have no TVS/series protection on the 5 m cable | 04_IO | **ESD/CABLE RISK** |
| R7-12 | Leak probe uses DC +3V3 through 100k into water; long-term electrolysis/corrosion risk | 04_IO | **DESIGN RISK** |
| R7-13 | J7 combines 5 V power, PP, telemetry and CVBS; 5 m drop and connector current are not proven | 04_IO | **BLOCKED** |
| R7-14 | Q1 hold-to-run magnet switch has no self-latch; MCU reset behavior is power-off, but operation requires the magnet to remain in place | 01_POWER | **DECISION_REQUIRED** |
| R7-15 | 137 NETOBJECTONGRID and 1 CHECKFLOATPIN remain; no full object/page log | drc_result | **GUI DRC BLOCKED** |

## Page-by-page notes

### 01_POWER

- Q1 and D1 are correct as above.
- U5 MT3608 pin map is 1 SW, 2 GND, 3 FB, 4 EN, 5 VIN, 6 NC; EN tied to VMOTOR, FB divider R1/R2. The converter is not thermally qualified.
- C1-C3 are polarized polymer tantalum; pin 1 must be positive. No PCB marking exists yet.
- L1 SRP6060FA-220M is oversized for MT3608 but its current rating is helpful; TPS61022 would need a different inductor.
- No battery protection or reverse-polarity device is drawn; the XT30 and protected pack are assumptions.
- R5/SW1/C14 hold-to-run is understandable but not an operational latch. See `round7_power_review.md`.

### 02_G030

- U1 pin 4/5 are merged supply pins and correctly tied to +3V3/GND.
- PA4 (pin 11) and PA5 (pin 12) are not I2C-capable on this package. They are SPI1_NSS/SPI2_MOSI/TIM14_CH1 and SPI1_SCK. Do not use the proposed depth sensor there.
- PB6 (pin 30) and PB7 (pin 31) are spare and are I2C1_SCL/SDA. This is the lowest-conflict proposed depth interface.
- J8 must be replaced by a 6-pad 1.27 mm Tag-Connect TC2030 or an equivalent real pogo footprint; the current 2.54 mm header is only a placeholder.
- C16/C17 are connector decoupling; C10/C11 are MCU decoupling.

### 03_MOTOR

- U2-U4 pin mapping is correct per the MX113H datasheet.
- The driver is rated 1 A continuous at 25 C, 1.5 A peak, RDS(on) 0.4 ohm, thetaJA 220 C/W, thermal shutdown 150 C. At 1 A the package dissipates about 0.4 W and rises about 88 C; sealed 40 C ambient is near the limit. At 1.5 A peak the rise is much higher and is transient-only.
- Three thrusters at 1 A each cannot be called simultaneous continuous. Measure running/stall current and derate, or use a lower-RDS(on) driver.
- J2-J4 are 1 A JST-SH parts; replace with JST-XH, solder pads or another 2 A+ connector if measured stall approaches or exceeds 1 A.

### 04_IO

- J7 is a custom 6-pin buoy interface, not the LimeRC GH1.25 Mult-Bus connector. The mapping is 1 +5V, 2 GND, 3 CVBS, 4 video GND, 5 PP_DOWN, 6 TELEM_UP.
- The PP and telemetry directions are correct, but LimeRC's actual output may be inverted/disabled at boot. Set the receiver to normal TTL and capture the UART before freezing the interface.
- The 5 m cable needs 18-20 AWG power conductors or a separate power connector; 24 AWG over a 10 m loop has about 0.84 ohm and drops ~0.6 V at 0.72 A, more at 1 A.
- CVBS must use a 75 ohm coax or controlled pair with proper termination; the current schematic does not show a 75 ohm termination or TVS.
- J9 leak probe is a DC electrode; use a pulsed/AC-excited probe or accept corrosion and frequent cleaning.

## Matrix

See `round7_pin_net_matrix.csv`. The matrix is based on the page text and provisional export; it is not a GUI-exported netlist. Rows marked `GUI_VISUAL_OK` apply only to Q1/D1 after the GUI check.
