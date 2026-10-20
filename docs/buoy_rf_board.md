# V4 buoy RF board (stripped LimeCam)

Role: receive the LimeRC 2.4G remote, output `pp` at 115200, and carry the 5.8G VTX/video. No camera processing on this board.

## 1. What to keep from LimeCam

| Keep | Remove |
|---|---|
| F407VET6 minimum system | OV2640, DCMI, SCCB, JPEG |
| NRF2 + SPI2 | NRF1 video + SPI1 video path |
| USART1 `pp` output | `nrfPhoto`, `nrfVideo`, video tasks |
| `nrfMessage`, `Lime_nrf_slave`, `agreement_pp` | USB, CAN, SD, OLED, WS2812 |
| 3.3V/5V, SWD, HSE, flash/pairing | RNG, ADC, audio, camera PWDN |

## 2. F407 minimum system

- F407VET6 LQFP100; HSE 25MHz; PLL M=25/N=336/P=2/Q=7 -> 168MHz.
- VDD 11/19/28/50/75/100 -> 3V3; VSS 10/27/74/99 -> GND; VDDA 22/VREF+ 21 -> 3V3_A; VSSA 20 -> GND; VBAT 6 -> 3V3.
- VCAP_1 49, VCAP_2 73: 2.2uF each to GND.
- BOOT0 94: 10k to GND; NRST 14: 100nF to GND; SWD PA13/PA14.
- Full details in `../V3_SingleMCU_2G4/min_system.csv` and `pinout.csv`.

## 3. NRF2 and `pp`

- NRF2 SPI2: PB13 SCK, PB14 MISO, PB15 MOSI.
- CE PD10, CSN PD11, IRQ PD12, EN PD14.
- USART1 `pp`: PA9 TX, PA10 RX; 115200 8N1.
- 2.4G antenna: 31mm wire from the NRF24 IPEX; vertical.
- Keep the LimeCam pairing/`Lime_GlobalData`; the remote pairs as before.
- The LimeCam `nrfMessage` starts the slave and `AgreementOut_ChangeCodecTo(PP)`; keep.
- The remote must enable `pp` output mode; the LimeCam default may be disabled.

## 4. 5.8G video pass-through

The F407 does not process video. On the buoy board provide:

- J_CAM: 5V, GND, VIDEO (from the 50cm cable/camera).
- J_VTX: 5V, GND, VIDEO (to the 5.8G VTX).
- Route VIDEO from J_CAM to J_VTX with a short shielded trace/coax; add a ground guard.
- 5V from the cable -> VTX and camera; 100uF + 100nF; LC/ferrite.
- 5.8G VTX 25mW; cloverleaf; 5.8G receiver at tank edge.

## 5. Power

- 5V from the 50cm cable -> 3.3V LDO -> F407 + NRF2.
- 5V -> 5.8G VTX + camera.
- Current: F407 0.1A + NRF2 0.03A + VTX 0.2A + camera 0.1A = ~0.43A.
- 100uF at input; 3.3V LDO 300mA; F407 decoupling as usual.

## 6. Size and layout

- 30x30mm, 4-layer preferred (or 2-layer with solid GND).
- F407 LQFP100 in the center; NRF2 at one edge with a 2.4G keepout; 5.8G video headers on the other side.
- Keep the 2.4G antenna away from the 5.8G VTX/antenna (>=5cm).
- 5V/3.3V traces 0.6/0.4mm; video shielded.
- 4x M1.6 holes; fits the 55x70mm buoy.

## 7. Firmware

- Start from `LimeCam_Release`; remove camera/video/USB/CAN/SD/OLED tasks.
- Keep `nrfMessage`, `LimeNrfLib/Lime_nrf_slave.c`, `Lime_nrf_slave_ports.c`, `agreement_pp.c`, USART1, SPI2.
- Provide a stub for `nrfPhotoTask_Suspend()`; keep `Lime_GlobalData`/flash or a RAM stub.
- Output `pp` at 115200; the sub G030 parses it.
- Test pairing and `pp` before adding the buoy mechanics.

## 8. G030 alternative

- G030K8T6 + nRF24L01+ + 3.3V LDO + `pp` UART; 20x30mm.
- Port `Lime_nrf_slave`/`Lime_nrf_slave_ports` to G030; keep pairing.
- Smaller/cheaper, but more firmware work than the stripped F407.
