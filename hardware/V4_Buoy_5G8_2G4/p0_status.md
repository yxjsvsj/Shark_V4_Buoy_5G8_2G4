# P0/P1 status after third-round review

Branch: `p0-g030-remediation`. Base: `b143d9b`; round 2: `6e78020`, `f93bf6b`; round 3: this commit.
No PCB was ordered, no Gerber was generated, no production-ready claim is made.

## P0

| ID | Issue | Evidence | Status | Fix / remaining |
|---|---|---|---|---|
| P0-01 | TIM3 conflict: PA6/PA7 vertical PWM, PB1 jaw, PB0 LED | STM32G030x6/x8 datasheet Table 12/13 | **FIXED in docs** | Pinout/control board updated; JLCEDA schematic not ERC-verified |
| P0-02 | PA14-BOOT0/SWCLK | Datasheet pin 25 | **FIXED in docs** | No separate BOOT0 pin/resistor; SWD NRST; option bytes TBD |
| P0-03 | VDD/VDDA and VSS/VSSA merged | Datasheet pins 4/5 | **FIXED in docs** | Single `+3V3`/GND pins |
| P0-04 | MT3608 5V/1A at 3.0V and package thermal | MT3608 thetaJA 250C/W, PD 0.6W | **BLOCKED** | TJ ~128C at 0.4A, ~199C at 0.72A, ~261C at 1A (40C ambient). 0.72A/1A rejected; replace boost, split rail or reduce load |
| P0-05 | TLV70033 current | 200mA max, not 300mA | **FIXED in docs** | 1uF input C15 + 1uF output C9 added |
| P0-06 | Q1 AON7403 had no -2.5V RDS(on) | AON7403 datasheet | **FIXED in docs** | SiSS23DN-T1-GE3, 6.3mohm max at -2.5V; pin1 gate, 2-4 source, 5-8 drain; footprint/thermal verify |
| P0-07 | Battery/J1/protection current | ~4.96A continuous / ~6.46A peak including 5V input | **PARTIAL** | J1 XT30; actual motor/servo/protection current BLOCKED |
| P0-08 | J7 power/video connector and cable | JST-SH is 1A/28-32AWG; 24AWG incompatible | **PARTIAL** | JST-PH 6P proposed; 24AWG OD 0.9-1.5mm; mechanical fit PENDING |
| P0-09 | Buoyancy | mechanical.md said negative/neutral | **FIXED in docs** | Slightly positive; tank test still required |
| P0-10 | BOM duplicate refs/either-or | C1 Qty=3, AON7403/AO3401 | **FIXED in control BOM** | Unique refs; one selected part per function |
| P0-11 | LimeRC receiver source/license | Public GPL-3.0 source exists, but production hardware/HEX compatibility is not proven | **BLOCKED** | Do not freeze buoy RF PCB; verify source/license/hardware match |
| P0-12 | F407 HSE 24 vs 25MHz | V3 24MHz vs LimeCam 25MHz | **BLOCKED** | Resolve before layout |
| P0-13 | PP normal vs inverted TTL | LimeMini default inverted; LimeCam supports both | **BLOCKED** | Verify exact receiver setting |
| P0-14 | JLCEDA board name/ERC | Board renamed `Shark_Sub_G030`; GUI DRC run | **PARTIAL** | One `CHECKFLOATPIN` warning for intentionally unused pins; not ERC-clean |
| P0-15 | G030 schematic | Real JLCEDA project with system-library symbols; 45 components, 137 stubs, 32 nets | **DRAFTED** | Netlist export matches CSV 137/137; PCB empty; DRC warning; connector/footprint review still needed |
| P0-16 | F407 RF/firmware correspondence | E01C-ML01S not proven LimeCam-compatible | **BLOCKED** | `buoy_rf_board.md` dependency table |
| P0-17 | LED net: R7 fed from 3V3 | Netlist rows | **FIXED in netlist/docs** | PB0 -> R7.1 -> LED_A/LED1.1 -> GND |
| P0-18 | Net-name aliases | 3V3/5V, JAW, CAM_VIDEO, BUOY_TX, split BUOY_RX | **FIXED in docs/netlist** | `+3V3`, `+5V`, `JAW_SERVO`, `CVBS_VIDEO`, `PP_DOWN`/`BUOY_RX`, `TELEM_UP` |
| P0-19 | No committed netlist regression check | One-off manual check | **FIXED** | `check_netlist.py`; 137 rows, 32 nets, 45 refs pass |
| P0-20 | PP freshness on 2.4GHz loss | LimeRC `agreement_hal.c`: one neutral frame after 100ms, then silence | **FIXED in design** | G030 500ms no-frame timeout -> motors 0, jaw open; exact receiver firmware UART capture TBD |
| P0-21 | Magnet switch assumed toggle | Current SW1/R5/Q1 is hold-to-run | **FIXED in docs** | Magnet must remain; latch not designed and not added |
| P0-22 | 100uF/0805 ceramic effective capacitance | 0805 X5R loses large capacitance at 1S bias | **FIXED in BOM** | T520A107M006ATE070 100uF 6.3V polymer 1206; ripple/temperature TBD |
| P0-23 | J7/cable 3mm OD assumption | 2x24AWG + 2x28AWG + coax + jacket | **FIXED in docs/model** | ~5.0-5.5mm OD; 30mm static/55mm dynamic bend; physical fit PENDING |
| P0-24 | Negative regression tests | Six deliberate faults | **FIXED** | All six rejected; results retained in `tests/negative_test_results.json` |

