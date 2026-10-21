# LimeMiniDriver / LimeRC reference audit

Date: 2026-10-21. Baseline: `62098cf`.

Status: **REFERENCE EVIDENCE PARTIAL. The LimeRC hardware schematic was obtained; the LimeMiniDriver schematic/BOM was not.**

## Sources actually inspected

- `https://oshwhub.com/phantom001/limeminidriver` - public project description, BOM and "hardware.rar" attachment available but the archive was not downloaded/verified.
- `https://oshwhub.com/phantom001/limerc3-1_release` - public project description and protocol/voltage notes.
- `https://github.com/pingyun001/LimeRC` - cloned to a temporary directory at commit `a9beb01` ("add user guide book pdf").
- `HARDWARE/SCH_CamReceiver.pdf` - 4-page schematic, V3.1, 2025-10-30.
- `SOFTWARE/LimeCam_Release/Agreement/agreement_pp.c`, `agreement_hal.c`, `App/nrfMessage.c`, `LimeNrfLib/Lime_nrf_slave.c`.
- `LICENSE` in the repository root.

## Findings

### LimeMiniDriver

| Item | Status | Evidence / limit |
|---|---|---|
| 3 motor channels, 3 servo channels, 1 LED | **VERIFIED (description only)** | OSHWHub description; no schematic/BOM copy obtained |
| Integrated 1S charger and boost | **VERIFIED (description only)** | OSHWHub description; actual circuit not inspected |
| PP decoding and TTL inversion on the original board | **INFERRED** | OSHWHub text says TTL level inversion and PP decode; exact XOR circuit not available |
| MCU / exact motor driver / pinout | **BLOCKED** | `hardware.rar` was not downloaded or opened; no pin-level claim is made |
| Original servo output count | **VERIFIED (description only)** | 3 servo channels described; Shark uses one |
| Original board is a direct Shark schematic donor | **UNVERIFIED** | Do not copy pin/net claims without the actual schematic |

The original board is useful as a functional reference (3 motors, servo, PP input, charger/boost, inversion), but it is not evidence for any Shark pin assignment.

### LimeRC receiver

| Item | Status | Evidence |
|---|---|---|
| MCU family/package | **INFERRED** | 100-pin STM32F4-class pin names and F4 LimeCamV3 firmware name; exact order code not read from BOM |
| HSE clock | **VERIFIED** | `SCH_CamReceiver.pdf` page 1: X1 = 25 MHz, 12 pF |
| RF modules | **VERIFIED** | Two `AS01-ML01S` nRF24L01+ modules, page 3 |
| Camera/video path | **VERIFIED** | OV2640 DCMI camera, 24 MHz MCO, 2.8 V/1.3 V LDOs; **no CVBS output** |
| Receiver input power | **VERIFIED** | Mult-Bus VBUS and STM32/LDO 3.3 V rails; page 3 uses `VBUS` |
| PP physical output | **VERIFIED** | `UART1TX` -> 74LVC1G86 XOR -> GH1.25 Mult-Bus signal pin; `UART2RX` is the opposite-direction input |
| PP polarity control | **VERIFIED** | `NOT_CTRL` drives XOR B; `AgreementOut_ChangeCodecTo()` sets it; `agreement_hal.c` |
| PP default at receiver boot | **VERIFIED** | `nrfMessage.c`: `ChangeCodecTo(PP, true, false)` -> inverted, output disabled until settings enable it |
| PP UART format | **VERIFIED** | 115200-8-N-1; `pp<ch0>,<ch1>,<ch2>,<ch3>,<left>,<right>,\r\n`; `agreement_pp.c` |
| PP loss behavior | **VERIFIED** | After >100 ms without a packet, one neutral frame (all channels 2048), then `isOffline = true`; `agreement_hal.c` |
| Mult-Bus connector | **VERIFIED** | 6-pin GH1.25; VBUS/GND plus UART1TX and UART2RX; exact pin numbers need a physical continuity check |
| LimeRC video is CVBS | **FALSE** | Camera is OV2640/DCMI; video is digital over the nRF24 link |
| LimeRC can feed Shark CVBS directly | **BLOCKED** | The receiver has no CVBS output; Shark's J6/J7 CVBS is an independent camera/VTX chain |

## Consequence for Shark V4

1. **PP polarity is a configuration gate.** The receiver can output normal or inverted TTL, but the boot default is inverted and output-disabled. The Shark/F407 chain must explicitly select normal output (or provide an inverter) and prove it by UART capture. Do not assume a normal-TTL receiver out of the box.
2. **The 5V receiver/VTX load is real and must be measured.** LimeRC uses a 5V VBUS input; the nRF24 modules and camera are not 5V-tolerant. The buoy must provide a clean 5V rail and local decoupling.
3. **The RF module is AS01-ML01S**, not E01C-ML01S. The F407 buoy design must be checked against the actual AS01 pinout/antenna and the LimeRC firmware; do not claim E01C compatibility.
4. **The video chain is independent.** LimeRC's OV2640 digital video cannot be treated as Shark's CVBS camera. A separate CVBS camera + 5.8 GHz VTX is allowed, but its 75 ohm termination, coax, and VTX input must be tested; this is not LimeRC video compatibility.
5. **The 25 MHz HSE is confirmed on the receiver schematic.** This does not prove the exact F407 firmware build, but it confirms the 25 MHz clock requirement is real.
6. **License conflict requires legal review.** Repository `LICENSE` is GPL-3.0; the OSHWHub hardware page says CC BY-SA 4.0 and also contains a commercial-use restriction sentence. Hardware/software reuse terms are not clean enough to call commercial-ready. Treat as **BLOCKED for commercial use** until the author clarifies.

## What must not be claimed

- No LimeMini pin-level schematic claim: the hardware archive was not opened.
- No PP polarity guarantee: receiver boot state is inverted/disabled.
- No CVBS compatibility with LimeRC: the receiver has no CVBS output.
- No E01C/AS01 equivalence: not verified.
- No final F407 build/RF/pairing compatibility.
