# G030 schematic draft (connection level)

Status: **DRAFTED IN JLCEDA PRO / FOUR A3 PAGES / REAL LIBRARY SYMBOLS / DRC HAS 138 WARNINGS / PCB EMPTY / NOT PRODUCTION READY.**
The connection-level reference is still this file plus `g030_netlist_draft.csv`. The real project is `hardware/g030_control/Shark_Sub_G030_RevB/Shark_Sub_G030_RevB.eprj3`; open the `Shark_Sub_G030` board -> `G030_Control` -> pages `01_POWER`, `02_G030`, `03_MOTOR`, `04_IO`. It has 45 real library components, 137 net-name stub wires and 32 nets. The netlist export matches the CSV exactly. DRC is not clean: 137 `NETOBJECTONGRID` warnings and one unused-pin warning. The PCB is empty by design.

## 1. Page plan

| Page | Content |
|---|---|
| `01_POWER` | XT30, protected 1S pack, Q1 SiSS23DN, MT3608 +5V, TLV70033 +3V3, battery sense |
| `02_G030` | G030K8T6, VDD/VDDA pin4, VSS/VSSA pin5, NRST, SWD, PA14-BOOT0 option |
| `03_MOTOR` | 3x MX113H, motor connectors J2-J4, gate/decoupling |
| `04_IO` | Servo J5, camera J6, buoy J7, leak J9, LED, PP UART |

## 2. Power tree

```
Protected 1S pack -> XT30 J1 -> VBAT
VBAT -> Q1 SiSS23DN -> VMOTOR
VMOTOR -> U5 MT3608 -> +5V
+5V -> U6 TLV70033 -> +3V3 -> U1 G030
```

- Q1 SiSS23DN-T1-GE3: pin 1 gate = PWR_GATE, pins 2-4 source = VBAT, pins 5-8 drain = VMOTOR. R5 100k pull-up, SW1 reed to GND, C14 100nF gate-source.
- Q1 is rated 20V/50A package-limited; RDS(on) 6.3mohm max at VGS=-2.5V. It replaces AON7403, which has no published -2.5V RDS(on). Verify the PowerPAK 1212-8S footprint and copper.
- U5 MT3608 is a candidate only: VIN/EN = VMOTOR, SW = L1/D1, FB = R1/R2; L1 SRP6060FA-220M 22uH, D1 SS34, C7/C8 22uF 25V, R1 73.2k, R2 10k -> 5.0V. **MT3608 thermal fails at 0.72A/1A from 3.0V; see `power_budget.md`.**
- U6 TLV70033: IN/EN = +5V, OUT = +3V3; 200mA max; C15 1uF input, C9 1uF output.
- +5V loads nominal: camera 0.1A + buoy 0.4A + servo 0.2A + LDO 0.02A = ~0.72A; 1A boost not thermally approved.
- Input current at 3.0V/85% for 5V/1A is ~1.96A; L1 Isat 5.6A, Irms 3.8A.
- +3V3 load: G030 ~20mA; 200mA LDO is enough.
- **BLOCKED:** 1S protection continuous/peak current, motor start/stall current, servo stall current, 5V input current and thermal are not measured.

## 3. MCU connections

See `control_pinout.csv` for the authoritative pin/AF table.

- PA8/PA9/PA10/PA11: TIM1_CH1-4 AF2, 20kHz (main/lateral).
- PA6/PA7: TIM3_CH1/2 AF1, 20kHz (vertical).
- PB1: TIM14_CH1 AF0, 50Hz jaw (Table 14).
- PB0: GPIO LED.
- PA3/PA2: USART2 RX/TX 115200.
- PA0: ADC battery; PA1: leak.
- PA13/PA14: SWD; PA14 pin25 is SWCLK/BOOT0, no separate BOOT0.
- VDD/VDDA pin4; VSS/VSSA pin5; NRST pin6.

## 4. MX113H

- U2 main, U3 lateral, U4 vertical.
- Pins: 1 OUT2, 2 GND, 3 OUT1, 4 VCC, 5 IN1, 6 IN2.
- IN1/IN2 from MCU; OUT1/OUT2 to J2-J4.
- 100uF + 100nF at each VCC; 20kHz PWM.
- **BLOCKED:** actual current/thrust/thermal not measured.

## 5. Connectors

- J1 XT30: VBAT/GND.
- J2/J3/J4: motor outputs.
- J5: +5V/GND/JAW_SERVO.
- J6: +5V/GND/CVBS_VIDEO.
- J7: +5V, GND_PWR (tied to board GND), CVBS_VIDEO, GND_VIDEO (tied to board GND), PP_DOWN, TELEM_UP. Proposed **JST-PH 6P**; SH is 1A/28-32AWG and cannot take 24AWG.
- J8: +3V3/GND/SWDIO/SWCLK/NRST.
- J9: LEAK/GND.

## 6. Netlist and BOM

- `g030_netlist_draft.csv` - 137 connections, 32 nets, 45 refs. Automated structural check passes; this is **not** an EDA ERC.
- `check_netlist.py` - committed structural checker; run `python hardware/V4_Buoy_5G8_2G4/check_netlist.py`.
- `tests/run_negative_tests.py` - six negative tests; all rejected as expected.
- `hardware/g030_control/Shark_Sub_G030_RevB/` - real JLCEDA Pro project with four A3 pages; 45 system-library components, 137 net-name stubs, 32 nets. Netlist export matches CSV; DRC has 138 warnings; PCB empty.
- `hardware/g030_control/netlist_compare.json` - exported netlist vs CSV: 137/137 pins, 32/32 nets, no missing/extra.
- `hardware/g030_control/drc_result.json` - GUI DRC warning list.
- `control_bom.csv` - unique refs; MT3608/TLV70033/SiSS23DN are fixed, no "or" selection; no BOOT0 resistor; no separate VDDA/VSSA. C1-C3 are polymer 1206, C15-C17 added.

## 7. Not verified / BLOCKED

- JLCEDA project is opened and drafted with real library symbols, but DRC has 137 `NETOBJECTONGRID` warnings plus one unused-pin warning; no PCB layout, no footprints placed on a board, no clean ERC claim.
- MT3608 thermal budget fails at 0.72A/1A from 3.0V; the 5V rail is not approved. See `power_budget.md`.
- Board outline/placement: PCB is empty; 26x40-46mm is a first-pass target only.
- Motor current/thrust/MX113H thermal: not measured.
- L1 SRP6060FA-220M saturation/thermal: calculated only, not measured.
- Servo current/stall and simultaneous +5V load: not measured.
- C1-C3 100uF polymer ripple/temperature: not measured.
- Protected pack/J1/XT30/protection current: not measured.
- Q1 PowerPAK 1212-8S footprint/copper temperature: not verified.
- J7/cable mechanical fit: envelope model only, not physically checked.
- CVBS 75 ohm VTX termination: not confirmed.
- Positive buoyancy: design requirement, not tank-verified.
- **Do not order PCB or mark production-ready.**