## P1

| ID | Issue | Status | Action |
|---|---|---|---|
| P1-01 | 5.8G VTX 75 ohm input termination | TBD | Check VTX datasheet/input |
| P1-02 | Board fit/size | TBD | G030 26x40-46 first pass; F407 30x30-30x35; layout before freeze |
| P1-03 | L1 SRP6060FA-220M saturation/thermal | TBD | 22uH, Isat 5.6A, Irms 3.8A; measure at 3.0V/1A |
| P1-04 | J7/J1/cable current | TBD | XT30; JST-PH proposed; measure 5V + motor peak + servo stall |
| P1-05 | SWD/BOOT0 option bytes | TBD | SWD NRST; nBOOT_SEL option |
| P1-06 | ERC/DRC | PARTIAL | DRC run: one unused-pin warning; still no clean ERC/DRC |
| P1-07 | Servo stall / 5V headroom | TBD | Measure; 0.52A other load + 0.5A servo already exceeds 1A |
| P1-08 | Q1 copper/thermal | TBD | PowerPAK 1212-8S land pattern/copper at ~6.5A peak |
| P1-09 | MT3608 replacement | BLOCKED | Select larger boost or split/reduce 5V load |
| P1-10 | Schematic GUI/ERC/footprint binding | PARTIAL | Project opens; real library symbols/footprints; PCB empty; connector/footprint mapping review and DRC cleanup remain |
| P1-11 | J7/cable/gland physical fit | TBD | Print mock-up, 24AWG crimp pull test, bend/gland check |
| P1-12 | C1-C3 polymer ripple/temperature | TBD | 20kHz motor ripple and case temperature |

## Evidence

- STM32G030x6/x8 datasheet (DS12991): LQFP32 pins/AF, PA14-BOOT0, merged VDD/VDDA and VSS/VSSA.
- LimeRC source `pingyun001/LimeRC`, commit `a9beb0102be529bc43736acc8ca2f508560c46d6`, `Agreement/agreement_hal.c`: after >100ms no NRF packet, channels set to 2048 and exactly one frame sent, then `isOffline = true`.
- MT3608 datasheet: thetaJA 250C/W, PD 0.6W, TJ 160C. Calculations in `power_budget.md`.
- Vishay SiSS23DN datasheet: 20V/50A package-limited, 6.3mohm max at VGS=-2.5V, PowerPAK 1212-8S pinout.
- JST PH datasheet: 2A at AWG24, AWG32-24, insulation OD 0.5-1.5mm; B6B-PH-K-S / PHR-6 / SPH-002T-P0.5S.
- KEMET T520A107M006ATE070: 100uF 6.3V polymer tantalum, 70mohm, 1.035A ripple at 45C.
- `check_netlist.py` and `tests/run_negative_tests.py`: structural results only, not EDA ERC.
- JLCEDA GUI verification: project opens; 45 system-library components, 137 net-name stubs, 32 nets; netlist export matches CSV 137/137. DRC: one `CHECKFLOATPIN` warning. Evidence: `hardware/g030_control/`.
- Netlist comparison: `hardware/g030_control/netlist_compare.json`; DRC warning list: `hardware/g030_control/drc_result.json`.

## Not claimed

- No fabricated PCB, no Gerber, no clean DRC/ERC pass, no firmware compatibility, no measured thrust/current, no servo stall data, no MT3608 thermal test, no J7 physical fit, no tank test, no production readiness.
- `check_netlist.py` is not an electrical rule check and cannot catch wrong pin functions, missing decoupling, or footprint errors.
- The G030 schematic has real library symbols but uses net-name stubs, not fully routed presentation wiring; connector/footprint mappings and the single DRC warning still need review. The PCB is empty.
