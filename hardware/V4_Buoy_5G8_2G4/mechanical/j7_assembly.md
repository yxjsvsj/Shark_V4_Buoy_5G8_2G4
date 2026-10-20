# J7 connector and cable mechanical check

Status: **envelope model only; not a manufacturer STEP assembly; no physical fit test.**
J7 remains **PENDING CONFIRMATION**.

## 1. Connector set

| Item | Part | Check |
|---|---|---|
| Board header | JST `B6B-PH-K-S` | PH 2.0 mm, 6 circuits, top entry, through-hole |
| Wire housing | JST `PHR-6` | 6 circuits, 13.8 mm class body |
| Crimp terminal | JST `SPH-002T-P0.5S` | AWG 30-24, insulation OD 0.9-1.5 mm |

The three parts are from the same PH series and are intended to mate. The header is 2 A rated at AWG24, 100 V, -25 to +85 C. The terminal accepts 24AWG only if the actual wire insulation OD is between 0.9 and 1.5 mm. A 24AWG wire with a thicker insulation jacket will not crimp correctly.

Required incoming inspection:

- Measure the actual 24AWG insulation OD.
- Crimp pull test per the terminal tooling specification.
- Verify the housing fully latches into the header.
- Verify the header pin 1 orientation against the PCB silkscreen.

## 2. Mated envelope

Use these conservative envelope dimensions:

| Feature | Dimension |
|---|---|
| Header/housing length | 13.9 mm |
| Header/housing width | 4.5 mm |
| Mated height above PCB | 8.0 mm |
| Pin pitch | 2.0 mm |
| Recommended clearance around body | >=2 mm |

The OpenSCAD model in this directory uses a 13.9 x 4.5 x 8.0 mm mated envelope, a 26 x 46 mm board, a 5.5 mm cable and a 30 mm static bend radius. It is an **envelope/interference model**, not the JST STEP file.

Files:

- `j7_assembly.scad` - parametric envelope model.
- `j7_assembly.stl` - exported envelope mesh (with buoy shell).
- `j7_assembly_connector.stl` - connector/cable-only mesh.
- `j7_assembly_connector.png` - connector/cable view.
- `j7_assembly.png` - view inside the 55 x 70 mm buoy envelope.

## 3. Cable diameter

The previous “3 mm OD” assumption is not credible for this conductor set.

A representative build:

| Conductor | Size | Insulation OD | Approx. area |
|---|---|---|---|
| +5V | 24AWG | 1.2 mm | 1.13 mm2 |
| GND_PWR | 24AWG | 1.2 mm | 1.13 mm2 |
| PP_DOWN | 28AWG | 0.7 mm | 0.38 mm2 |
| TELEM_UP | 28AWG | 0.7 mm | 0.38 mm2 |
| CVBS | 75 ohm micro coax | 1.9 mm | 2.84 mm2 |

Conductor bundle area is about 5.9 mm2 before fillers, shield, wrap and jacket. With a realistic fill factor and a 0.5-0.8 mm jacket, the finished cable is approximately **5.0-5.5 mm OD**, not 3 mm. A 3 mm jacket cannot contain two 24AWG power wires plus the shielded video channel with usable insulation and strain relief.

If a 3 mm cable is mandatory, the architecture must change: thinner power wire (not acceptable at 1-2 A), a separate video coax, or a different connector/ cable construction. Do not claim 3 mm without a cable sample and cross-section.

## 4. Bend radius and buoy fit

For a 5.5 mm cable:

- Static installation bend radius: about 5x OD = **27.5 mm**.
- Repeated flexing/towing: about 10x OD = **55 mm**.

The model uses a 30 mm static bend. The cable exits the top-entry connector, rises about 10 mm, turns through 30 mm radius, and then runs horizontally. That already needs roughly 48 mm of vertical space above the PCB, before the service loop and gland.

The buoy is 55 mm diameter x 70 mm tall. A top-entry `B6B-PH-K-S` with a 30 mm bend is **tight**; the cable may foul the lid or the battery/electronics. A right-angle `S6B-PH-K-S` header, a larger buoy, or a different cable exit is likely needed. This is not frozen.

Do not assume the connector plus a 30-55 mm bend fits until a physical print and cable sample are checked.

## 5. Waterproof entry

- The cable must pass through a proper gland or potted entry, not through a bare hole.
- A tow loop/strength member must take the pull; the JST contacts must not take tow load.
- Keep a service loop inside the buoy; do not bend the cable at the crimp.
- The gland, boot and connector envelope need a 3D printed mock-up before the PCB outline is frozen.
- Strain relief must be separate from the JST latch.

## 6. Conclusion

- Connector family: **JST-PH 6P is still the candidate**; B6B + PHR-6 + SPH-002T-P0.5S are a valid family match.
- 24AWG: **conditional**; insulation OD must be 0.9-1.5 mm and the crimp must pass a pull test.
- Cable OD: **5.0-5.5 mm estimated**, not 3 mm.
- Bend: **30 mm static / 55 mm dynamic**, which is large relative to the 55 mm buoy.
- Mechanical fit: **PENDING**; top-entry plus 30 mm bend is tight.
- J7/PCB freeze: **do not freeze** until a physical connector/cable/gland mock-up is checked.
