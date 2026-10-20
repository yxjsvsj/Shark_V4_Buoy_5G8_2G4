# V4 shark G030 control board

V1 uses a new G030 board (the user has no original driver board). The board does only: `pp`, 3x MX113H, jaw servo, power, camera/buoy wiring, battery/leak safety. No RF, no camera processing.

## 0. Board role

- Buoy F407 receiver -> `pp` 115200 -> G030 UART2.
- 3 thrusters: main, lateral, vertical.
- 1 jaw servo.
- Camera CVBS passes through to the buoy; it does not enter the MCU.
- No 2.4G/5.8G/OV2640 on this board.

## 1. Block diagram

```
Protected 1S LiPo
  |-> VBAT_MOTOR -> 3x MX113H -> 3 thrusters
  |-> P-MOS switch -> 5V boost 2A -> 5V
        |-> camera 5V
        |-> buoy VTX/receiver 5V
        |-> jaw servo 5V
        |-> 3.3V LDO -> G030
```

- 3.3V must come from 5V (or a dedicated 3.3V buck-boost), not directly from a 1S LDO.
- 5V boost input current must be summed with motor current; check battery/protection.
- Do not stack a second boost without checking the LimeMini original power design.

## 2. MCU and pin map

MCU: **STM32G030K8T6, LQFP32, 64KB flash, 8KB RAM.**

| Function | Pin | Peripheral |
|---|---|---|
| Main motor IN1 | PA8 | TIM1_CH1 |
| Main motor IN2 | PA9 | TIM1_CH2 |
| Lateral motor IN1 | PA10 | TIM1_CH3 |
| Lateral motor IN2 | PA11 | TIM1_CH4 |
| Vertical motor IN1 | PA6 | TIM3_CH1 |
| Vertical motor IN2 | PA7 | TIM3_CH2 |
| Jaw servo | PB0 | TIM3_CH3, 50Hz |
| Buoy `pp` RX | PA3 | USART2_RX, 115200 |
| Telemetry TX | PA2 | USART2_TX, optional |
| Battery sense | PA0 | ADC_IN0 |
| Leak sense | PA1 | GPIO input |
| Status LED | PB1 | GPIO |
| SWD | PA13/PA14 | SWD |
| Spare | PA4/PA5/PA12/PB2-PB7 | Keep pads |

Motor PWM: 20kHz. Servo: 50Hz, 500-2500us. PP is **normal 3.3V TTL**, not inverted; confirm the receiver firmware matches.

## 3. Motor drivers

- 3x **MX113H**, SOT-23-6, one H-bridge each.
- 2-8V, 1A continuous / 1.5A peak, Rds(on) 0.4 ohm, thermal shutdown.
- IN1/IN2:
  - forward: IN1=PWM, IN2=0
  - reverse: IN1=0, IN2=PWM
  - stop: IN1=0, IN2=0
  - brake: IN1=1, IN2=1
- 6 PWM, 20kHz; 100uF + 100nF at each VCC; keep motor connectors short.
- **Before layout:** measure each thruster with prop: running current, start-up peak, stall current, thrust. If peak >1.5A, change motor/driver.
- Check SOT-23-6 copper/thermal; 1A continuous is the limit, not a target.

## 4. Power and protection

- Protected 1S battery (DW01A/FS8205A or equivalent) -> `VBAT_MOTOR`.
- Check protection continuous/peak current; 3 motors + 5V load may exceed a small FS8205A.
- 5V boost 2A: camera 0.1A + buoy 0.4A + servo 0.2A + 3.3V LDO 0.05A = ~0.75A.
- At 5V/2A full load, 3.3V/85% input is ~3.6A; actual buoy load is lower, but sum motor peaks.
- 3.3V LDO from 5V (e.g., TLV70033 300mA) is acceptable; a dedicated buck-boost is better if the 5V rail is noisy.
- Battery sense: 100k/100k + 100nF to PA0.
- Leak: 3.3V -> 100k -> pad -> water -> GND -> PA1.
- Reed switch + magnet on the P-MOS gate; 100k pull-up; 100nF gate-source.
- Fuse or protected battery; check connector current.

## 5. Connectors and cable

| Ref | Type | Pinout |
|---|---|---|
| J1 | JST-PH 2P | 1S, GND |
| J2 | JST-SH 2P | main motor |
| J3 | JST-SH 2P | lateral motor |
| J4 | JST-SH 2P | vertical motor |
| J5 | JST-SH 3P | 5V, GND, jaw servo |
| J6 | JST-SH 3P | 5V, GND, camera video |
| J7 | JST-SH 6P | 1 +5V_BUOY, 2 GND_PWR, 3 CVBS_VIDEO, 4 GND_VIDEO, 5 PP_DOWN, 6 TELEM_UP |
| J8 | 4 pogo | 3V3, GND, SWDIO, SWCLK |
| J9 | JST-SH 2P | leak pad, GND |

Cable: 50 cm for shallow testing; longer version for 50 cm depth plus float/connector margin. Use a separate shielded video pair/coax, not only the overall shield.

- Camera video J6 -> J7 pin 3/4; 75 ohm system; check VTX input termination.
- Buoy `pp` J7 pin 5 -> G030 PA3.
- G030 telemetry J7 pin 6 -> buoy F407 RX (optional).
- 5V/GND J7 pins 1/2 -> buoy VTX/receiver/camera.

## 6. Firmware and safety

- `pp` parser: 115200 8N1, validate header, field count, ranges; reject malformed frames.
- Mixing: ch0 lateral/yaw, ch1 main/throttle, ch2 vertical, ch3 jaw.
- 500ms no valid `pp` -> motors 0, jaw open, LED blink.
- Reset/boot: all MX113H IN1=IN2=0; no motor motion before valid frames.
- IWDG 1s; low voltage (<3.4V) or leak -> safe state.
- Jaw 0-45 deg; bite macro; spring-open on power loss.
- Positive buoyancy: shark surfaces on power/control loss.
- Do not stub LimeCam tasks blindly; see `buoy_rf_board.md`.

## 7. Board size and layout

- First pass: **26x40-46mm**; target 20x30mm only after layout feasibility.
- 4-layer, 1.6mm; 4x M1.6 holes.
- MX113H x3 near J2-J4; 1.5mm motor, 0.8mm 5V, 0.4mm 3.3V.
- Camera video shielded/short; keep away from motor PWM; ground guard.
- UART series 22-100 ohm + TVS optional; cable shield to GND at one end.
- Boost/LDO away from video; input/output caps close.
- Fits a 35-40mm ID hull; 10-15cm shark.

## 8. Test

1. 3.3V/5V rails, current limit; check protection.
2. PP from USB-UART: valid and malformed frames; H-bridges stay off at reset.
3. Each MX113H: forward/reverse/stop; running/stall current; heat at 1A.
4. Failsafe: stop PP; motors stop; jaw open.
5. Camera video J6->J7 to buoy VTX; 75 ohm/termination check.
6. Full 50cm cable + buoy tank test; positive buoyancy check.
