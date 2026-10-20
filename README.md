# Shark V4 Buoy 5.8G / 2.4G

Fully submerged 10-15 cm freshwater shark with a small surface buoy.
The shark tows a 50 cm cable to the buoy; all RF stays above water.

## Architecture

```
Shark (fully submerged)
  camera CVBS + G030 + 3 thrusters + jaw + protected 1S + 5V boost
        |
        | 50 cm, 6-core cable:
        | +5V_BUOY, GND_PWR, CVBS_VIDEO, GND_VIDEO, PP_DOWN, TELEM_UP
        v
Buoy (surface)
  5.8G 25mW VTX + cloverleaf
  2.4G LimeCam receiver + 31 mm antenna
        |
        | 5.8G air                    | 2.4G air
        v                             v
  5.8G receiver + monitor       LimeRC remote
```

- Video: underwater CVBS camera -> cable -> 5.8G VTX on buoy -> receiver at tank edge.
- Control: LimeRC remote -> 2.4G receiver on buoy -> `pp` -> cable -> G030.
- No IR, no 433M, no 1.2G. The only underwater link is the 50 cm cable.

## Contents

| Path | What |
|---|---|
| `hardware/f407_buoy/` | JLCEDA Pro project for the buoy F407 receiver board (copy of V3). Open `Shark_V4_Buoy_F407_RevA.eprj3`. |
| `hardware/V4_Buoy_5G8_2G4/` | System, two-board plan, buoy RF, G030 control, keep/remove, mechanical, test, BOM, design review. |

## Status

- No PCB has been fabricated.
- The F407 project is a **copy of the V3 project**, not build-ready. It still contains the V3 camera/NRF1 pages.
- **P0 gate:** LimeRC receiver source/license, clock (24 vs 25 MHz), pairing, PP polarity. If only HEX is available, use the original LimeCam board or get source/permission.
- **P0 gate:** measure thruster current/stall and MX113H thermal before layout.
- Board sizes are not frozen: first-pass G030 26x40-46 mm, buoy 30x30-30x35 mm.
- First milestone: 5.8G video + 2.4G `pp` + 50 cm cable test in the tank.
- Do not draw/fabricate the final PCBs until the gates pass.

## Next steps

1. Resolve LimeRC receiver source/license/clock/pin/PP polarity.
2. Measure thruster current/thrust and MX113H thermal.
3. Buy the 5.8G VTX, receiver, CVBS camera, antennas, buoy materials, 50 cm cable; run the tank test.
4. Finish the G030 schematic, then the F407 schematic; layout before freezing sizes.
5. If a link fails, use 900M analog or a thin tether; do not return to 2.4G/5.8G underwater RF.

## Design review

See `hardware/V4_Buoy_5G8_2G4/design_review.md` for the P0/P1 gates and the final V1 selection (F407 buoy + G030 brushed).

## Notes

- The F407 project is based on the author's `Shark_V3_SingleMCU_RevA`; see `hardware/f407_buoy/V3_REFERENCE.md`.
- Check the LimeRC/OpenROV licenses before redistribution or commercial use.
- The buoy is a short-tether semi-wireless design, not a fully wireless submarine.
