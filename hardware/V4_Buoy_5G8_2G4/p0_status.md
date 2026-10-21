# P0/P1 status after round 7 review

Branch: `p0-g030-remediation`. Audit baseline: `abe8bc3e3f010765ddc304744eabf1a2dc9dec09`; earlier rounds: `6e78020`, `f93bf6b`, `5d7ef5a`, `2b874fc`, `e58a1cc`.
No PCB was ordered, no Gerber was generated, no production-ready claim is made.

## P0

| ID | Issue | Evidence | Status | Fix / remaining |
|---|---|---|---|---|
| P0-01 | TIM3 conflict: PA6/PA7 vertical PWM, PB1 jaw, PB0 LED | STM32G030x6/x8 datasheet Table 12/13 | **FIXED in docs** | Pinout/control board updated; JLCEDA schematic not ERC-verified |
| P0-02 | PA14-BOOT0/SWCLK | Datasheet pin 25 | **FIXED in docs** | No separate BOOT0 pin/resistor; SWD NRST; option bytes TBD |
| P0-03 | VDD/VDDA and VSS/VSSA merged | Datasheet pins 4/5 | **FIXED in docs** | Single `+3V3`/GND pins |
| P0-04 | MT3608 5V/1A at 3.0V and package thermal | MT3608 thetaJA 250C/W, PD 0.6W; loss split into diode/L1/chip | **BLOCKED** | Corrected chip TJ ~63-86C at 0.4A, 83-129C at 0.72A, 106-180C at 1A (40C, 250C/W). Not a proven pass/fail; measure efficiency and case temperature |
| P0-05 | TLV70033 current | 200mA max, not 300mA | **FIXED in docs** | 1uF input C15 + 1uF output C9 added |
| P0-06 | Q1 AON7403 had no -2.5V RDS(on) | AON7403 datasheet | **FIXED in docs** | SiSS23DN-T1-GE3, 6.3mohm max at -2.5V; pins 1-3 source, pin 4 gate, pins 5-8 drain; footprint/thermal verify |
| P0-07 | Battery/J1/protection current | ~4.96A continuous / ~6.46A peak including 5V input | **PARTIAL** | J1 XT30; actual motor/servo/protection current BLOCKED |
| P0-08 | J7 power/video connector and cable | JST-SH is 1A/28-32AWG; 24AWG incompatible | **PARTIAL** | JST-PH 6P proposed; 24AWG OD 0.9-1.5mm; mechanical fit PENDING |
| P0-09 | Buoyancy | mechanical.md said negative/neutral | **FIXED in docs** | Slightly positive; tank test still required |
| P0-10 | BOM duplicate refs/either-or | C1 Qty=3, AON7403/AO3401 | **FIXED in control BOM** | Unique refs; one selected part per function |
| P0-11 | LimeRC receiver source/license | Public GPL-3.0 source exists (`pingyun001/LimeRC`, commit `a9beb0…`); final build/hardware not proven | **PARTIAL** | Source available; final compile, RF pins, clock, pairing, PP polarity and UART loss behavior still BLOCKED; do not freeze buoy RF PCB |
| P0-12 | F407 HSE 24 vs 25MHz | V3 24MHz vs LimeCam 25MHz | **BLOCKED** | Resolve before layout |
| P0-13 | PP normal vs inverted TTL | LimeMini default inverted; LimeCam supports both | **BLOCKED** | Verify exact receiver setting |
| P0-14 | JLCEDA board name/ERC | Board renamed `Shark_Sub_G030`; GUI DRC run | **PARTIAL** | 137 `NETOBJECTONGRID` + 1 `CHECKFLOATPIN` warning; not ERC-clean |
| P0-15 | G030 schematic | Real four-page A3 JLCEDA project with system-library symbols; 45 components, 137 stubs, 32 nets | **DRAFTED** | Netlist export matches CSV 137/137; PCB empty; 138 DRC warnings; connector/footprint review still needed |
| P0-16 | F407 RF/firmware correspondence | E01C-ML01S not proven LimeCam-compatible | **BLOCKED** | `buoy_rf_board.md` dependency table |
| P0-17 | LED net: R7 fed from 3V3 | Netlist rows | **FIXED in netlist/docs** | PB0 -> R7.1 -> LED_A/LED1.1 -> GND |
| P0-18 | Net-name aliases | 3V3/5V, JAW, CAM_VIDEO, BUOY_TX, split BUOY_RX | **FIXED in docs/netlist** | `+3V3`, `+5V`, `JAW_SERVO`, `CVBS_VIDEO`, `PP_DOWN`/`BUOY_RX`, `TELEM_UP` |
| P0-19 | No committed netlist regression check | One-off manual check | **FIXED** | `check_netlist.py`; 137 rows, 32 nets, 45 refs pass |
| P0-20 | PP freshness on 2.4GHz loss | LimeRC `agreement_hal.c`: one neutral frame after 100ms, then silence | **FIXED in design** | G030 500ms no-frame timeout -> motors 0, jaw open; exact receiver firmware UART capture TBD |
| P0-21 | Magnet switch assumed toggle | Current SW1/R5/Q1 is hold-to-run | **FIXED in docs** | Magnet must remain; latch not designed and not added |
| P0-22 | 100uF/0805 ceramic effective capacitance | 0805 X5R loses large capacitance at 1S bias | **FIXED in BOM** | T520A107M006ATE070 100uF 6.3V polymer 1206; ripple/temperature TBD |
| P0-23 | J7/cable 3mm OD assumption | 2x24AWG + 2x28AWG + coax + jacket | **FIXED in docs/model** | ~5.0-5.5mm OD; 30mm static/55mm dynamic bend; physical fit PENDING |
| P0-24 | Negative/regression tests | Six netlist faults + geometry/metadata/semantic tests | **FIXED** | 18/18 pass: baseline, six netlist negatives, page parse, overlap/endpoint/pin-contact, metadata, fixed export, abe8bc3 fixture, Q1 swap, D1 swap; footprint BLOCKED |
| P0-25 | `.esch2` wire geometry overlaps/contacts | 137 LINE segments; old candidate had 21 conflicts | **FIXED in generator** | 500x380 placement, 30-unit stubs; 137 segments/32 nets/0 conflicts; `geometry_report.json`; negative tests pass |
| P0-26 | `.eprj3` / `.ecfg` / `.esch2` UUID mismatch | Old ecfg was F407 SCH/board | **FIXED in generator** | ecfg `b2c3…` / board `a1b2…` / `Schematic1`; metadata PASS; candidate still not GUI-verified |
| P0-27 | MT3608 thermal analysis assigned all converter loss to chip | Efficiency loss is system loss | **FIXED in docs** | Split diode/L1 core+DCR/chip conduction+switching+gate+quiescent; TJ ranges/sensitivity in `power_budget.md`; MT3608 remains BLOCKED |
| P0-28 | Q1 Source/Gate physical pins reversed in RevB | SiSS23DN pins 1-3 S, 4 G, 5-8 D; RevB had Q1.1 PWR_GATE and Q1.4 VBAT | **GUI VISUAL PASS / EXPORT BLOCKED** | GUI shows Q1.1/2/3 VBAT, Q1.4 PWR_GATE, Q1.5-8 VMOTOR; after screenshot saved; GUI Protel export still BLOCKED |
| P0-29 | D1 SS34 Anode/Cathode reversed in RevB | SS34 library pin 1 K, pin 2 A; RevB had K on SW and A on +5V | **GUI VISUAL PASS / FOOTPRINT BLOCKED** | GUI shows D1.1 K +5V and D1.2 A SW; PCB SMA cathode marking still TBD |
| P0-30 | Pin-number-only netlist comparison missed Q1/D1 semantics | 137/137 numeric match hid reversed physical pins | **FIXED** | `verify_g030_netlist.py` parses Ref/Pin/PinName/Net, checks 60 critical pins and CSV; old `abe8bc3` fixture fails on all four errors; Q1/D1 mutations rejected |
| P0-31 | 137 NETOBJECTONGRID + 1 CHECKFLOATPIN | Aggregate 138; per-page counts were duplicated | **GUI BLOCKED** | JLCEDA Pro opened, but the full DRC object/net/coordinate/rule/page log was not exported; grid realignment and explicit NC flags not completed; no DRC-clean claim |
| P0-32 | Actual EDA netlist export after RevB edit | `g030_export.net` corrected only provisionally | **GUI BLOCKED** | JLCEDA Pro opened and Q1/D1 visually checked; export dialog opened but Protel type could not be selected reliably; no GUI export produced; see `netlist_export_status.json` |
| P0-33 | 5V power device decision | MT3608 remains marginal above 0.4A; load TBD | **PARTIAL** | `power_options.md`: split two MT3608 rails or replace with TPS61022; TPS61022 preferred, not yet in schematic |
| P0-34 | J8 debug connector mismatch | Actual J8 is HDR1X5 2.54mm; BOM previously claimed 1.27mm pogo | **PARTIAL** | Proposed Tag-Connect TC2030 6-pad 1.27mm + TC2030-IDC; BOM marked DO NOT FAB; schematic symbol still placeholder |
| P0-35 | LimeRC reference compatibility | Actual schematic/source now reviewed; AS01-ML01S, 25MHz, OV2640, XOR PP | **PARTIAL** | PP default inverted/disabled; E01C/AS01 equivalence, final firmware and CVBS compatibility BLOCKED |
| P0-36 | 5m depth sensing absent | No pressure sensor in RevB; PA4/PA5 are not I2C | **BLOCKED** | Proposed I2C1 on PB6/PB7 + J10; MS5837-02BA needs 1.5-1.8bar characterization; no schematic change |
| P0-37 | 5m buoy cable | Current design is 50cm/24AWG/JST-PH | **BLOCKED** | 18-20AWG power or separate IP68 connector, coax, TVS, strain relief, drop/ripple test required |
| P0-38 | MX113H thermal/current | 1A cont at 25C, 0.4ohm, 220C/W; 1.5A peak; J2-J4 1A | **MEASUREMENT_REQUIRED** | Sealed-hull continuous current must be derated; three 1A motors not approved; connector upgrade TBD |

