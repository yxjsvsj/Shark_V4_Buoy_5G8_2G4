# V4 Buoy 5.8G / 2.4G - ACTIVE

Status: **ACTIVE. Buoy architecture selected. Do not draw the final sub PCB until the buoy link test passes.**
Goal: fully submerged 10-15 cm freshwater shark, 3 thrusters, jaw, real-time video, no long shore tether.
The shark tows a short cable to a small surface buoy. All RF stays above water.

## 1. Architecture

```
[Shark, fully submerged]
  camera CVBS + G030 + 3 ESC/MX113H + jaw servo + 1S + 5V boost
        |
        | 50 cm, 6-core cable:
        | +5V (cable +5V_BUOY), GND_PWR, CVBS_VIDEO, GND_VIDEO, PP_DOWN, TELEM_UP
        v
[Buoy, on the surface]
  5.8G 25mW VTX + cloverleaf
  2.4G LimeCam receiver + 31 mm antenna
        |
        | 5.8G air                     | 2.4G air
        v                              v
[5.8G receiver + USB capture/5" monitor]  [LimeRC remote]
```

- Video: underwater CVBS camera -> cable -> 5.8G VTX on buoy -> 5.8G receiver at tank edge.
- Control: LimeRC remote -> 2.4G receiver on buoy -> `pp` UART -> cable -> G030 in shark.
- No IR, no 433M, no 1.2G. 2.4G and 5.8G are in air, not water.

## 2. Why this is the high-success option

- 5.8G with the antenna above water is a standard, reliable FPV link; 25mW is enough for a fish tank.
- 2.4G with the receiver on the buoy is the original LimeRC link in air; it reuses the remote and `pp` protocol.
- The only underwater link is a short cable, not RF.
- Commercial 1.2G underwater fishing cameras use a floating transmitter; RC submarine FPV often uses a surface boat/buoy. This is the proven pattern.

## 3. Size and weight

| Part | Size | Weight |
|---|---|---|
| Buoy shell | 55 mm dia x 70 mm tall, PETG, 1.5 mm wall | 25-40 g |
| Buoy electronics | 5.8G VTX + LimeCam + caps | 20-30 g |
| Buoy battery | none (powered from shark) | 0 |
| Keel + mast + gland | 10-20 g | 10-20 g |
| **Buoy total** | ~60 x 80 mm with antenna | **50-80 g** |
| Cable | 50 cm, 6-core, ~3 mm OD, neutral | 16-24 g |
| Shark | 10-15 cm | 90-130 g |

Buoy displacement ~150 cm3, so it has enough reserve to float with the cable and antenna.

## 4. Cost

| Item | Qty | Approx RMB |
|---|---|---|
| 5.8G 25mW VTX | 1 | 30-80 |
| 5.8G receiver (RX5808-class) | 1 | 50-150 |
| CVBS camera 1/3" 1200TVL 2.1mm 5V | 1 | 40-100 |
| 5.8G antennas (VTX cloverleaf + RX cloverleaf) | 2 | 20-60 |
| LimeCam/LimeRC control receiver | 1 | reuse: 0; new 2.4G: 20-40 |
| 2.4G 31 mm antenna | 1 | 5-10 |
| 5V boost/filter | 1 | 5-15 |
| Buoy shell/foam/keel/mast/gland | 1 set | 10-30 |
| 6-core shielded cable + connectors | 1 set | 10-30 |
| Tank-edge capture/monitor | 1 | 30-300 |

**Total: about 150-400 RMB** (plus monitor/capture if needed). Reusing LimeCam/LimeRC saves the control receiver cost.

## 5. Success rate

| Link / part | Expected success | Notes |
|---|---|---|
| 5.8G video (antenna above water) | Very high | 25mW, 640x480, low latency; 10-50 m in air |
| 2.4G control (receiver on buoy) | Very high | Original LimeRC link; no water path |
| Buoy / cable / sealing | Medium first build | Flip, tangle, cable gland leak are the risks |
| Overall | High | RF is no longer the bottleneck; mechanics are |

## 6. Power and cable

- Protected 1S -> Q1 SiSS23DN-T1-GE3 -> `VMOTOR` -> 3x MX113H.
- Protected 1S -> MT3608 +5V boost candidate -> camera/buoy/servo -> TLV70033 +3V3/200mA -> G030.
- Do not use a 1S-to-3.3V LDO. Do not stack a second boost without checking the LimeMini original.
- **MT3608 is not thermally approved for 0.72A or 1A at 3.0V.** The datasheet 250C/W package estimate gives about 199C at 0.72A and 261C at 1A in 40C ambient. The 0.4A case is about 128C; still not a comfortable design. See `power_budget.md`.
- +5V nominal load is ~0.72A, but servo stall is not measured and may exceed 1A with the other loads. **The 5V source must be resized or split before layout.**
- +5V/1A at 3.0V/85% is ~1.96A input; L1 is SRP6060FA-220M, Isat 5.6A, Irms 3.8A.
- Q1 is rated 20V/50A and 6.3mohm max at VGS=-2.5V; AON7403 is not approved for 1S gate drive.
- C1-C3 are **100uF 6.3V polymer tantalum 1206** (T520A107M006ATE070), not 100uF/0805 X5R.
- Cable: 50 cm, 6 cores, 24AWG for +5V/GND, 28AWG signals, separate shielded video pair/coax. Finished OD is **~5.0-5.5mm**, not 3mm.
- J7: **JST-PH 6P, 2.0mm, 2A at 24AWG** (proposed; series change pending confirmation). JST-SH 1A/28-32AWG cannot take 24AWG.
- J7/24AWG insulation OD must be 0.9-1.5mm; crimp pull test required. 30mm static / 55mm dynamic bend is tight in a 55mm buoy.
- Pins: 1=+5V (cable +5V_BUOY), 2=GND_PWR, 3=CVBS_VIDEO, 4=GND_VIDEO, 5=PP_DOWN, 6=TELEM_UP.
- Add 100uF + 100nF at the buoy +5V input and a ferrite/LC filter for the camera/video.
- PP link loss: LimeCam sends one neutral frame after ~100ms, then stops; use the 500ms G030 frame timeout for failsafe. See `pp_link_behavior.md`.
- Use a Kevlar/string strength member; the cable must not be the tow load.
- Waterproof gland at the buoy; potted/gland at the shark; strain relief loop at both ends.
- 50 cm is for shallow testing; make a longer version for 50 cm depth plus float/connector margin.

