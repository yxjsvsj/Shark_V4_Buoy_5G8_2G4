# V4 shark G030 control board

V1 uses a new G030 board. It does only: `pp`, 3x MX113H, jaw servo, power, camera/buoy wiring, battery/leak safety. No RF, no camera processing.

Status: Q1 Source/Gate and D1 polarity are corrected in the RevB source, but the GUI netlist export, DRC log and footprint checks are incomplete. **Do not connect a battery or power the board.** The first power-up must use a current-limited supply with no motors, servo, camera or buoy.

## 1. Block diagram

```
Protected 1S pack (XT30)
  |-> VBAT -> Q1 SiSS23DN -> VMOTOR -> 3x MX113H -> 3 thrusters
  |-> VMOTOR -> U5 MT3608 +5V candidate -> +5V
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
- Q1 **SiSS23DN-T1-GE3** P-MOS, PowerPAK 1212-8S: pins 1-3 source to VBAT, pin 4 gate to PWR_GATE, pins 5-8 drain to VMOTOR. R5 100k gate pull-up; SW1 reed to GND; C14 100nF gate-source. This replaces AON7403, which does not specify RDS(on) at VGS=-2.5V.
- Q1 budget: 3x MX113H at 1A continuous = 3A, plus 5V rail input at 3.0V/85% = 1.96A -> **~4.96A continuous**; 3x 1.5A MX113H peak + 1.96A = **~6.46A peak**. SiSS23DN is 50A package-limited, 27A at TA=25C, and 6.3mohm max at VGS=-2.5V. At 6.5A and 1.4x hot RDS(on), P ~= 0.37W; with 63C/W steady-state RthJA, rise ~23C. Verify copper and temperature.
- U5 **MT3608** SOT-23-6 is retained only as a **candidate and is BLOCKED**. The corrected loss split (SS34, L1 DCR/core, MT3608 conduction/switching/gate/quiescent) gives MT3608 TJ roughly 63-86C at 0.4A, 83-129C at 0.72A, and **106-180C at 1A** (40C ambient, 250C/W). The 1A max case exceeds the junction limit; the typical case is about 106C. This is an uncertainty, not a proven pass or fail.
- D1 SS34: library pin 1 K -> +5V, pin 2 A -> SW. PCB SMA cathode marking remains TBD.
- MT3608 parts: L1 **Bourns SRP6060FA-220M** 22uH, 6.6x6.4mm, Isat 5.6A, Irms 3.8A, DCR 55mohm; D1 SS34; C7/C8 22uF 25V 0805 X5R; R1 73.2k / R2 10k. See `power_budget.md` for loss allocation and sensitivity.
- 5V load nominal: camera 0.1A + buoy 0.4A + servo 0.2A + LDO 0.02A = ~0.72A. At 3.0V/85%, the 5V rail alone draws **~1.96A** input. The 85% figure is optimistic at 1A; measure efficiency.
- Servo stall is **TBD** and not assumed to be 0.2A. With 0.52A of other load, 0.5A servo current already exceeds 1A. **Do not mark the 5V rail capable or failed until the load/thermal test is run.** Resize/split the source or reduce the load after measuring.
- C1/C2/C3: **KEMET T520A107M006ATE070**, 100uF 6.3V polymer tantalum, 1206/3216, 70mohm ESR. This replaces the unreliable 100uF/0805 X5R assumption. Ripple rating is 1.035A at 45C, 724.5mA at 85C; verify 20kHz motor ripple and case temperature.
- C15 adds 1uF at the TLV70033 input; C16/C17 add 100nF at the camera and buoy connectors.
- U6 **TLV70033** 3.3V **200mA max** (not 300mA); G030 load is ~20mA; C9/C15 1uF and C10/C11 decoupling.
- Battery sense R3/R4 100k/100k + C13 100nF to PA0.
- Leak: +3V3 -> R6 100k -> pad -> water -> GND -> PA1.
- **BLOCKED:** MT3608 thermal validation, protection pack current, motor start/stall current, servo current/stall, 5V transient, and C1-C3 ripple/temperature.

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
| J8 | HDR1X5 2.54mm placeholder | +3V3, GND, SWDIO, SWCLK, NRST; replace with Tag-Connect TC2030 6-pad 1.27mm pogo before layout |
| J9 | JST-SH 2P | leak pad, GND |

- J2-J4 are JST-SH 1A-class; if measured motor stall >1A, use JST-XH or solder pads.
- **J7 must not remain JST-SH.** JST-SH is 1A and 28-32AWG, so it is not compatible with 24AWG power/GND. Proposed J7 is **JST-PH 6P, 2.0mm, 2A at 24AWG, 24-30AWG**: header `B6B-PH-K-S`, housing `PHR-6`, terminal `SPH-002T-P0.5S`. This series change is **PENDING CONFIRMATION**; if 24AWG crimp/current is marginal or the 5V load rises above 2A, use JST-XH or a larger connector.
- Camera video J6 pin3 -> J7 pin3; J6 GND -> J7 pin4; the video return is tied to board GND at J7, so the cable still has a dedicated return pin.
- Buoy PP J7 pin5 -> R8 -> G030 PA3; G030 telemetry J7 pin6 -> buoy F407 RX.
- +5V/GND J7 pins1/2 -> buoy; 50cm cable: 24AWG for +5V/GND, 28AWG signals, separate shielded video pair/coax.
- 24AWG drop at 50cm: about 0.084 ohm loop, ~0.08V at 1A and ~0.17V at 2A; check the buoy input voltage under load.
- **Cable OD is not 3mm.** Two 24AWG power wires, two 28AWG signal wires, a 75 ohm micro coax, shield/filler and jacket yield about **5.0-5.5mm** finished OD. See `mechanical/j7_assembly.md`.
- Mated connector envelope is about 13.9 x 4.5 x 8.0mm. A 5.5mm cable needs about 30mm static / 55mm dynamic bend radius. A top-entry J7 plus that bend is tight in the 55x70mm buoy; a side-entry header or larger buoy may be required.
- 24AWG insulation OD must be 0.9-1.5mm for `SPH-002T-P0.5S`; crimp pull test and housing latch are required.
- 50cm is a shallow-test version; for 50cm depth plus float/connector margin, make a longer version.
- CVBS is 75 ohm; check whether the VTX input has 75 ohm termination.

## 6. Safety

- H-bridges off at reset: IN1=IN2=0; no motion before valid PP.
- PP parser validates header, field count, ranges; malformed frames rejected.
- PP link-loss source behavior: after about 100ms without an NRF packet, LimeCam sends **one neutral frame** (sticks 2048), then stops sending. It does not repeat the last frame. Evidence: `pp_link_behavior.md`.
- G030 records the last valid PP timestamp. **500ms no valid PP -> motors 0, jaw open, LED blink.** The 500ms timeout is the link-freshness detector; do not use repeated channel values as proof of link health.
- Exact receiver firmware must be verified by a UART capture; a different build may not match the reviewed source.
- A receiver link-status wire is not available on J7. If independent status is required, use a 7-pin cable or a defined telemetry frame; do not repurpose `TELEM_UP`.
- Magnet switch is **hold-to-run**: the magnet must stay near SW1 to keep Q1 on. A short-touch toggle requires a latch and is **not designed**.
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
6. Link loss: disconnect only 2.4GHz; confirm one neutral PP frame then silence, and G030 failsafe within 500ms.
7. MT3608: 3.0V input at 0.4/0.72/1.0A; record case temperature, 5V ripple and shutdown. Treat 0.72/1.0A as fail if TJ/package limits are exceeded.
8. J7: 24AWG crimp pull test, housing latch, 30mm bend, gland mock-up.
9. Full 50cm cable + buoy tank test; positive buoyancy check.

## 9. Status

- Third-round review adds PP link-loss evidence, corrected MT3608 loss/TJ analysis, polymer motor capacitors, separate J7 models, and candidate schematic checks.
- Q1 is **SiSS23DN-T1-GE3** with a published 6.3mohm max at VGS=-2.5V; AON7403 is not approved for 1S gate drive.
- J7 is proposed as **JST-PH 6P**; the series change is pending confirmation. Cable OD is **5.0-5.5mm**, not 3mm; top-entry plus bend is tight.
- **MT3608 is BLOCKED pending measured efficiency/case temperature**; corrected chip-loss analysis is 63-86C at 0.4A, 83-129C at 0.72A and 106-180C at 1A. The 5V architecture is not approved or declared impossible.
- L1 is now **SRP6060FA-220M** (22uH, Isat 5.6A, Irms 3.8A); the previous 6x6 1.8A part is insufficient.
- C1-C3 are **100uF 6.3V polymer tantalum 1206**, not 100uF/0805 X5R. C15/C16/C17 add LDO input and connector decoupling.
- G030 schematic: `hardware/g030_control/Shark_Sub_G030_RevB/Shark_Sub_G030_RevB.eprj3`; four A3 pages, real library symbols, 45 components, 137 net stubs, 32 nets. Netlist matches CSV; DRC has 138 warnings (137 NETOBJECTONGRID + 1 unused-pin); PCB empty.
- `check_netlist.py` results: 137 rows, 32 nets, 45 refs; six negative tests pass. This is **not** EDA ERC.
- Round 7 adds no depth sensor to the real RevB schematic. Proposed I2C1 is **PB6/PB7**, not PA4/PA5 (PA4/PA5 have no I2C function on STM32G030). See `reviews/round7_depth_control.md`.
- LimeRC receiver boots PP inverted/output-disabled; set it to normal TTL and capture the UART. LimeRC video is OV2640 digital, not CVBS; Shark J6/J7 CVBS is an independent chain.
- A 5 m cable cannot use the 50 cm/24AWG/JST-PH power assumption. Use 18-20AWG power or a separate IP68 connector; exact type TBD.
- MX113H is 1A continuous at 25C/0.4ohm/220C/W; sealed-hull continuous current must be derated, and J2-J4 JST-SH 1A connectors are not approved for 1.5A peaks.
- Motor current, servo current/stall, protection current, MT3608 thermal, C1-C3 ripple, and board fit remain **BLOCKED/TBD** until measured.
