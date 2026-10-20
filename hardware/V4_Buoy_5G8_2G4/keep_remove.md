# What to keep / remove from the open-source boards

For the buoy architecture, the shark side has no RF and the buoy side does not need the camera/video/NRF1 parts. You can remove a lot, but keep the power, SWD, pairing and `pp` path.

## 1. Sub side: existing G030 driver board

| Keep | Remove | Add |
|---|---|---|
| G030 + 3.3V LDO | 2 unused servo channels/connectors | MT3608 5V candidate (thermal fail at 0.72A/1A) |
| UART2 `pp` input | Extra headers/test points/LEDs | Camera 5V/GND/VIDEO connector |
| 3 motor H-bridges | Unused ADC/keys if not wired | Buoy 6-pin connector |
| 1 servo channel (jaw) | 2 servo connectors | LC/ferrite on camera/buoy 5V |
| SWD, battery ADC, leak, LED | | |

- Keep all 3 motor channels: 3 thrusters.
- Keep one servo: jaw; remove the other two connectors.
- Add a 5V boost for camera + buoy VTX/receiver + servo.
- Check the existing H-bridge current; if too small, keep the G030/PWM and use 3x MX113H or a 1S 4-in-1 ESC.
- Do not remove the 3.3V LDO, SWD, UART2 or the 500ms failsafe.

## 2. Buoy side: LimeCam board

| Keep | Remove |
|---|---|
| F407, 3.3V/5V power | OV2640, DCMI, SCCB, JPEG |
| NRF2 (2.4G control) + SPI2 | NRF1 (video) + SPI1 video path |
| USART1 `pp` output | `nrfPhoto`, `nrfVideo`, video tasks |
| `Lime_nrf_slave`, `agreement_pp`, `nrfMessage` | USB, CAN, SD, OLED, WS2812 |
| Flash/global data, pairing | RNG, ADC, audio, `Lime_screen_show` |
| FreeRTOS (or bare loop) | Camera power/reset/PWDN |

- The buoy LimeCam only needs to receive the LimeRC remote and output `pp`.
- The camera is in the shark; the buoy gets CVBS over the cable and feeds a 5.8G VTX.
- The remote screen will not show video; use a separate 5.8G monitor.
- Provide stubs for `nrfPhotoTask_Suspend()` and camera init if the removed code still calls them.
- Keep `Lime_GlobalData`/flash or a RAM stub; keep the pairing logic.
- If the LimeCam board is too big, replace it with a small 2.4G receiver + MCU that outputs `pp`; but that needs protocol work.

## 3. Code dependencies to check

- `LimeCam_Release/Core/Src/main.c`: remove camera/DCMI/USB/CAN/SD/OLED init.
- `Core/Src/freertos.c`: remove `nrfPhoto` task; keep `nrfMessage`.
- `App/nrfMessage.c`: keep; it initializes the nRF slave and `pp`.
- `LimeNrfLib/Lime_nrf_slave.c`: on timeout calls `nrfPhotoTask_Suspend()`; provide a stub.
- `Agreement/agreement_pp.c`: keep; it outputs `pp`.
- `USART1` (`huart1`) is the `pp` output; keep.
- `SPI2`/NRF2: keep; NRF1 video can be removed.
- Test pairing and `pp` output after each removal; don't delete the whole `LimeNrfLib`.

## 4. What not to remove

- 3.3V/5V decoupling, SWD, BOOT0 option, NRST, HSE.
- UART2 on the sub; USART1 on the buoy.
- nRF24 NRF2 + antenna; LimeRC pairing.
- Failsafe/watchdog; battery/leak protection.
- Motor power/ground and the 5V boost input caps.

## 5. Fastest path

Use the existing G030 driver board + a 5V boost + a LimeCam stripped to a 2.4G `pp` receiver. Do not design a new PCB until the buoy and links pass.