## 7. Buoy mechanical

- PETG 3D printed shell, 55 mm diameter, 70 mm tall, screw lid with O-ring.
- Foam inside for reserve buoyancy; 10-15 g keel at the bottom.
- 5.8G cloverleaf on a 20 mm mast; 2.4G 31 mm wire on the opposite side; at least 5 cm apart.
- Cable exits the bottom through a gland; a tow loop above the gland takes the strain.
- The buoy must stay upright; the keel and mast help. If it flips, increase keel or add a small drop keel.
- The buoy is visible in the tank; shape it as a small fish/float/tag if desired.

## 8. Shark side

- New G030 board (the user has no original board): 3x MX113H, 1 jaw servo, camera 5V, 5V boost, 3.3V from 5V, battery ADC, leak, UART2 `pp`. No RF.
- First-pass board 26x40-46 mm; target 20x30 mm after layout.
- Camera in the nose behind a 2 mm acrylic window; 2.1 mm lens; white LED fill.
- Cable exits the top/back; the shark tows the buoy; keep the cable slack.
- 1S 450mAh 30C; 3 thrusters; jaw; 10-15 cm hull.
- H-bridges off at reset; PP frame validation; watchdog; low voltage/leak; positive buoyancy.
- Measure thruster running/start/stall current before layout; MX113H 1A continuous / 1.5A peak.

## 9. Test plan

1. Buoy leak test, float test, cable strain test; check 5V at the buoy.
2. 5.8G video in air; then camera in a glass of tank water with the buoy above water; test 10/20/30/40 cm camera depth.
3. 2.4G control: LimeRC remote -> buoy receiver -> `pp` -> G030; run motors/servo; 10 minutes.
4. Shark tows buoy in the tank: turns, dive, jaw; check buoy upright, cable not tangled, video/control stable.
5. Failsafe: unplug cable / remote off -> motors stop, jaw open; shark floats.

Pass: stable 640x480 video, no control dropout, no leaks, buoy upright, no cable tangle.

## 10. Files

- `bom.csv` - buoy + tank-edge BOM.
- `mechanical.md` - buoy dimensions, cable, sealing.
- `test_plan.md` - detailed test steps and pass criteria.
- `control_board.md` - G030 sub control board.
- `control_pinout.csv` - G030 pin/peripheral map.
- `control_bom.csv` - G030 BOM.
- `g030_netlist_draft.csv` - G030 connection-level netlist.
- `check_netlist.py` - structural netlist checker; run `python hardware/V4_Buoy_5G8_2G4/check_netlist.py`.
- `tests/run_negative_tests.py` - six structural negative tests; results in `tests/negative_test_results.json`.
- `power_budget.md` - MT3608/Q1/servo/capacitor budget and measured-data gaps.
- `pp_link_behavior.md` - LimeCam PP link-loss behavior and G030 safety logic.
- `mechanical/j7_assembly.md` - J7/cable dimensions, bend radius and fit conclusion.
- `g030_control/` - candidate JLCEDA Pro `.eprj3`/`.esch2` schematic; format-validated only.
- `buoy_rf_board.md` - stripped F407 buoy RF board and firmware gate.
- `two_board_plan.md` - two-board redesign plan.
- `keep_remove.md` - keep/remove from the open-source boards.
- `design_review.md` - P0/P1 review, firmware source, clock, power, cable, sizes, safety.

## 11. Caveats and gates

- This is a **short-tether buoy**, not a fully wireless submarine. The shark is fully submerged; the buoy is on the surface.
- The buoy adds drag and visibility; keep it small and streamlined.
- 5.8G is chosen because the antenna is above water; do not put the 5.8G VTX underwater.
- **Firmware gate:** LimeRC receiver source/license, RF module, pairing, clock (V3 24MHz vs original 25MHz), PP polarity. If only HEX is available, use the original LimeCam board or get source/permission; do not stub tasks blindly.
- **Motor gate:** measure thruster current/thrust and MX113H thermal before layout.
- **Power/connector gate:** MT3608 0.72A/1A thermal rejection, Q1 footprint/thermal, L1 SRP6060FA-220M, servo stall, C1-C3 ripple, and J7 mechanical fit must be closed before layout freeze.
- **Schematic gate:** `Shark_Sub_G030.esch2` is a candidate with generic symbols and no footprint binding. Open it in JLCEDA, run ERC, and fix it before calling it drafted.
- **Size gate:** board sizes are not frozen; layout first.
- If the buoy/cable proves troublesome, the fallback is a thin shore tether or a smaller antenna float.
