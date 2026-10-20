# P0/P1 status after remediation

Branch: `p0-g030-remediation`. Base: `b143d9b`; previous remediation: `6e78020`; second remediation: this commit.
No PCB was ordered, no Gerber was generated, no production-ready claim is made.

## P0

| ID | Issue | Evidence | Status | Fix / remaining |
|---|---|---|---|---|
| P0-01 | TIM3 conflict: PA6/PA7 vertical PWM, PB1 jaw, PB0 LED | STM32G030x6/x8 datasheet Table 12/13: PA6 TIM3_CH1, PA7 TIM3_CH2, PB1 TIM14_CH1, PB0 GPIO/TIM3_CH3 | **FIXED in docs** | Pinout/control board updated; JLCEDA schematic still not drawn |
| P0-02 | PA14-BOOT0/SWCLK | Datasheet pin 25: PA14-BOOT0, SWCLK; internal pull-down; nBOOT_SEL option | **FIXED in docs** | No separate BOOT0 pin/resistor; SWD NRST; option bytes TBD |
| P0-03 | VDD/VDDA and VSS/VSSA merged on LQFP32 | Datasheet pins 4/5: VDD/VDDA, VSS/VSSA | **FIXED in docs** | Single `+3V3`/GND pins; no separate 3V3_A/VDDA net |
| P0-04 | 5V boost was "MT3608 or TPS61023" | BOM ambiguity; input current was understated | **FIXED in docs** | MT3608 +5V/1A; 3.0V/85% input = 1.96A; L1 Isat >=3.5A, Irms >=2.2A; load/thermal measurement TBD |
| P0-05 | TLV70033 current | TLV70033 200mA max, not 300mA | **FIXED in docs** | +3V3 load ~20mA; 200mA enough |
| P0-06 | P-MOS was AON7403/AO3401 | AON7403 has no RDS(on) at VGS=-2.5V | **FIXED in docs** | Selected SiSS23DN-T1-GE3, 20V/50A, 6.3mohm max at -2.5V; pin1 gate, 2-4 source, 5-8 drain; footprint/thermal verify |
| P0-07 | Battery/J1/protection current | ~4.96A continuous / ~6.46A peak including 5V input | **PARTIAL** | J1 XT30; protected pack; actual motor/servo/protection current still BLOCKED |
| P0-08 | J7 cable and video return | JST-SH is 1A/28-32AWG; 24AWG power incompatible | **PARTIAL** | J7 changed to proposed JST-PH 6P (2A/24AWG, 24-30AWG); series change PENDING CONFIRMATION; VTX 75 ohm termination TBD |
| P0-09 | Buoyancy | mechanical.md said negative/neutral | **FIXED in docs** | Shark slightly positive; power-loss surfacing still needs tank test |
| P0-10 | BOM duplicate refs/either-or | C1 Qty=3, MT3608 or TPS61023, AON7403/AO3401 | **FIXED in control BOM** | Unique refs; one selected part per function |
| P0-11 | LimeRC receiver source/license | Hardware CC BY-SA 4.0; source copyright separate; HEX personal/non-commercial | **BLOCKED** | Need source/permission or use original LimeCam board |
| P0-12 | F407 HSE 24 vs 25MHz | V3 project 24MHz; original LimeCam code 25MHz | **BLOCKED** | Must match final firmware before layout |
| P0-13 | PP normal vs inverted TTL | LimeMini default inverted; LimeCam supports normal/inverted | **BLOCKED** | New design uses normal TTL; verify firmware setting |
| P0-14 | JLCEDA board name/ERC | `.eprj3` name was overwritten by JLCEDA once; no GUI ERC | **BLOCKED** | Rename/save in JLCEDA UI; run ERC there |
| P0-15 | G030 schematic draft | Connection-level draft created | **DRAFT** | `g030_schematic_draft.md` + `g030_netlist_draft.csv`; no `.esch2`, no ERC |
| P0-16 | F407 RF/firmware correspondence | E01C-ML01S not proven LimeCam-compatible | **BLOCKED** | `buoy_rf_board.md` dependency table |
| P0-17 | LED net: R7 fed from 3V3, PB0 on same net | Netlist rows showed 3V3->R7, R7->LED, LED->PB0 | **FIXED in netlist/docs** | PB0 -> R7.1, R7.2 -> LED_A/LED1.1, LED1.2 -> GND; checker rejects 3V3 on R7 |
| P0-18 | Net-name aliases | 3V3/5V, JAW/JAW_SERVO, CAM_VIDEO/CVBS_VIDEO, BUOY_TX/TELEM_UP, split BUOY_RX nets | **FIXED in docs/netlist** | Canonical: `+3V3`, `+5V`, `JAW_SERVO`, `CVBS_VIDEO`, `PP_DOWN`/`BUOY_RX`, `TELEM_UP` |
| P0-19 | No committed netlist regression check | Prior check was a one-off manual command | **FIXED** | `hardware/V4_Buoy_5G8_2G4/check_netlist.py`; structural rules only, not ERC |

## P1

| ID | Issue | Status | Action |
|---|---|---|---|
| P1-01 | 5.8G VTX 75 ohm input termination | TBD | Check VTX datasheet/input; avoid double termination |
| P1-02 | Board fit/size | TBD | G030 26x40-46 first pass; F407 30x30-30x35; layout before freeze |
| P1-03 | MT3608 inductor saturation/thermal | TBD | 22uH Isat >=3.5A, Irms >=2.2A; measure at +5V/1A and 3.0V input |
| P1-04 | J7/J1/cable current | TBD | XT30; JST-PH proposed, 24AWG +5V/GND; measure +5V + motor peak + servo stall; JST-PH series pending confirmation |
| P1-05 | SWD/BOOT0 option bytes | TBD | Use SWD NRST; set nBOOT_SEL option; no external BOOT0 |
| P1-06 | ERC/DRC | BLOCKED | JLCEDA GUI only; record all warnings, not just "0 error" |
| P1-07 | Servo stall / +5V headroom | TBD | Measure servo stall; 1A boost may not supply stall + camera/buoy simultaneously |
| P1-08 | Q1 copper/thermal | TBD | Verify PowerPAK 1212-8S footprint and copper at ~6.5A peak |

## Evidence

- STM32G030x6/x8 datasheet (DS12991): Figure 5 LQFP32 pinout; Table 12 pin assignment; Table 13 AF mapping; PA14-BOOT0 note; VDD/VDDA and VSS/VSSA merged.
- MX113H datasheet: 2-8V, 1A continuous/1.5A peak, SOT-23-6, pin 1 OUT2/2 GND/3 OUT1/4 VCC/5 IN1/6 IN2.
- TLV70033: 200mA max.
- MT3608: +5V/1A continuous target; L1 22uH, D1 SS34, R1 73.2k/R2 10k; 3.0V/85% input = 1.96A.
- Vishay SiSS23DN datasheet: P-channel 20V, 50A package-limited, 6.3mohm max at VGS=-2.5V; PowerPAK 1212-8S pin 1 gate, pins 2-4 source, pins 5-8 drain.
- JST PH datasheet: 2A at AWG24, applicable wire AWG32-24; B6B-PH-K-S / PHR-6 / SPH-002T-P0.5S.
- `check_netlist.py`: structural net/ref/pin checks plus LED, Q1 pinout, J7 pin map, and canonical-net rules.

## Not claimed

- No fabricated PCB, no Gerber, no DRC/ERC pass, no firmware compatibility, no measured thrust/current, no servo stall measurement, no tank test, no production readiness.
- `check_netlist.py` is not an electrical rule check; it cannot catch wrong pin functions, missing decoupling, or footprint errors.
