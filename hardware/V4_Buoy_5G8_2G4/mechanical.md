# V4 buoy mechanical notes

## 1. Buoy envelope

- Shell: 55 mm diameter x 70 mm tall, PETG, 1.5 mm wall.
- Screw lid with O-ring; internal electronics tray.
- Foam inside for reserve buoyancy; 10-15 g keel at the bottom.
- 5.8G cloverleaf on a 20 mm mast; 2.4G 31 mm wire on the opposite side.
- Cable exits the bottom through a waterproof gland.
- Tow loop above the gland takes the cable strain; the cable is not the strength member.

Target: 50-80 g buoy, displacement ~150 cm3, positive buoyancy with the 0.8-1.2 m cable and antennas. Maximum design depth: 0.5 m.

## 2. Cable

- 100 cm nominal (80-120 cm), 6 cores: **24AWG for +5V/GND_PWR**, 28AWG for signals, separate shielded video pair/coax. This is the 0.5 m-depth baseline; 50 cm is too short.
- Connector: **JST-PH 6P, 2.0mm, 2A at 24AWG, 24-30AWG** (proposed; series change pending confirmation). JST-SH is only 1A/28-32AWG and cannot take 24AWG.
- Current check: +5V rail ~0.72A nominal; verify at full load including servo stall. 24AWG drop over a 1 m cable is ~0.12V at 0.72A, ~0.17V at 1A and ~0.34V at 2A (10 m loop is not applicable here). J7 and cable must be rated for the sum of buoy + camera + servo.
- Cable OD is **~5.0-5.5mm**, not 3mm. A 5.5mm cable needs about 30mm static / 55mm dynamic bend radius. The connector and bend are tight in a 55mm buoy; see `mechanical/j7_assembly.md`.
- Pins: 1=+5V (cable label +5V_BUOY), 2=GND_PWR, 3=CVBS_VIDEO, 4=GND_VIDEO, 5=PP_DOWN (buoy->shark), 6=TELEM_UP (shark->buoy).
- Kevlar/string strength member inside the jacket; CVBS is 75 ohm; check VTX input termination.
- Loop/strain relief at both ends; do not pull on the solder joints.
- Neutral buoyancy: add a small foam bead or use a thin cable; the buoy must not be pulled under.

## 3. Buoy internals

```
        [5.8G cloverleaf]        [2.4G 31mm wire]
              |                        |
        +-----+------------------------+-----+
        |  5.8G VTX        LimeCam receiver  |
        |  5V filter       (camera disabled) |
        |                                    |
        |   foam        keel 10-15g          |
        +----------------+-------------------+
                         |
                    cable gland
                         |
                    100cm cable
                         |
                      shark
```

- Keep the 5.8G VTX and its antenna away from the 2.4G receiver/antenna (>=5 cm).
- Put the 5V filter and 100uF at the cable entry.
- The LimeCam camera can be removed/disabled; only the 2.4G receiver + `pp` output are used.
- If the LimeCam board is too large, use a small 2.4G receiver + MCU on a 30x30 perfboard.

## 4. Shark cable entry

- Camera in the nose; 3-wire shielded video/5V/GND to the buoy.
- UART TX/RX for `pp`; 5V/GND; spare.
- Waterproof gland or potted cable exit at the top/back.
- Cable exits above the center of gravity; keep a slack loop so the shark can turn.
- The shark tows the buoy; the buoy stays on the surface; the cable length is 0.8-1.2 m (1 m nominal).

## 5. Buoyancy and trim

- Buoy: positive buoyancy; with 50-80 g electronics, use ~100-150 cm3 foam/air.
- Keel: 10-15 g at the bottom; antenna mast adds windage but not much weight.
- If the buoy flips, add keel or a small drop keel; keep the antennas vertical.
- Shark: **slightly positive buoyancy**; the vertical thruster holds depth; on power/control loss it must surface naturally. The buoy cable adds a small upward pull.
- Test in the tank before installing electronics: float, tilt, cable pull; then verify power-off surfacing with the complete shark.

## 6. Sealing

- Buoy is above water; splash/condensation only. A screw lid + O-ring is enough.
- Cable gland is the main water path; use a proper gland + silicone; strain relief.
- Shark hull is fully submerged; use the existing O-ring hull and a potted/gland cable entry.
- Leak test the empty buoy and the shark hull separately before power.

## 7. Antennas

- 5.8G cloverleaf: vertical, on the mast, above the buoy shell.
- 2.4G 31 mm wire: vertical, opposite side; at least 5 cm from the 5.8G antenna.
- Do not coil the 2.4G wire around the 5.8G mast.
- The tank-edge 5.8G receiver antenna should be vertical and line-of-sight to the buoy.
