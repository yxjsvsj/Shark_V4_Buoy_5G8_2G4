# V4 Buoy 5.8G / 2.4G - ACTIVE

Status: **ACTIVE. Buoy architecture selected. Do not draw the final sub PCB until the buoy link test passes.**
Goal: fully submerged 10-15 cm freshwater shark, 3 thrusters, jaw, real-time video, no long shore tether.
The shark tows a short cable to a small surface buoy. All RF stays above water.

## 1. Architecture

```
[Shark, fully submerged]
  camera CVBS + G030 + 3 ESC/MX113H + jaw servo + 1S + 5V boost
        |
        | 50 cm, 6-core shielded cable:
        | 5V, GND, VIDEO, UART_TX, UART_RX, spare
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

- Shark 1S -> 5V boost (1A) -> cable 5V -> buoy VTX + LimeCam + camera.
- 5V current: VTX 0.2A + LimeCam 0.1A + camera 0.1A = ~0.4A; 1A boost is enough.
- Cable: 6 cores, 26-28AWG silicone, shielded pair for video; 50 cm.
- Pins: 1=5V, 2=GND, 3=VIDEO, 4=UART_TX (buoy->sub), 5=UART_RX (sub->buoy), 6=spare/GND.
- Add 100uF + 100nF at the buoy 5V input and a ferrite/LC filter for the camera/video.
- Use a Kevlar/string strength member; the cable must not be the tow load.
- Waterproof gland at the buoy; potted/gland at the shark; strain relief loop at both ends.

## 7. Buoy mechanical

- PETG 3D printed shell, 55 mm diameter, 70 mm tall, screw lid with O-ring.
- Foam inside for reserve buoyancy; 10-15 g keel at the bottom.
- 5.8G cloverleaf on a 20 mm mast; 2.4G 31 mm wire on the opposite side; at least 5 cm apart.
- Cable exits the bottom through a gland; a tow loop above the gland takes the strain.
- The buoy must stay upright; the keel and mast help. If it flips, increase keel or add a small drop keel.
- The buoy is visible in the tank; shape it as a small fish/float/tag if desired.

## 8. Shark side

- G030/G031 board: 3 ESC outputs (or 3x MX113H), 1 jaw servo, camera 5V, 5V boost, battery ADC, leak, UART2 for `pp`. No RF.
- Camera in the nose behind a 2 mm acrylic window; 2.1 mm lens; white LED fill.
- Cable exits the top/back; the shark tows the buoy; keep the cable slack.
- 1S 450mAh 30C; 3 thrusters; jaw; 10-15 cm hull.

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

## 11. Caveats

- This is a **short-tether buoy**, not a fully wireless submarine. The shark is fully submerged; the buoy is on the surface.
- The buoy adds drag and visibility; keep it small and streamlined.
- 5.8G is chosen because the antenna is above water; do not put the 5.8G VTX underwater.
- If the buoy/cable proves troublesome, the fallback is a thin shore tether or a smaller antenna float.
