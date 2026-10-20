# V4 sub control board

The buoy carries all RF. This board only does: `pp` parsing, 3 motor drivers, jaw servo, power, camera/buoy wiring, battery/leak safety. No RF, no camera interface, no DCMI.

## 0. Fastest path: reuse the existing G030 driver board

The `driver/` board already has 3 motor channels + 3 servo channels + UART2 `pp`.
For the first buoy prototype, you do not need a new PCB:

- Buoy LimeCam `pp` -> driver UART2 (115200).
- 3 thrusters -> MOTOR A/B/C.
- Jaw servo -> servo A.
- Add a 5V boost module for the camera + buoy.
- Camera video goes directly to the buoy cable; it does not need the driver board.
- Check the existing H-bridge current rating; if it is too small for the thrusters, use the custom MX113H board below.

This gets the buoy + shark in the tank fastest. Design the custom 20x30 board only after the mechanics and links pass.

## 1. Block diagram

```
1S LiPo -> P-MOS -> 5V boost 2A -> 5V (camera, buoy, servo)
                   |-> 3.3V LDO -> G030
                   |-> 3x MX113H motor power (1S)

Buoy 2.4G receiver --pp 115200--> UART2 -> G030
Camera CVBS ------------------------------> buoy video pin (pass-through)
G030 -> 6 PWM -> 3x MX113H -> 3 thrusters
G030 -> 1 PWM -> jaw servo
G030 <- ADC battery, GPIO leak, LED
```

## 2. MCU and pin map

**MCU: STM32G030K8T6, LQFP32, 64KB flash, 8KB RAM.** Enough for `pp`, 6 PWM, servo, ADC, UART, failsafe. No RF.

| Function | Pin | Peripheral |
|---|---|---|
| Main motor IN1 | PA8 | TIM1_CH1 |
| Main motor IN2 | PA9 | TIM1_CH2 |
| Lateral motor IN1 | PA10 | TIM1_CH3 |
| Lateral motor IN2 | PA11 | TIM1_CH4 |
| Vertical motor IN1 | PA6 | TIM3_CH1 |
| Vertical motor IN2 | PA7 | TIM3_CH2 |
| Jaw servo | PB0 | TIM3_CH3, 50Hz |
| Buoy UART RX | PA3 | USART2_RX, 115200 |
| Buoy UART TX | PA2 | USART2_TX, optional |
| Battery sense | PA0 | ADC_IN0 |
| Leak sense | PA1 | GPIO input |
| Status LED | PB1 | GPIO |
| SWDIO/SWCLK | PA13/PA14 | SWD |
| Spare | PA4/PA5/PA12/PB2-PB7 | Keep pads |

All motor PWM: 20kHz, 0-100% duty. Servo: 50Hz, 500-2500us.

## 3. Motor drivers

- 3x **MX113H**, SOT-23-6, 1 H-bridge each.
- VCC 1S (2-8V), 1A continuous / 1.5A peak, Rds(on) 0.4Ω, thermal shutdown.
- Each motor uses IN1/IN2:
  - forward: IN1=PWM, IN2=0
  - reverse: IN1=0, IN2=PWM
  - stop: IN1=0, IN2=0
  - brake: IN1=1, IN2=1
- 6 PWM outputs; 20kHz; avoid audible noise.
- Add 100uF + 100nF at each MX113H VCC; keep motor connectors close.
- 1A limit: use small 6-8mm brushed motors; check stall current; add copper/thermal.
- If using brushless later: remove MX113H, use 1S 4-in-1 ESC; 3 PWM + 6-pin ESC connector.

## 4. Power

- 1S 450mAh 30C -> P-MOS 5A+ (AON7403/AO3401) -> 5V boost 2A -> 5V.
- 5V -> TLV70033 3.3V/300mA -> G030.
- 1S -> MX113H VCC.
- 5V -> camera, buoy VTX/receiver, jaw servo.
- 5V current: camera 0.1A + buoy 0.4A + servo 0.2A + LDO 0.05A = 0.75A; 2A boost.
- Battery sense: 100k/100k + 100nF to PA0.
- Leak: 3.3V -> 100k -> pad -> water -> GND -> PA1.
- Reed switch + magnet on the P-MOS gate; 100k pull-up; 100nF gate-source.

## 5. Connectors

| Ref | Type | Pinout |
|---|---|---|
| J1 | JST-PH 2P | 1S, GND |
| J2 | JST-SH 2P | main motor |
| J3 | JST-SH 2P | lateral motor |
| J4 | JST-SH 2P | vertical motor |
| J5 | JST-SH 3P | 5V, GND, servo |
| J6 | JST-SH 3P | 5V, GND, camera video |
| J7 | JST-SH 6P | 5V, GND, VIDEO, UART_TX, UART_RX, spare |
| J8 | 4 pogo | 3V3, GND, SWDIO, SWCLK |
| J9 | JST-SH 2P | leak pad, GND |

- Camera video (J6) passes through to J7 VIDEO; the camera 5V/GND also to J7.
- J7 cable to buoy: 50cm, 6-core shielded.
- UART from buoy: LimeCam `pp` output -> J7 UART_TX -> G030 PA3.
- The camera video is not connected to the MCU; it only goes to the buoy VTX.

## 6. Buoy carrier (separate)

- 5.8G 25mW VTX + cloverleaf.
- LimeCam board as 2.4G receiver; camera disabled; `pp` output.
- 5V filter/100uF; 2.4G 31mm antenna; 5.8G antenna.
- Cable J7; buoy shell; no MCU (LimeCam has the F407).
- First version can be a 30x40 perfboard; no custom PCB needed.

## 7. Firmware

- `pp` parser: 115200 8N1, `pp<ch0>,<ch1>,<ch2>,<ch3>,<keyL>,<keyR>,`.
- Mixing: ch0 lateral/yaw, ch1 main/throttle, ch2 vertical, ch3 jaw.
- Failsafe: no valid `pp` > 500ms -> all motors 0, jaw open, LED blink.
- Battery < 3.4V or leak -> same failsafe.
- IWDG 1s; ESC/MX113H outputs 0 at boot.
- Jaw: 0-45 deg; bite macro on key.
- The buoy LimeCam must enable `pp` output at 115200; its camera can be disabled.

## 8. Board and layout

- 20x30mm, 4-layer, 1.6mm; 4x M1.6 holes.
- MX113H x3 near J2-J4; 1S/5V traces wide; 1.5mm motor, 0.8mm 5V, 0.4mm 3.3V.
- Camera video trace shielded/short; keep away from motor PWM; ground guard.
- UART series resistor 22-100R + TVS optional; cable shield to GND at one end.
- Boost/LDO away from camera video; input/output caps close.
- The board fits a 35-40mm ID hull; 10-15cm shark.

## 9. Test

1. 3.3V/5V rails; current limit.
2. `pp` from a USB-UART: `pp2048,2048,2048,2048,3,3,` at 10-20Hz; motors/servo respond.
3. Each MX113H: forward/reverse/stop; current; heat at 1A.
4. Failsafe: stop `pp`; motors stop; jaw open.
5. Camera video through J6->J7 to the buoy VTX.
6. Full buoy cable + tank test.
