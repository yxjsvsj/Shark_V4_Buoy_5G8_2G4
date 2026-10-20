# G030 power budget and component review

Status: **calculated only; no hardware measurement yet.**
Do not mark the 5V rail, Q1, L1, C1-C3 or servo supply as verified until the tests in this document are run.

## 1. Assumptions

- Battery: protected 1S, 3.0 V minimum, 4.2 V maximum.
- Boost: MT3608, 1.2 MHz, 22 uH, 5.0 V output.
- Efficiency used for the table: **85%** at 3.0 V input. This is a planning assumption, not a measured value.
- MT3608 datasheet: `thetaJA = 250 C/W`, `PD(max) = 0.6 W`, `TJ(max) = 160 C` (thermal shutdown typ 155 C).
- Ambient used for the junction estimate: **40 C** inside the sealed shark. A 25 C estimate is also shown for reference.
- Duty cycle `D = 1 - Vin/Vout = 0.4`.
- Inductor ripple `dIL = Vin * D / (f * L) = 3.0 * 0.4 / (1.2e6 * 22e-6) = 0.045 A`.

## 2. MT3608 at 3.0 V input

| 5 V load | Pout | Pin at 85% | Input current | Inductor peak | Loss in MT3608 | TJ at 40 C ambient | TJ at 25 C ambient |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.40 A | 2.00 W | 2.35 W | 0.784 A | 0.807 A | 0.353 W | **128 C** | 113 C |
| 0.72 A | 3.60 W | 4.24 W | 1.412 A | 1.434 A | 0.635 W | **199 C** | 184 C |
| 1.00 A | 5.00 W | 5.88 W | 1.961 A | 1.984 A | 0.882 W | **261 C** | 246 C |

At 40 C ambient, the maximum loss that keeps `TJ <= 160 C` is:

`(160 - 40) / 250 = 0.48 W`

At 85% efficiency, that corresponds to:

`Pout = 0.48 * 0.85 / 0.15 = 2.72 W`, or about **0.54 A at 5 V**.

**Conclusion:** the MT3608 SOT-23-6 is **not thermally viable at 0.72 A or 1.0 A from 3.0 V**, even before adding margin for a sealed enclosure. The 0.40 A case is the only table point below the absolute junction limit, and it still reaches about 128 C at 40 C ambient. The 0.72 A nominal load is already above the package dissipation rating (0.635 W > 0.6 W).

This is a **P0 blocker** for the current 5 V architecture. Options, to be chosen before layout:

1. Replace MT3608 with a larger boost with a real thermal pad and specified efficiency at 3 V/1 A (not yet selected).
2. Reduce the 5 V load to a measured maximum below about 0.4 A and move the servo to a separate supply.
3. Use a boost module with a much larger copper area and verify case temperature; a bare SOT-23-6 is not enough.
4. Use a 2S battery and a different power tree; this is an architecture change.

Do not claim “MT3608 5V/1A” as a completed design.

## 3. Inductor

Required at 3.0 V/1 A:

- Average input current: 1.96 A.
- Peak: about 1.98 A with 22 uH at 1.2 MHz.
- Recommended part: **Bourns SRP6060FA-220M**, 22 uH, 6.6 x 6.4 mm, DCR 55 mohm max, Isat 5.6 A, Irms 3.8 A.
- LCSC `C2045802` was out of stock at review time; verify Mouser/DigiKey/LCSC before ordering.
- A 6 x 6 mm 22 uH part with only 1.8 A rating / 2.2 A saturation (for example SWPA6045S220MT) is **not sufficient** for the 1 A case.

Even with the correct inductor, the MT3608 package thermal limit above still applies.

## 4. Diode and capacitors

- D1 SS34: 3 A average, 40 V; output current is 0.4-1.0 A. Verify temperature at 1 A; the diode loss is not included separately in the 85% assumption.
- C7/C8: **22 uF, 25 V, 0805 X5R**, `CL21A226MAYNNNE` (`C602037`). The 25 V rating reduces DC-bias loss at 5 V; effective capacitance is still lower than nominal and must be measured.
- C9: 1 uF, 25 V, 0603 X7R, `CL10B105KA8NNNC` (`C29936`) at the TLV70033 output.
- C15: same 1 uF part at the TLV70033 input.
- C16/C17: 100 nF, 50 V, 0402 X7R, `GRM155R71H104KE14D` (`C77020`) at the camera and buoy connectors.
- C10/C12/C13/C14/C4-C6: same 100 nF part.

