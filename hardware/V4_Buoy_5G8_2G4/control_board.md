# V4 shark G030 control board

V1 uses a new G030 board. It does only: `pp`, 3x MX113H, jaw servo, power, camera/buoy wiring, battery/leak safety. No RF, no camera processing.

## 1. Block diagram

```
Protected 1S pack (XT30)
  |-> VBAT -> Q1 SiSS23DN -> VMOTOR -> 3x MX113H -> 3 thrusters
  |-> VMOTOR -> U5 MT3608 +5V/1A -> +5V
        |-> camera +5V
        |-> buoy VTX/receiver +5V
        |-> jaw servo +5V
        |-> U6 TLV70033 3.3V/200mA -> +3V3 -> G030
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
| Status LED | PB0 | 15 | GPIO | Active high; PB0 -> R7 1k -> LED1 -> GND |
| Buoy PP RX | PA3 | 10 | AF1 | USART2_RX, 115200; `BUOY_RX` after R8 |
| Telemetry TX | PA2 | 9 | AF1 | USART2_TX; `TELEM_UP` |
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
- **VDD/VDDA pin 4** and **VSS/VSSA pin 5** are merged on LQFP32; no separate 3.3V_A/VDDA net. Canonical 3.3V net is `+3V3`.
- PP is normal 3.3V TTL; do not inherit the inverted-PP circuit. Canonical cable nets are `PP_DOWN` (F407 to G030) and `TELEM_UP` (G030 to F407).

## 3. MX113H

- 3x MX113H, SOT-23-6, one H-bridge each.
- Pins: 1 OUT2, 2 GND, 3 OUT1, 4 VCC, 5 IN1, 6 IN2 (verify against the exact datasheet).
- 2-8V, 1A continuous / 1.5A peak, Rds(on) 0.4 ohm, thermal shutdown.
- Forward IN1=PWM, IN2=0; reverse IN1=0, IN2=PWM; stop 0/0.
- 6 PWM, 20kHz; 100uF + 100nF at each VCC.
- **BLOCKED:** actual thruster running/start/stall current and MX113H temperature are not measured. Do not mark drive capability verified.

## 4. Power

- Protected 1S pack with PCM, XT30 connector; J1 XT30.
- Q1 **SiSS23DN-T1-GE3** P-MOS, PowerPAK 1212-8S: pin 1 gate, pins 2-4 source to VBAT, pins 5-8 drain to VMOTOR. R5 100k gate pull-up; SW1 reed to GND; C14 100nF gate-source. This replaces AON7403, which does not specify RDS(on) at VGS=-2.5V.
- Q1 budget: 3x MX113H at 1A continuous = 3A, plus 5V rail input at 3.0V/85% = 5V*1A/(0.85*3.0V) = 1.96A -> **~4.96A continuous**; 3x 1.5A MX113H peak + 1.96A = **~6.46A peak**. SiSS23DN is 50A package-limited, 27A at TA=25C, and 6.3mohm max at VGS=-2.5V. At 6.5A, P ~= 0.27W; using 63C/W steady-state RthJA, rise ~17C. Verify copper and thermal in layout.
- U5 **MT3608** SOT-23-6: VIN/EN VMOTOR; L1 22uH; D1 SS34; C7 10uF input; C8 22uF output; R1 73.2k / R2 10k feedback -> 5.0V; +5V/1A continuous.
- 5V load nominal: camera 0.1A + buoy 0.4A + servo 0.2A + LDO 0.02A = ~0.72A. At 3.0V/85%, the 5V rail alone draws **~1.96A** input, not 1.4A. L1 must have Isat >=3.5A and Irms >=2.2A; 2.5A saturation is not enough.
- Servo stall is **TBD**: a 5V hobby servo can exceed 0.2A and may exceed the remaining 1A boost headroom when camera/buoy loads are present. Measure stall current; if simultaneous stall + loads >1A, use a larger 5V source, separate servo rail, or enforce a load/current limit. Do not mark the 5V rail verified.
- U6 **TLV70033** 3.3V **200mA max** (not 300mA); G030 load is ~20mA; 200mA is enough.
- Battery sense R3/R4 100k/100k + C13 100nF to PA0.
- Leak: +3V3 -> R6 100k -> pad -> water -> GND -> PA1.
- **BLOCKED:** protection pack continuous/peak current, J1/XT30, motor start/stall current, servo stall current, and measured 5V input current.

## 5. Connectors and cable

| Ref | Type | Pinout |
|---|---|---|
| J1 | XT30 2P | VBAT, GND |
| J2 | JST-SH 2P | main motor OUT1/OUT2 |
| J3 | JST-SH 2P | lateral motor |
| J4 | JST-SH 2P | vertical motor |
| J5 | JST-SH 3P | +5V, GND, JAW_SERVO |
| J6 | JST-SH 3P | +5V, GND, CVBS_VIDEO |
| J7 | JST-PH 6P (proposed) | 1 +5V, 2 GND_PWR (board GND), 3 CVBS_VIDEO, 4 GND_VIDEO (board GND), 5 PP_DOWN, 6 TELEM_UP |
| J8 | 5 pogo | +3V3, GND, SWDIO, SWCLK, NRST |
| J9 | JST-SH 2P | leak pad, GND |

- J2-J4 are JST-SH 1A-class; if measured motor stall >1A, use JST-XH or solder pads.
- **J7 must not remain JST-SH.** JST-SH is 1A and 28-32AWG, so it is not compatible with 24AWG power/GND. Proposed J7 is **JST-PH 6P, 2.0mm, 2A at 24AWG, 24-30AWG**: header `B6B-PH-K-S`, housing `PHR-6`, terminal `SPH-002T-P0.5S`. This series change is **PENDING CONFIRMATION**; if 24AWG crimp/current is marginal or the 5V load rises above 2A, use JST-XH or a larger connector.
- Camera video J6 pin3 -> J7 pin3; J6 GND -> J7 pin4; the video return is tied to board GND at J7, so the cable still has a dedicated return pin.
- Buoy PP J7 pin5 -> R8 -> G030 PA3; G030 telemetry J7 pin6 -> buoy F407 RX.
- +5V/GND J7 pins1/2 -> buoy; 50cm cable: 24AWG for +5V/GND, 28AWG signals, separate shielded video pair/coax.
- 24AWG drop at 50cm: about 0.084 ohm loop, ~0.08V at 1A and ~0.17V at 2A; check the buoy input voltage under load.
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
- MX113H x3 near J2-J4; 1.5mm motor, 0.8mm +5V, 0.4mm +3V3.
- Q1 SiSS23DN: short/widened VBAT/VMOTOR copper and thermal vias under the PowerPAK 1212-8S exposed pad; verify temperature at ~6.5A peak.
- Camera video shielded/short; keep away from motor PWM; ground guard.
- UART series 22-100 ohm + TVS optional; cable shield to GND at one end.
- Boost/LDO away from video; input/output caps close.
- Fits a 35-40mm ID hull; 10-15cm shark.

## 8. Test

1. +3V3/+5V rails, current limit; check protection.
2. PP valid and malformed frames; H-bridges stay off at reset.
3. Each MX113H: forward/reverse/stop; running/stall current; heat at 1A.
4. Failsafe: stop PP; motors stop; jaw open.
5. Camera video J6->J7; 75 ohm/termination check.
6. Full 50cm cable + buoy tank test; positive buoyancy check.

## 9. Status

- Second P0 remediation updates net names, LED topology, Q1, J7, and MT3608 margin.
- Q1 is **SiSS23DN-T1-GE3** with a published 6.3mohm max at VGS=-2.5V; AON7403 is not approved for 1S gate drive.
- J7 is proposed as **JST-PH 6P**; the series change is pending confirmation. It must not silently remain JST-SH.
- L1 must be >=3.5A saturation / >=2.2A RMS; the previous 2.5A note was insufficient.
- G030 schematic is a **connection-level draft** (`g030_schematic_draft.md`), not a JLCEDA ERC-verified schematic.
- JLCEDA G030 board is still blank; ERC not run.
- Motor current, servo stall, protection current, 5V thermal, Q1 copper temperature, and board fit are **BLOCKED/TBD** until measured.
- `check_netlist.py` performs structural/netlist checks only; it is **not** ERC and does not prove the circuit.
