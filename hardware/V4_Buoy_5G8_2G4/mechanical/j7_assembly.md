# J7 and cable assembly envelopes

Status: **TBD / envelope models only / not physical fit-tested.**
The previous model that put the 26 x 46 mm G030 board inside the 55 x 70 mm buoy was wrong and has been removed.

## 1. Connector set

| Item | Part | Check |
|---|---|---|
| Shark board header | JST `B6B-PH-K-S` | PH 2.0 mm, 6 pins, 2 A at AWG24 |
| Cable housing | JST `PHR-6` | 6 circuits |
| Crimp terminal | JST `SPH-002T-P0.5S` | AWG30-24, insulation OD 0.9-1.5 mm |

The actual 24AWG insulation OD and crimp pull test are required. A 24AWG wire with an OD outside 0.9-1.5 mm is not supported.

## 2. Shark side

Model: `j7_shark_assembly.scad` / `j7_shark_assembly.png`

- G030 PCB envelope: **26 x 46 mm** (TBD until layout).
- J7: JST PH 6P, mated body about 13.9 x 4.5 x 8.0 mm.
- Cable: 5.5 mm OD, 30 mm static bend.
- Sharks enclosure: 35 mm ID x 120 mm length envelope (TBD; actual hull not frozen).
- Waterproof entry: rear/top gland, 10 mm class; cable service loop and separate strain relief.
- The cable must not carry tow load; J7 must not be the strain relief.

The model is an interference envelope, not a manufacturing drawing. The actual hull, gland, cable jacket and connector orientation are still TBD.

## 3. Buoy side

Model: `j7_buoy_assembly.scad` / `j7_buoy_assembly.png`

- F407 PCB envelope: **30 x 30 mm** (TBD).
- Buoy shell: **55 mm diameter x 70 mm** envelope (TBD).
- Mating 6-pin cable connector at the bottom entry, separate from the shark-side J7.
- 5.8G VTX: about 25 x 25 x 5 mm, separate module.
- 2.4G receiver/antenna and 5.8G cloverleaf on opposite sides; at least 5 cm apart.
- Cable: 5.5 mm OD, 30 mm static bend; bottom gland with service loop.
- Foam/keel/mast and positive buoyancy remain TBD.

Do not reuse the shark-side connector envelope or cable path for the buoy. The two sides have different PCBs, shells, glands and cable entries.

## 4. Cable

- 50 cm test length.
- Two 24AWG power/GND, two 28AWG UART, one 75 ohm micro coax, shield/filler/jacket.
- Finished OD about **5.0-5.5 mm**, not 3 mm.
- Static bend about 30 mm; repeated flex/tow bend about 55 mm.
- 24AWG loop resistance ~0.084 ohm/50 cm, ~0.08 V at 1 A, ~0.17 V at 2 A.
- Use a Kevlar/string strength member; potted/glanded entries; strain relief at both ends.

## 5. Conclusion

- Connector family: JST PH is a reasonable candidate.
- Shark side and buoy side are modeled separately.
- Board outlines, hull dimensions, gland and cable are **TBD**; do not freeze until a physical mock-up and cable sample are checked.
- No claim of waterproofing, fit or strain relief is made.
