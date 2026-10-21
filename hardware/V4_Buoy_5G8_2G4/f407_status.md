# F407 buoy board status and firmware dependencies

Status: **BLOCKED / minimum-system and interface draft only. RF nets are not frozen. No JLCEDA ERC.**

## Confirmed only at document level

- F407VET6 LQFP100 minimum system (from the V3 project) exists as a starting point.
- NRF2 candidate pins from the original LimeCam project: SPI2 PB13/PB14/PB15; CE PD10, CSN PD11, IRQ PD12, EN PD14.
- USART1 `pp` candidate: PA9/PA10, 115200.
- 5.8G VTX and camera video are external; the F407 only passes CVBS.

These are **candidates**, not verified against the actual LimeCam receiver hardware.

The upstream source is now **available**, not “completely missing”: `pingyun001/LimeRC` is public with a GPL-3.0 LICENSE, and the source tree contains the 100ms timeout/one-neutral-frame logic in `agreement_hal.c`. This does **not** prove that the final production receiver build compiles, that the RF module/pins match, that the clock is 24 or 25MHz, that PP polarity is normal, or that a new F407 board can run it. The final firmware link-loss behavior still needs a real UART capture. F407 remains BLOCKED for layout.

## Firmware dependencies

| Dependency | Status | Action |
|---|---|---|
| Upstream LimeRC source available | **AVAILABLE** | `pingyun001/LimeRC`, commit `a9beb0102be529bc43736acc8ca2f508560c46d6`, GPL-3.0 LICENSE |
| Final production version compiles | TBD | Build the exact version and record compiler/toolchain; public source does not prove buildability |
| Third-party source/license dependencies | TBD | Inventory each dependency; GPL-3.0 source availability is not a full license review |
| Exact RF module/chip (NRF2) | BLOCKED | Verify AS01/E01C/LimeCam actual part |
| CE/CSN/IRQ/EN and SPI2 pins | BLOCKED | Verify against real LimeCam schematic |
| USART1 `pp` pins/baud | TBD | Verify |
| Pairing/flash storage | BLOCKED | Source + hardware match |
| HSE 24MHz vs 25MHz and PLL | BLOCKED | Match final firmware; V3 project is 24MHz, original code 25MHz |
| PP normal vs inverted 3.3V TTL | BLOCKED | Measure/verify; new design uses normal TTL |
| Final firmware link-loss behavior | TBD | UART capture on the exact receiver build; source review is not hardware proof |
| NRF1/video task removal | BLOCKED | Prove control link before removing |
| Camera task / `nrfPhotoTask_Suspend` | BLOCKED | Do not stub blindly; dependencies unknown |
| 5.8G VTX 75 ohm termination | TBD | Check VTX input |
| V3 1S protection/boost removal | FIXED in docs | Buoy uses cable 5V -> TLV70033 3.3V/200mA; no V3 battery/boost |

## What is not done

- No F407 schematic beyond the V3 copy.
- No RF net freeze.
- No JLCEDA ERC/DRC.
- No firmware compile or pairing test.
- No claim that E01C-ML01S is LimeCam-compatible.

## Next actions

1. Obtain source/permission or use an original LimeCam board.
2. Verify RF chip, pins, clock, PP polarity and pairing on the real hardware.
3. Then freeze NRF2/SPI2/USART1 and the 5V/3.3V power section.
4. Run JLCEDA ERC and record all warnings.
