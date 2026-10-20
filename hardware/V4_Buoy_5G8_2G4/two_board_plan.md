# V4 buoy: two-board redesign plan

Final V1 selection: **F407 stripped buoy board + G030 brushed control board**.
No 4-in-1 brushless ESC in V1. Device values and board sizes are not frozen.

## 1. Boards

| Board | Based on | Role | First-pass size |
|---|---|---|---|
| Shark control board | `driver` G030 | `pp` + 3x MX113H + jaw + 5V + camera/buoy connectors | 26x40-46 mm |
| Buoy RF board | `LimeCam` F407 | 2.4G LimeRC + `pp` + 5.8G video pass-through | 30x30-30x35 mm |
| Buoy carrier | custom | VTX, camera video, antennas, cable, float | 55x70 mm |

Target 20x30 (G030) and 30x30 (F407) only after layout feasibility.

## 2. Shark control board

Use `control_board.md`.

- G030K8T6; 3x MX113H; 1 jaw servo; protected 1S; MT3608 5V candidate (thermal fail at 0.72A/1A); TLV70033 3.3V/200mA; battery/leak; UART2 `pp`.
- Camera CVBS J6 -> J7 pass-through; no MCU video.
- H-bridges off at reset; PP frame validation; watchdog; low voltage/leak; positive buoyancy.
- Measure thruster running/start/stall current before layout; MX113H 1A continuous / 1.5A peak.

## 3. Buoy RF board

Use `buoy_rf_board.md`.

- F407VET6 + NRF2 + USART1 `pp`; video pass-through.
- **Source gate:** LimeRC receiver source/license, RF module, pairing, clock, PP polarity.
- If only HEX: use the original LimeCam board, or obtain source/permission; do not assume a new F407 board runs the HEX.
- Clock conflict: V3 JLCEDA project 24MHz vs original LimeCam 25MHz; resolve before layout.
- Remove OV2640/DCMI/NRF1/video/USB/CAN/SD/OLED only after the control link is proven.
- PP is normal 3.3V TTL; do not inherit the inverted-PP circuit.
- 5.8G VTX can be a separate module; 75 ohm video; check VTX termination.

## 4. Cable

50 cm for shallow testing; longer version for 50 cm depth plus float/connector margin.

| Pin | Net | Direction |
|---|---|---|
| 1 | +5V (cable label +5V_BUOY) | shark -> buoy |
| 2 | GND_PWR | power return |
| 3 | CVBS_VIDEO | shark -> buoy |
| 4 | GND_VIDEO | video return |
| 5 | PP_DOWN | F407 TX -> G030 RX |
| 6 | TELEM_UP | G030 TX -> F407 RX |

Use a separate shielded video pair/coax; not only the overall shield. 100uF at buoy input. J7 is proposed **JST-PH 6P** (2A at 24AWG); JST-SH is incompatible with 24AWG and must not be used.

## 5. Power

- Protected 1S -> Q1 SiSS23DN -> `VMOTOR` -> 3x MX113H.
- Protected 1S -> MT3608 5V candidate -> camera/buoy/servo -> TLV70033 3.3V/200mA -> G030.
- Do not use a 1S-to-3.3V LDO; do not stack a second boost without checking the LimeMini original.
- **MT3608 is thermally rejected for 0.72A/1A at 3.0V**; see `power_budget.md`. Replace/split/reduce before layout.
- +5V load ~0.72A nominal; +5V/1A at 3.0V/85% is ~1.96A input, plus motor peaks; L1 is SRP6060FA-220M (5.6A Isat, 3.8A Irms).
- Q1 SiSS23DN-T1-GE3: 6.3mohm max at VGS=-2.5V; ~4.96A continuous / ~6.46A peak budget.
- C1-C3: 100uF 6.3V polymer 1206; do not use unmeasured 100uF/0805 X5R.
- Check DW01A/FS8205A or chosen protection continuous/peak; check battery 30C and connector.
- +5V drop over 50cm/24AWG: ~0.08V at 1A, ~0.17V at 2A loop; verify at full load and servo stall. Cable OD is ~5.0-5.5mm.

## 6. Firmware

Shark:
- G030 `pp` parser + 3 motors + jaw + 500ms failsafe + battery/leak.
- 6 PWM, 20kHz; H-bridges off at boot; validate frames.

Buoy:
- Only with source: keep `nrfMessage`/`Lime_nrf_slave`/`agreement_pp`/USART1/SPI2; remove camera/video tasks after proving control.
- Only with HEX: use the original LimeCam board as-is; do not stub blindly.
- The remote must enable `pp` output; normal TTL.

Remote:
- Original LimeRC 2.4G remote; video on a separate 5.8G monitor.

## 7. Cost and size

| Item | Approx |
|---|---|
| Shark board (G030 + 3 MX113H + 5V) | 80-150 RMB |
| Buoy F407 board (F407 + NRF2 + 5V) | 80-150 RMB |
| 5.8G VTX/RX/camera/antennas | 150-350 RMB |
| Buoy shell/cable/connectors | 30-60 RMB |
| PCB fabrication (2 boards) | 50-100 RMB |
| **Total** | **~400-800 RMB** |

Shark 10-15 cm; buoy 55x70 mm, 50-80 g; cable 50 cm.

## 8. Alternative: G030 buoy board

- G030K8T6 + nRF24L01+ + 3.3V LDO + `pp` UART; 20x30 mm.
- Requires porting `Lime_nrf_slave`/`Lime_nrf_slave_ports` and the pairing protocol.
- Smaller/cheaper, but it does **not** solve the source/license issue.

## 9. Order of work

1. Resolve LimeRC source/license/clock/pin/PP polarity.
2. Measure thruster current/thrust and MX113H thermal.
3. Finish the G030 schematic with the final power tree and cable pinout.
4. Only then finish the F407 schematic, after firmware/hardware correspondence is proven.
5. Layout first, then freeze board sizes.
