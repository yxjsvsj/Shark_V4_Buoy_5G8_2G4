# Shark_V4_Buoy_F407_RevA

New JLCEDA Pro project for the **buoy F407 receiver board**. It is a copy of `Shark_V3_SingleMCU_RevA`, used as a starting point. It is **not build-ready**.

## 1. What this board does

- Receives the LimeRC 2.4G remote on NRF2.
- Outputs `pp` at 115200 on USART1 to the shark over the 50 cm cable.
- Passes the shark camera CVBS video to the 5.8G VTX on the buoy.
- No camera processing, no NRF1 video, no motor drivers.

The shark control board (G030 + 3 thrusters + jaw) is a separate project. See:
`../V4_Buoy_5G8_2G4/control_board.md`.

## 2. Keep / remove from V3

| Keep | Remove |
|---|---|
| F407VET6 minimum system (HSE 24/25 MHz to confirm) | OV2640, DCMI, SCCB, JPEG |
| SWD, BOOT0, NRST, VCAP, decoupling | NRF1 / SPI1 video |
| NRF2 / SPI2 2.4G control | USB, CAN, SD, OLED, WS2812 |
| USART1 `pp` output | Camera 2.8 V / 1.3 V LDOs |
| 1S protection, TPS63802 3.3V | Camera PWDN / reset |
| Battery sense, 2.4G antenna | Motor/servo page (separate G030 board) |

Add:
- 5V input from the buoy cable.
- 5.8G VTX header: 5V / GND / VIDEO.
- Camera video header: 5V / GND / VIDEO (pass-through to VTX).
- 100uF + 100nF + LC/ferrite on the 5V/camera rail.
- 2.4G 31 mm antenna keepout; 5.8G antenna on the buoy.

## 3. Page changes

| Page | Action |
|---|---|
| `01_POWER` | Keep 1S protection + 3.3V; remove camera LDOs; add 5V cable input + VTX/camera 5V. |
| `02_STM32` | Keep F407 minimum; keep NRF2/SPI2 and USART1; remove NRF1/video; keep SWD. |
| `03_CAMERA_RF` | Remove OV2640/DCMI/SCCB/NRF1; keep NRF2; add camera/VTX video headers and 5.8G/2.4G antenna placement. |
| `04_MOTOR_SERVO` | Do not use on this board; the G030 sub board handles motors. |
| `05_SENSORS_DEBUG` | Optional; not needed for the buoy. |

## 4. Firmware

**Firmware source gate:** LimeRC hardware is CC BY-SA 4.0, but source copyright is separate. Confirm compilable source, RF module, pairing, clock and PP polarity before layout.

- With source: keep `App/nrfMessage.c`, `LimeNrfLib/Lime_nrf_slave.c`, `Lime_nrf_slave_ports.c`, `Agreement/agreement_pp.c`, USART1, SPI2; remove camera/video tasks only after proving NRF2/SPI2/USART1/pairing independently.
- With HEX only: use the original LimeCam board as-is; do not assume a new F407 board runs the HEX; do not stub `nrfPhotoTask_Suspend()` blindly.
- Output `pp` at 115200 on USART1; normal 3.3V TTL, not inverted.
- The LimeRC remote must enable `pp` output mode.
- The remote screen will not show video; use a separate 5.8G monitor.

## 5. Board target

- Target 30x30mm, allow 30x35mm; 4-layer preferred; F407 LQFP100 in the center; NRF2 at one edge with antenna keepout.
- 5.8G/camera headers on the opposite side; keep 2.4G and 5.8G antennas >=5 cm apart.
- 4x M1.6 holes; fits the 55x70mm buoy.
- The V3 board outline is only a reference; resize after placement.

## 6. Status

- This is a **copy of the V3 project**; the camera/RF wiring in V3 was incomplete.
- Do not fabricate as-is.
- First validate the buoy links (2.4G `pp`, 5.8G video, 50 cm cable) before finalizing this PCB.

## 7. Open

Use JLCEDA Pro V4.1.78 to open `Shark_V4_Buoy_F407_RevA.eprj3`.
Save As a new project before editing; the internal UUIDs came from V3.

The original V3 notes are kept in `V3_REFERENCE.md`. See `../V4_Buoy_5G8_2G4/design_review.md` for the P0 gates.
