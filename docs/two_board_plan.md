# V4 buoy: two-board redesign plan

Since you do not have the original boards, build two new boards from the open-source designs, with unused modules removed.

## 1. Boards

| Board | Based on | Role | Size |
|---|---|---|---|
| Shark control board | `driver` G030 board | `pp` + 3 motors + jaw + 5V + camera/buoy connectors | 20x30 mm (or 46x26) |
| Buoy RF board | `LimeCam` F407 board | 2.4G LimeRC receiver + `pp` output + 5.8G VTX carrier | 30x30 mm |
| Buoy carrier | custom | VTX, camera video, antennas, cable, float | 55x70 mm |

The 5.8G VTX/camera are separate modules; the buoy RF board only handles 2.4G control and `pp`.

## 2. Shark control board

Use `control_board.md` in this folder.

- G030K8T6; 3x MX113H or 3 H-bridges; 1 jaw servo; 5V boost; battery/leak; UART2 `pp`.
- Keep 3 motor channels, 1 servo; remove 2 servo channels and unused headers.
- Camera video goes from J6 to J7 (buoy) as a pass-through; the MCU does not touch video.
- No RF on the sub.
- If the original H-bridge current is enough, use the original `driver` schematic; otherwise use 3x MX113H or a 1S 4-in-1 ESC.

## 3. Buoy RF board

Use `buoy_rf_board.md` in this folder.

- F407VET6 minimum system + NRF2 (2.4G control) + USART1 `pp`.
- Remove OV2640/DCMI/NRF1/video/USB/CAN/SD/OLED/WS2812.
- Add 5.8G VTX 5V/VIDEO header and camera video input; video is a pass-through, not processed.
- 2.4G 31 mm antenna; 5.8G antenna on the buoy.
- Reuse the LimeCam `nrfMessage`/`Lime_nrf_slave`/`agreement_pp` code.
- The original LimeRC remote works; the screen will not show video; use a 5.8G monitor.

## 4. Cable

- 50 cm, 6-core shielded: 5V, GND, VIDEO, UART_TX (buoy->sub), UART_RX (sub->buoy), spare.
- Camera video from the shark nose goes through the sub board J6 -> J7 -> buoy VTX.
- Buoy `pp` -> sub UART2 at 115200.
- 5V from the sub boost -> buoy RF board + VTX + camera.
- 100uF at buoy input; LC/ferrite for video.

## 5. Power

- Shark 1S 450mAh -> 5V boost 2A -> camera + buoy + servo.
- Buoy: 5V -> 3.3V LDO -> F407 + NRF2; 5V -> VTX/camera.
- Buoy current ~0.4A; shark 5V rail ~0.75A; 2A boost.
- 5V drop over 50cm: ~0.09V at 0.4A; fine.

## 6. Firmware

Shark:
- `driver` `app_main.c` / `motor.c` / `servo.c`; `pp` 115200; 3 motors; jaw; 500ms failsafe; battery/leak.
- If MX113H: 6 PWM, 20kHz; if original H-bridge: DIR+PWM.

Buoy:
- LimeCam `nrfMessage` + `Lime_nrf_slave` + `agreement_pp`; USART1 `pp`; NRF2.
- Remove camera/video tasks; stub `nrfPhotoTask_Suspend`; keep `Lime_GlobalData`/pairing.
- The remote must enable `pp` output at 115200.

Remote:
- Original LimeRC 2.4G remote; no changes; video on a separate 5.8G monitor.

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

If the buoy F407 board is too large or expensive, replace it with:
- G030K8T6 + nRF24L01+ + 3.3V LDO + `pp` UART; 20x30 mm.
- Port `Lime_nrf_slave`/`Lime_nrf_slave_ports` to G030; keep the LimeRC pairing.
- Smaller/cheaper, but more firmware work.

## 9. Next step

Choose:
1. Buoy RF: stripped F407 LimeCam (fastest, bigger) or G030 + nRF24 (smaller, more firmware).
2. Motor: 3x MX113H brushed or 1S 4-in-1 ESC brushless.
3. Sub board: original 46x26 driver layout or 20x30 custom.

After choosing, generate the schematic netlist and 20x30/30x30 board outlines.
