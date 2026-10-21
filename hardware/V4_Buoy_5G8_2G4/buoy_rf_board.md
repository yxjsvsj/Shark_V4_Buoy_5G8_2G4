# V4 buoy RF board (stripped LimeCam)

Role: receive the LimeRC 2.4G remote, output `pp` at 115200, and pass camera CVBS to the 5.8G VTX. No camera processing on this board.

## 0. Firmware gate first

Do not freeze this board until the LimeRC receiver source/license is resolved.

- LimeRC hardware is CC BY-SA 4.0; source copyright is separate. The public HEX may be personal/non-commercial only.
- Confirm:
  - compilable receiver source;
  - exact RF module/chip and pin map;
  - pairing/flash storage;
  - HSE/PLL clock;
  - NRF2/SPI2 and USART1 `pp`;
  - PP polarity (normal 3.3V TTL vs inverted).
- If only HEX is available:
  - do not assume a new F407 board will run it;
  - do not assume `nrfPhotoTask_Suspend()` can be stubbed;
  - use the original LimeCam board as the buoy receiver, or obtain source/permission.
- The G030+nRF24 alternative does not avoid this: it still needs a LimeRC-compatible protocol.

## 1. Keep / remove (only after source is available)

| Keep | Remove |
|---|---|
| F407VET6 minimum system | OV2640, DCMI, SCCB, JPEG |
| NRF2 + SPI2 | NRF1 video + SPI1 video path |
| USART1 `pp` output | `nrfPhoto`, `nrfVideo`, video tasks |
| `nrfMessage`, `Lime_nrf_slave`, `agreement_pp` | USB, CAN, SD, OLED, WS2812 |
| 3.3V/5V, SWD, flash/pairing | RNG, ADC, audio, camera PWDN |

Do not delete `nrfMessage`/`Lime_nrf_slave`/`agreement_pp`/USART1/SPI2 until the control link is proven.

## 2. F407 minimum system and clock

- F407VET6 LQFP100; 3.3V; VCAP_1/2 2.2uF; BOOT0 10k to GND; NRST 100nF.
- **Clock conflict to resolve:** the V3 JLCEDA project uses 24MHz HSE; the original LimeCam code uses 25MHz (PLL M=25/N=336/P=2/Q=7).
- The new board must match the final firmware's HSE/PLL. Do not copy the V3 24MHz clock into a board that runs the original 25MHz HEX, or vice versa.
- Pin details: use the V3 project `02_STM32` page as the reference; verify every pin in JLCEDA.

## 3. NRF2 and `pp`

- NRF2 SPI2: PB13 SCK, PB14 MISO, PB15 MOSI.
- CE PD10, CSN PD11, IRQ PD12, EN PD14.
- USART1 `pp`: PA9 TX, PA10 RX; 115200 8N1.
- 2.4G 31mm antenna; vertical; IPEX.
- Keep the LimeCam pairing/`Lime_GlobalData`; the remote pairs as before.
- PP is normal 3.3V TTL in the new design; do not inherit the LimeMini inverted-PP circuit. Confirm the receiver firmware setting.
- The remote must enable `pp` output mode.

## 4. 5.8G video pass-through

The F407 does not process video.

- J_CAM: 5V, GND, VIDEO from the 1 m (0.8-1.2 m) cable.
- J_VTX: 5V, GND, VIDEO to the 5.8G VTX.
- Route with a short shielded trace/coax and a ground guard.
- CVBS is a 75 ohm system; check whether the VTX input already has 75 ohm termination to avoid double termination.
- 5.8G VTX 25mW; cloverleaf; VTX can be a separate module, not integrated on the F407 board.

## 5. Power

- 5V from the 1 m (0.8-1.2 m) cable -> TLV70033 3.3V/200mA -> F407 + NRF2. No V3 1S protection/TPS63802 and no buoy battery; no reverse feed.
- 5V -> 5.8G VTX + camera.
- Current: F407 0.1A + NRF2 0.03A + VTX 0.2A + camera 0.1A = ~0.43A.
- 100uF at input; 3.3V LDO TLV70033 200mA (F407+NRF2 ~0.13A); F407 decoupling as usual.
- Check the +5V drop over 1 m and the buoy connector.
- The buoy cable connector must mate with the G030 **JST-PH 6P** (2A at 24AWG); do not use JST-SH for 24AWG power/GND.

## 6. Size and layout

- Target 30x30mm; allow 30x35mm if placement/thermal needs it.
- 4-layer preferred; F407 LQFP100 in the center; NRF2 at one edge with a 2.4G keepout.
- VTX can be a separate module; keep 2.4G and 5.8G antennas >=5cm apart.
- 4x M1.6 holes; fits the 55x70mm buoy.
- Do not freeze the outline before placement.

## 7. Firmware plan

- Only with source:
  - start from `LimeCam_Release`;
  - keep `nrfMessage`, `Lime_nrf_slave`, `Lime_nrf_slave_ports`, `agreement_pp`, USART1, SPI2;
  - remove camera/video tasks only after proving NRF2/SPI2/USART1/pairing independently;
  - test `pp` with the G030 before adding buoy mechanics.
- Only with HEX:
  - use the original LimeCam board as-is (camera can remain connected but unused);
  - do not build a new F407 board around the HEX unless the hardware/clock match is proven.

## 8. Current status and firmware dependencies

Status: **BLOCKED / minimum-system and interface draft only. RF nets are not frozen. No JLCEDA ERC.**

| Dependency | Status | Evidence / action |
|---|---|---|
| Legally usable, compilable LimeRC receiver source | BLOCKED | Need author/source/license confirmation |
| Exact RF module/chip (NRF2) | BLOCKED | Do not assume E01C-ML01S is compatible |
| CE/CSN/IRQ/EN pins and SPI2 | BLOCKED | Verify against the real LimeCam receiver schematic |
| USART1 `pp` at 115200 | TBD | Verify pins/baud |
| Pairing/flash storage | BLOCKED | Need source and hardware match |
| HSE 24MHz vs 25MHz and PLL | BLOCKED | Must match final firmware |
| PP normal vs inverted 3.3V TTL | BLOCKED | Measure/verify; new design uses normal TTL |
| NRF1/video task removal | BLOCKED | Do not remove until control link is proven |
| Camera task removal / `nrfPhotoTask_Suspend` | BLOCKED | Do not stub blindly; task dependencies unknown |
| 5.8G VTX 75 ohm termination | TBD | Check VTX datasheet/input |
| V3 1S protection/boost removal | FIXED in docs | Buoy is 5V cable -> 3.3V LDO; no V3 battery/boost |

## 9. G030 alternative

- G030K8T6 + nRF24L01+ + 3.3V LDO + `pp` UART; 20x30mm.
- Requires porting `Lime_nrf_slave`/`Lime_nrf_slave_ports` and the pairing protocol.
- Smaller/cheaper, but it does not solve the source/license issue.