## P1

| ID | Issue | Status | Action |
|---|---|---|---|
| P1-01 | 5.8G VTX 75 ohm input termination | TBD | Check VTX datasheet/input |
| P1-02 | Board fit/size | TBD | G030 26x40-46 first pass; F407 30x30-30x35; layout before freeze |
| P1-03 | L1 SRP6060FA-220M saturation/thermal | TBD | 22uH, Isat 5.6A, Irms 3.8A; measure at 3.0V/1A |
| P1-04 | J7/J1/cable current | TBD | XT30; JST-PH proposed; measure 5V + motor peak + servo stall |
| P1-05 | SWD/BOOT0 option bytes | TBD | SWD NRST; nBOOT_SEL option |
| P1-06 | ERC/DRC | PARTIAL | DRC run: 137 NETOBJECTONGRID + one unused-pin warning; still no clean ERC/DRC |
| P1-07 | Servo stall / 5V headroom | TBD | Measure; 0.52A other load + 0.5A servo already exceeds 1A |
| P1-08 | Q1 copper/thermal | TBD | PowerPAK 1212-8S land pattern/copper at ~6.5A peak |
| P1-09 | MT3608 replacement | BLOCKED | Select larger boost or split/reduce 5V load |
| P1-10 | Schematic GUI/ERC/footprint binding | PARTIAL | Project opens; real library symbols/footprints; PCB empty; connector/footprint mapping review and DRC cleanup remain |
| P1-11 | J7/cable/gland physical fit | TBD | Print mock-up, 24AWG crimp pull test, bend/gland check |
| P1-12 | C1-C3 polymer ripple/temperature | TBD | 20kHz motor ripple and case temperature |
| P1-13 | J7 mechanical model used wrong assembly object | **PARTIAL** | Separate shark-side G030/J7/hull/gland and buoy-side F407/VTX/shell models; sizes TBD |
| P1-14 | Symbol/footprint binding | **PARTIAL** | RevB uses real JLCEDA library symbols/footprints for 45 parts; old generator candidate explicitly FOOTPRINT BLOCKED; connector/NC review remains |
| P1-15 | Automatic test categories | **FIXED** | STRUCTURAL/GEOMETRY/METADATA/FOOTPRINT/ERC categories; parser crashes not counted as pass |
| P1-16 | LimeRC source status | **PARTIAL** | Upstream GPL-3.0 source available; final build, RF pins, clock, PP polarity, UART loss behavior and third-party licenses remain BLOCKED/TBD |
| P1-17 | RevB Q1/D1 screenshots and DRC object log | **PARTIAL** | Q1 and D1 after screenshots captured in GUI; full DRC object log, grid realignment and NC flags still BLOCKED |
| P1-18 | Q1/D1 first-power test | **BLOCKED** | No battery or PCB; first power only with current-limited supply, no motors/servo/camera/buoy; verify no short and 5V/3.3V rails |
| P1-19 | 5V converter selection | **PARTIAL** | TPS61022 preferred, target 1.5A at 3.0V; split-MT3608 fallback; actual schematic/BOM change not made; stall/VTX current TBD |
| P1-20 | J8 1.27mm pogo implementation | **PARTIAL** | Tag-Connect TC2030 6-pad + TC2030-IDC proposed; actual J8 symbol/footprint still HDR1X5 |
| P1-21 | Footprint/polarity audit | **PARTIAL** | Symbol pin maps checked; PCB pad numbering, D1 cathode, C1-C3 positive marking and connector mechanical pads still require layout inspection |
| P1-22 | Round 7 reference audit | **PARTIAL** | LimeRC schematic/source reviewed; LimeMini hardware archive still BLOCKED |
| P1-23 | Round 7 static regression | **PASS** | 18/18 existing and 10/10 new static tests; not ERC/DRC or physical test |