## 5. C1/C2/C3 motor decoupling

The original “100 uF / 0805” requirement is not credible as a guaranteed 100 uF at 4.2 V. A 100 uF 0805 X5R such as `GRM21BR60J107ME15L` is a real part, but its effective capacitance falls sharply with DC bias; the marked value must not be used as the effective value.

Selected replacement:

- **KEMET T520A107M006ATE070** (`C561794`), 100 uF, 6.3 V polymer tantalum, 1206/3216, ESR 70 mohm max.
- Ripple current: 1.035 A rms at 45 C, 724.5 mA rms at 85 C, 258.75 mA at 105 C (100 kHz).
- Capacitance is stable with DC bias, unlike the 0805 X5R.
- Add the existing 100 nF C4/C5/C6 in parallel.
- The 6.3 V rating gives 1.5x margin over 4.2 V. Do not operate above 4.2 V.
- Estimate motor ripple current and verify capacitor case temperature at 20 kHz PWM; the 100 kHz rating is a reference, not a 20 kHz guarantee.

If the 1206 polymer part is not acceptable mechanically, the alternative is a 1206/1210 100 uF X5R with measured effective capacitance, or two smaller ceramics in parallel. Do not keep an 0805 100 uF part without a bias measurement.

## 6. Servo and 5 V headroom

The servo model and stall current are not fixed. The current nominal budget is:

`camera 0.10 + buoy 0.40 + LDO 0.02 = 0.52 A` before the servo.

| Servo current | Total 5 V | MT3608 1 A rating | MT3608 thermal at 3.0 V/40 C |
|---:|---:|---|---|
| 0.20 A running | 0.72 A | within 1 A | **fails** (~199 C) |
| 0.50 A | 1.02 A | exceeds | fails |
| 1.00 A | 1.52 A | exceeds | fails |
| 1.50 A | 2.02 A | exceeds | fails |

**Do not mark the 5V supply capable.** The servo stall current must be measured, and the 5V source must be resized or split before the schematic is frozen. The camera/buoy/servo loads also need a startup/transient test.

## 7. Q1 high-temperature conduction

- Q1: SiSS23DN-T1-GE3, 6.3 mohm max at VGS = -2.5 V.
- Budget with all three MX113H at 1 A and 5V/1A input: 4.96 A continuous; 6.46 A peak.
- Use a 1.4x RDS(on) multiplier at high junction temperature as a conservative estimate.
- At 6.5 A: `P = 6.5^2 * 0.0063 * 1.4 = 0.372 W`.
- With the datasheet steady-state `RthJA = 63 C/W`: rise about 23 C; at 40 C ambient, TJ about 63 C. With a poorer 100 C/W layout, TJ about 77 C.
- This is acceptable only with short/widened VBAT/VMOTOR copper and thermal vias under the PowerPAK 1212-8S exposed drain pad. The land pattern must be created/verified in JLCEDA; the schematic candidate does not prove it.

## 8. LDO and local decoupling

- TLV70033 requires a 1 uF ceramic output capacitor; C9 is 1 uF.
- C15 adds 1 uF at the input. C10 100 nF and C11 4.7 uF are at the G030 VDD/VDDA pin.
- C16/C17 add 100 nF at the camera and buoy connectors.
- The buoy-end 100 uF + 100 nF and optional ferrite/LC filter remain off-board and must be placed at the buoy cable entry.
- Keep the boost inductor/diode and motor PWM away from the CVBS path; use a separate video return and shield.

## 9. Required measurements

1. MT3608 case temperature and 5 V ripple at 3.0 V input, 0.4/0.72/1.0 A, in the sealed enclosure.
2. L1 temperature and saturation check at 3.0 V/1 A; current waveform if possible.
3. Q1 case temperature at 6.5 A peak and at the measured motor running current.
4. C1-C3 case temperature/ripple at 20 kHz; effective capacitance if a ceramic alternative is used.
5. Servo model, running current, startup peak and stall current; 5 V transient at the servo connector.
6. J7 voltage drop and connector temperature at the measured 5 V load.
7. Camera/buoy input ripple with the cable and filters installed.

Until these are recorded, the power tree is **calculated, not validated**.
