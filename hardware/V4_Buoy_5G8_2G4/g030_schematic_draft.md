# G030 schematic draft (connection level)

Status: **DRAFT / NOT EDA-ERC VERIFIED / NOT PRODUCTION READY.**
This is a connection-level draft to draw in JLCEDA Pro. It is not a `.esch2` schematic and no JLCEDA ERC has been run.

## 1. Page plan

| Page | Content |
|---|---|
| `01_POWER` | XT30, protected 1S pack, Q1 AON7403, MT3608 5V, TLV70033 3.3V, battery sense |
| `02_G030` | G030K8T6, VDD/VDDA pin4, VSS/VSSA pin5, NRST, SWD, PA14-BOOT0 option |
| `03_MOTOR` | 3x MX113H, motor connectors J2-J4, gate/decoupling |
| `04_IO` | Servo J5, camera J6, buoy J7, leak J9, LED, PP UART |

## 2. Power tree

```
Protected 1S pack -> XT30 J1 -> VBAT
VBAT -> Q1 AON7403 -> VMOTOR
VMOTOR -> U5 MT3608 -> 5V
5V -> U6 TLV70033 -> 3V3 -> U1 G030
```

- Q1 AON7403: source 1-3 = VBAT, gate 4 = PWR_GATE, drain 5-8 = VMOTOR. R5 100k pull-up, SW1 reed to GND, C14 100nF gate-source.
- U5 MT3608: VIN/EN = VMOTOR, SW = L1/D1, FB = R1/R2; L1 22uH, D1 SS34, C7 10uF, C8 22uF, R1 73.2k, R2 10k -> 5.0V; 5V/1A continuous.
- U6 TLV70033: IN/EN = 5V, OUT = 3V3; 200mA max.
- 5V loads: camera 0.1A + buoy 0.4A + servo 0.2A + LDO 0.02A = ~0.72A; 1A boost.
- 3.3V load: G030 ~20mA; 200mA LDO is enough.
- **BLOCKED:** 1S protection continuous/peak current, motor start/stall current, 5V input current and thermal are not measured.

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
- J5: 5V/GND/JAW.
- J6: 5V/GND/CAM_VIDEO.
- J7: +5V_BUOY, GND_PWR, CVBS_VIDEO, GND_VIDEO, PP_DOWN, TELEM_UP.
- J8: 3V3/GND/SWDIO/SWCLK/NRST.
- J9: LEAK/GND.

## 6. Netlist and BOM

- `g030_netlist_draft.csv` - 131 connections, 31 nets. Manual check: no single-node nets, no duplicate pins, no pin on two nets. This is **not** an EDA ERC.
- `control_bom.csv` - unique refs; MT3608/TLV70033/AON7403 are fixed, no "or" selection; no BOOT0 resistor; no separate VDDA/VSSA.

## 7. Not verified / BLOCKED

- JLCEDA `.esch2` drawing: not created; no ERC.
- Board outline/placement: not drawn; 26x40-46mm is a first-pass target only.
- Motor current/thrust/MX113H thermal: not measured.
- 5V boost inductor saturation/thermal: calculated only, not measured.
- Protected pack/J1/XT30/protection current: not measured.
- CVBS 75 ohm VTX termination: not confirmed.
- Positive buoyancy: design requirement, not tank-verified.
- **Do not order PCB or mark production-ready.**
