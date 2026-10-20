# V4 shark G030 control board

V1 uses a new G030 board. It does only: `pp`, 3x MX113H, jaw servo, power, camera/buoy wiring, battery/leak safety. No RF, no camera processing.

## 1. Block diagram

```
Protected 1S pack (XT30)
  |-> VBAT -> Q1 AON7403 -> VMOTOR -> 3x MX113H -> 3 thrusters
  |-> VMOTOR -> U5 MT3608 5V/1A -> 5V
        |-> camera 5V
        |-> buoy VTX/receiver 5V
        |-> jaw servo 5V
        |-> U6 TLV70033 3.3V/200mA -> G030
```

- 3.3V comes from 5V; no 1S-to-3.3V LDO.
- 5V boost is **MT3608 only** (not "MT3608 or TPS61023").
- 5V continuous load is ~0.72A; MT3608 is used at 1A max, not 2A.

## 2. MCU and pin map

MCU: **STM32G030K8T6, LQFP32, 64KB flash, 8KB RAM.**

| Function | Pin | LQFP32 | AF | Notes |
|---|---|---|---|---|
| Main IN1 | PA8 | 18 | AF2 | TIM1_CH1, 20kHz |
| Main IN2 | PA9 | 19 | AF2 | TIM1_CH2, 20kHz |
| Lateral IN1 | PA10 | 21 | AF2 | TIM1_CH3, 20kHz |
| Lateral IN2 | PA11 | 22 | AF2 | TIM1_CH4, 20kHz |
| Vertical IN1 | PA6 | 13 | AF1 | TIM3_CH1, 20kHz |
| Vertical IN2 | PA7 | 14 | AF1 | TIM3_CH2, 20kHz |
| Jaw servo | PB1 | 16 | AF0 | TIM14_CH1, 50Hz; Table 14 AF0 |
| Status LED | PB0 | 15 | GPIO | Active high |
| Buoy PP RX | PA3 | 10 | AF1 | USART2_RX, 115200 |
| Telemetry TX | PA2 | 9 | AF1 | USART2_TX |
| Battery sense | PA0 | 7 | ADC_IN0 | 100k/100k |
| Leak | PA1 | 8 | GPIO | 100k pull-up |
| SWDIO | PA13 | 24 | AF0 | SWD |
| SWCLK/BOOT0 | PA14 | 25 | AF0 | SWCLK; no separate BOOT0 pin |
| VDD/VDDA | 4 | - | PWR | Merged; 100nF + 4.7uF |
| VSS/VSSA | 5 | - | PWR | Merged |
| NRST | 6 | - | RST | 100nF; SWD NRST |

Notes:

- **PA11[PA9]**: pin 22 is PA11 by default, TIM1_CH4 AF2. Do **not** enable the SYSCFG PA9/PA10 remap to PA11/PA12; use PA9 pin 19, PA10 pin 21, PA11 pin 22. PA12 pin 23 is unused.
- **PA14-BOOT0**: pin 25 is SWCLK + BOOT0 option. Do not draw a separate BOOT0 pin or resistor. The internal pull-down is active; nBOOT_SEL default 1 means BOOT0 is not sampled. Use option bytes; include NRST on SWD.
- **VDD/VDDA pin 4** and **VSS/VSSA pin 5** are merged on LQFP32; no separate 3.3V_A/VDDA net.
- PP is normal 3.3V TTL; do not inherit the inverted-PP circuit.

## 3. MX113H

- 3x MX113H, SOT-23-6, one H-bridge each.
- Pins: 1 OUT2, 2 GND, 3 OUT1, 4 VCC, 5 IN1, 6 IN2 (verify against the exact datasheet).
- 2-8V, 1A continuous / 1.5A peak, Rds(on) 0.4 ohm, thermal shutdown.
- Forward IN1=PWM, IN2=0; reverse IN1=0, IN2=PWM; stop 0/0.
- 6 PWM, 20kHz; 100uF + 100nF at each VCC.
- **BLOCKED:** actual thruster running/start/stall current and MX113H temperature are not measured. Do not mark drive capability verified.

## 4. Power