## Evidence

- STM32G030x6/x8 datasheet (DS12991): LQFP32 pins/AF, PA14-BOOT0, merged VDD/VDDA and VSS/VSSA.
- LimeRC source `pingyun001/LimeRC`, commit `a9beb0102be529bc43736acc8ca2f508560c46d6`, `Agreement/agreement_hal.c`: after >100ms no NRF packet, channels set to 2048 and exactly one frame sent, then `isOffline = true`.
- MT3608 datasheet: thetaJA 250C/W, PD 0.6W, TJ 160C. Calculations in `power_budget.md`.
- Vishay SiSS23DN datasheet: 20V/50A package-limited, 6.3mohm max at VGS=-2.5V, PowerPAK 1212-8S pinout.
- JST PH datasheet: 2A at AWG24, AWG32-24, insulation OD 0.5-1.5mm; B6B-PH-K-S / PHR-6 / SPH-002T-P0.5S.
- KEMET T520A107M006ATE070: 100uF 6.3V polymer tantalum, 70mohm, 1.035A ripple at 45C.
- `check_netlist.py` and `tests/run_negative_tests.py`: STRUCTURAL/GEOMETRY/METADATA tests, not EDA ERC.
- Geometry: `hardware/g030_control/geometry_report.json` — 137 segments, 32 nets, 0 conflicts; `check_schematic_geometry.py` re-parses the actual `.esch2` LINE/NET records. Negative tests cover overlap, endpoint and pin contact.
- Metadata: `.eprj3`, `Schematic1.ecfg`, and `.esch2` match board `a1b2…`, schematic `b2c3…`, page `c3d4…`; candidate project still not GUI-verified.
- RevB binding review: `hardware/g030_control/component_binding.md`; 45 real library devices, exact connector/NC/PCB checks remain PARTIAL.
- RevB Q1/D1: `hardware/g030_control/revb_q1_d1_fix.md`; corrected `01_POWER.esch2`, 18/18 tests, old `abe8bc3` fixture fails on Q1.1, Q1.4, D1.1, D1.2.
- Semantic report: `hardware/g030_control/semantic_report.json` - 137 pins, 32 nets, 60 critical pins, 0 CSV mismatches; export is provisional, not GUI-regenerated.
- JLCEDA GUI verification: four-page A3 project opens; 45 system-library components, 137 net-name stubs, 32 nets; netlist export matches CSV 137/137. DRC: 137 `NETOBJECTONGRID` + one `CHECKFLOATPIN` warning. Evidence: `hardware/g030_control/`.
- Netlist comparison: `hardware/g030_control/netlist_compare.json`; DRC warning list: `hardware/g030_control/drc_result.json`.

## Not claimed

- No fabricated PCB, no Gerber, no clean DRC/ERC pass, no firmware compatibility, no measured thrust/current, no servo stall data, no MT3608 thermal test, no J7 physical fit, no tank test, no production readiness.
- `check_netlist.py` is not an electrical rule check and cannot catch wrong pin functions, missing decoupling, or footprint errors.
- The G030 schematic has real library symbols but uses net-name stubs, not fully routed presentation wiring; connector/footprint mappings and the single DRC warning still need review. The PCB is empty.
