# Shark V4 Buoy 5.8G / 2.4G

Fully submerged 10-15 cm freshwater shark with a small surface buoy.
The shark tows a 50 cm cable to the buoy; all RF stays above water.

## Architecture

```
Shark (fully submerged)
  camera CVBS + G030 + 3 thrusters + jaw + 1S + 5V boost
        |
        | 50 cm, 6-core shielded cable:
        | 5V, GND, VIDEO, UART_TX, UART_RX, spare
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
| `hardware/f407_buoy/` | JLCEDA Pro project for the buoy F407 receiver board (copy of V3 as a starting point). Open `Shark_V4_Buoy_F407_RevA.eprj3`. |
| `hardware/sub_g030/` | Design docs for the shark G030 control board. The JLCEDA G030 project still needs to be created. |
| `docs/system.md` | Full buoy system plan, dimensions, cost, success. |
| `docs/two_board_plan.md` | Two-board redesign plan. |
| `docs/buoy_rf_board.md` | Stripped LimeCam F407 buoy board. |
| `docs/keep_remove.md` | What to keep/remove from the open-source boards. |
| `docs/mechanical.md` | Buoy dimensions, cable, sealing. |
| `docs/test_plan.md` | Tank test plan. |
| `docs/bom.csv` | Buoy and tank-edge BOM. |

## Status

- No PCB has been fabricated.
- The F407 project is a **copy of the V3 project**, not build-ready. It still contains the V3 camera/NRF1 pages; remove them per `docs/buoy_rf_board.md`.
- The G030 control board is documented but not yet a JLCEDA project.
- First milestone: 5.8G video + 2.4G `pp` + 50 cm cable test in the tank.
- Do not draw/fabricate the final PCBs until the buoy links pass.

## Next steps

1. Buy the 5.8G VTX, 5.8G receiver, CVBS camera, antennas, buoy materials, 50 cm cable.
2. Run the tests in `docs/test_plan.md`.
3. If pass, finish the F407 buoy board and create the G030 sub board.
4. If fail, fall back to 900M analog or a thin tether; do not return to 2.4G/5.8G underwater RF.

## Notes

- The F407 project is based on the author's `Shark_V3_SingleMCU_RevA`; see `hardware/f407_buoy/V3_REFERENCE.md`.
- Check the LimeRC/OpenROV licenses before redistribution or commercial use.
- The buoy is a short-tether semi-wireless design, not a fully wireless submarine.