- Protected 1S pack with PCM, XT30 connector; J1 XT30.
- Q1 **AON7403** P-MOS, DFN3x3: source 1-3 to VBAT, gate 4, drain 5-8 to VMOTOR (verify pinout). R5 100k gate pull-up; SW1 reed to GND; C14 100nF gate-source.
- U5 **MT3608** SOT-23-6: VIN/EN VMOTOR; L1 22uH; D1 SS34; C7 10uF input; C8 22uF output; R1 73.2k / R2 10k feedback -> 5.0V; 5V/1A continuous.
- 5V load: camera 0.1A + buoy 0.4A + servo 0.2A + LDO 0.02A = ~0.72A. At 3.0V/85%, input ~1.4A for the 5V rail; add motor current.
- U6 **TLV70033** 3.3V **200mA max** (not 300mA); G030 load is ~20mA; 200mA is enough.
- Battery sense R3/R4 100k/100k + C13 100nF to PA0.
- Leak: 3V3 -> R6 100k -> pad -> water -> GND -> PA1.
- **BLOCKED:** protection pack continuous/peak current, J1/XT30, motor start current and 5V input current must be measured.

## 5. Connectors and cable

| Ref | Type | Pinout |
|---|---|---|
| J1 | XT30 2P | VBAT, GND |
| J2 | JST-SH 2P | main motor OUT1/OUT2 |
| J3 | JST-SH 2P | lateral motor |
| J4 | JST-SH 2P | vertical motor |
| J5 | JST-SH 3P | 5V, GND, jaw servo |
| J6 | JST-SH 3P | 5V, GND, camera video |
| J7 | JST-SH 6P | 1 +5V_BUOY, 2 GND_PWR, 3 CVBS_VIDEO, 4 GND_VIDEO, 5 PP_DOWN, 6 TELEM_UP |
| J8 | 5 pogo | 3V3, GND, SWDIO, SWCLK, NRST |
| J9 | JST-SH 2P | leak pad, GND |

- J2-J4 are JST-SH 1A-class; if measured motor stall >1A, use JST-XH or solder pads.
- Camera video J6 pin3 -> J7 pin3; J6 GND -> J7 pin4 (GND_VIDEO); do not leave GND_VIDEO floating.
- Buoy PP J7 pin5 -> G030 PA3; G030 telemetry J7 pin6 -> buoy F407 RX.
- 5V/GND J7 pins1/2 -> buoy; 50cm cable: 24AWG for 5V/GND, 28AWG signals, separate shielded video pair/coax.
- 50cm is a shallow-test version; for 50cm depth plus float/connector margin, make a longer version.
- CVBS is 75 ohm; check whether the VTX input has 75 ohm termination.

## 6. Safety

- H-bridges off at reset: IN1=IN2=0; no motion before valid PP.
- PP parser validates header, field count, ranges; malformed frames rejected.
- 500ms no valid PP -> motors 0, jaw open, LED blink.
- IWDG 1s; low voltage (<3.4V) or leak -> safe state.
- Jaw 0-45 deg; spring-open on power loss.
- Shark must be slightly positive buoyancy; surfaces on power/control loss.

## 7. Board size and layout

- First pass: **26x40-46mm**, 4-layer; target 20x30mm only after layout feasibility.
- MX113H x3 near J2-J4; 1.5mm motor, 0.8mm 5V, 0.4mm 3.3V.
- Camera video shielded/short; keep away from motor PWM; ground guard.
- UART series 22-100 ohm + TVS optional; cable shield to GND at one end.
- Boost/LDO away from video; input/output caps close.
- Fits a 35-40mm ID hull; 10-15cm shark.

## 8. Test

1. 3.3V/5V rails, current limit; check protection.
2. PP valid and malformed frames; H-bridges stay off at reset.
3. Each MX113H: forward/reverse/stop; running/stall current; heat at 1A.
4. Failsafe: stop PP; motors stop; jaw open.
5. Camera video J6->J7; 75 ohm/termination check.
6. Full 50cm cable + buoy tank test; positive buoyancy check.

## 9. Status

- Pin/power/BOM corrections are in this branch.
- G030 schematic is a **connection-level draft** (`g030_schematic_draft.md`), not a JLCEDA ERC-verified schematic.
- JLCEDA G030 board is still blank; ERC not run.
- Motor current, protection current, 5V thermal, and board fit are **BLOCKED/TBD** until measured.
