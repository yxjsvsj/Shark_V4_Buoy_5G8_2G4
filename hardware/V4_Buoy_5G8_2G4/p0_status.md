# P0/P1 status after remediation

Branch: `p0-g030-remediation`. Base: `b143d9b`.
No PCB was ordered, no Gerber was generated, no production-ready claim is made.

## P0

| ID | Issue | Evidence | Status | Fix / remaining |
|---|---|---|---|---|
| P0-01 | TIM3 conflict: PA6/PA7 vertical PWM, PB1 jaw, PB0 LED | STM32G030x6/x8 datasheet Table 12/13: PA6 TIM3_CH1, PA7 TIM3_CH2, PB1 TIM14_CH1, PB0 GPIO/TIM3_CH3 | **FIXED in docs** | Pinout/control board updated; JLCEDA schematic still not drawn |
| P0-02 | PA14-BOOT0/SWCLK | Datasheet pin 25: PA14-BOOT0, SWCLK; internal pull-down; nBOOT_SEL option | **FIXED in docs** | No separate BOOT0 pin/resistor; SWD NRST; option bytes TBD |
| P0-03 | VDD/VDDA and VSS/VSSA merged on LQFP32 | Datasheet pins 4/5: VDD/VDDA, VSS/VSSA | **FIXED in docs** | Single 3V3/GND pins; no separate 3V3_A/VDDA net |
| P0-04 | 5V boost was "MT3608 or TPS61023" | BOM ambiguity | **FIXED in docs** | Chosen MT3608 5V/1A; L1 22uH, D1 SS34, R1 73.2k/R2 10k; thermal/inductor measurement TBD |
| P0-05 | TLV70033 current | TLV70033 200mA max, not 300mA | **FIXED in docs** | 3.3V load ~20mA; 200mA enough |
| P0-06 | P-MOS was AON7403/AO3401 | BOM ambiguity | **FIXED in docs** | Chosen AON7403 DFN3x3; source 1-3, gate 4, drain 5-8; verify footprint |
| P0-07 | Battery/J1/protection current | 3 motors + 5V peak; JST-PH 2A insufficient | **PARTIAL** | J1 changed to XT30; protected pack; actual motor/protection current still BLOCKED |
| P0-08 | J7 cable and video return | Previous pinout mixed power/video; GND_VIDEO could float | **PARTIAL** | Pinout fixed; 24AWG power; separate video shield; VTX 75 ohm termination TBD |
| P0-09 | Buoyancy | mechanical.md said negative/neutral | **FIXED in docs** | Shark slightly positive; power-loss surfacing still needs tank test |
| P0-10 | BOM duplicate refs/either-or | C1 Qty=3, MT3608 or TPS61023, AON7403/AO3401 | **FIXED in control BOM** | Unique refs; one selected part per function |
| P0-11 | LimeRC receiver source/license | Hardware CC BY-SA 4.0; source copyright separate; HEX personal/non-commercial | **BLOCKED** | Need source/permission or use original LimeCam board |
| P0-12 | F407 HSE 24 vs 25MHz | V3 project 24MHz; original LimeCam code 25MHz | **BLOCKED** | Must match final firmware before layout |
| P0-13 | PP normal vs inverted TTL | LimeMini default inverted; LimeCam supports normal/inverted | **BLOCKED** | New design uses normal TTL; verify firmware setting |
| P0-14 | JLCEDA board name/ERC | `.eprj3` name was overwritten by JLCEDA once; no GUI ERC | **BLOCKED** | Rename/save in JLCEDA UI; run ERC there |
| P0-15 | G030 schematic draft | Connection-level draft created | **DRAFT** | `g030_schematic_draft.md` + `g030_netlist_draft.csv`; no `.esch2`, no ERC |
| P0-16 | F407 RF/firmware correspondence | E01C-ML01S not proven LimeCam-compatible | **BLOCKED** | `buoy_rf_board.md` dependency table |

## P1

| ID | Issue | Status | Action |
|---|---|---|---|
| P1-01 | 5.8G VTX 75 ohm input termination | TBD | Check VTX datasheet/input; avoid double termination |
| P1-02 | Board fit/size | TBD | G030 26x40-46 first pass; F407 30x30-30x35; layout before freeze |
| P1-03 | MT3608 inductor saturation/thermal | TBD | 22uH >2.5A saturation; measure at 5V/1A and 3.0V input |
| P1-04 | J7/J1/cable current | TBD | XT30, 24AWG 5V/GND; measure 5V + motor peak |
| P1-05 | SWD/BOOT0 option bytes | TBD | Use SWD NRST; set nBOOT_SEL option; no external BOOT0 |
| P1-06 | ERC/DRC | BLOCKED | JLCEDA GUI only; record all warnings, not just "0 error" |

## Evidence

- STM32G030x6/x8 datasheet (DS12991): Figure 5 LQFP32 pinout; Table 12 pin assignment; Table 13 AF mapping; PA14-BOOT0 note; VDD/VDDA and VSS/VSSA merged.
- MX113H datasheet: 2-8V, 1A continuous/1.5A peak, SOT-23-6, pin 1 OUT2/2 GND/3 OUT1/4 VCC/5 IN1/6 IN2.
- TLV70033: 200mA max.
- MT3608: 5V/1A continuous target; L1 22uH, D1 SS34, R1 73.2k/R2 10k.

## Not claimed

- No fabricated PCB, no Gerber, no DRC/ERC pass, no firmware compatibility, no measured thrust/current, no tank test, no production readiness.
