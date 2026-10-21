# Round 7 buoy and J7 interface review

Date: 2026-10-21. Baseline: `62098cf`.

Status: **5 m CABLE NOT DESIGNED / PP POLARITY BLOCKED / VIDEO CHAIN INDEPENDENT / J7 NOT MULT-BUS.**

## 1. Current J7 map

| J7 pin | Net | Direction / function | RevB status |
|---|---|---|---|
| 1 | +5V | buoy power | present |
| 2 | GND | power return | present |
| 3 | CVBS_VIDEO | camera video to buoy VTX | present |
| 4 | GND | video return, tied to board GND | present |
| 5 | PP_DOWN | buoy/receiver to Shark G030 | present; R8 22 ohm to U1.10 / USART2_RX |
| 6 | TELEM_UP | Shark G030 to buoy | present; U1.9 / USART2_TX |

J7 is a **custom Shark buoy link**, not the LimeRC GH1.25 Mult-Bus connector. Do not describe J7 as a LimeRC connector. The LimeRC receiver's own Mult-Bus is a 6-pin GH1.25 with VBUS/GND and UART1TX/UART2RX.

## 2. PP and telemetry

Verified from LimeRC source and schematic:

- PP output is UART1TX through a 74LVC1G86 XOR and then the Mult-Bus connector.
- Format: 115200-8-N-1, `pp<ch0>,<ch1>,<ch2>,<ch3>,<left>,<right>,\r\n`.
- Boot default: inverted and output-disabled; the user must set PP + normal TTL (or use an inverter).
- Loss: after >100 ms, one neutral frame with all channels 2048, then output stops.
- UART2RX on the receiver is the opposite-direction input; it is not the PP output.

Shark requirement:

- The buoy F407 must explicitly set the LimeRC receiver to **normal TTL**, or invert in hardware/software.
- Capture the actual UART with a scope/logic analyzer before freezing `PP_DOWN` polarity.
- G030 should reject non-`pp` frames, malformed fields, and values outside 0-4095.
- 500 ms no valid frame -> motors 0, jaw open.
- Add series resistors and TVS on both `PP_DOWN` and `TELEM_UP` at the cable entry. R8 is only on PP today.

## 3. Video

- LimeRC video is **OV2640/DCMI, digital over nRF24**; the receiver has no CVBS output.
- Shark's J6/J7 CVBS is a separate camera + 5.8 GHz VTX chain. That is allowed, but it is not LimeRC video and its compatibility is unverified.
- Use a 75 ohm coax or controlled 75 ohm pair for CVBS; terminate at the VTX input if it is high impedance. Check the actual VTX input termination.
- Keep CVBS away from motor PWM and the boost inductor. Ground the shield at one end only; do not create a ground loop through J7 pin 4.

## 4. Five-metre cable calculation

Use a design length of **8-10 m**, not 0.5 m: 5 m depth + surface float + service loop + movement margin.

Copper resistance:

| Conductor | ohm/m | 10 m loop (20 m total) | Drop at 0.72 A | Drop at 1 A | Drop at 2 A |
|---|---:|---:|---:|---:|---:|
| 24 AWG | 0.0842 | 1.68 ohm | 1.21 V | 1.68 V | 3.36 V |
| 20 AWG | 0.0333 | 0.67 ohm | 0.48 V | 0.67 V | 1.34 V |
| 18 AWG | 0.0209 | 0.42 ohm | 0.30 V | 0.42 V | 0.84 V |

The existing 24 AWG + JST-PH plan is not acceptable for 5 m power. At 0.72 A it already drops >1 V in a 10 m loop; the buoy 5 V rail may fall below the receiver/VTX minimum.

Proposed cable:

- 2 x 18 AWG for +5V/GND, or a separate 2-pin IP68 bulkhead power connector.
- 2 x 24-26 AWG twisted pair for PP/TELEM, with series resistors/TVS.
- 75 ohm micro coax for CVBS plus shield.
- Overall jacket, strain member, and water-blocking; cable must not carry tow load.
- Use an IP68 bulkhead/gland and a separate strain relief. J7 inside the hull is not the water seal.

The exact connector is **TBD**. A 2 A JST-PH cannot accept 18 AWG and is not a 5 m power connector. Use an XT30/XT60-class power pair or a properly rated circular IP68 connector, plus a separate signal/video connector. Do not claim a connector until its contact size, current rating, sealing and bend radius are checked.

## 5. Mechanical and buoyancy

- 24AWG/28AWG 5.5 mm cable is for the shallow prototype. A 5 m cable with 18AWG power and coax will be larger and heavier.
- Estimate cable mass, displaced volume and drag before choosing float size. A neutrally buoyant cable reduces the shark's pitch/roll disturbance.
- The cable must have a service loop at both ends; the shark's motion must not load J7 or the gland.
- Positive buoyancy target ~2% of all-up mass. The cable and buoy pull must be included in the tank test.
- No 5 m pressure or cable test has been performed.

## 6. Blockers

- PP normal/inverted configuration not captured.
- Actual LimeRC Mult-Bus pin mapping not continuity-checked.
- CVBS/VTX 75 ohm termination not verified.
- 5 m cable, connector, gland and strain relief not selected.
- No cable drop/ripple measurement at 0.72/1/1.5 A.
- No watertight assembly or 5 m/7.5 m pressure test.
