# G030 power budget and MT3608 loss analysis

Status: **CALCULATED / NOT VALIDATED / MT3608 REMAINS BLOCKED.**
No 5V load test has been run. Do not mark the 5V rail passed or failed from this document alone.

## 1. Assumptions and what changed

The earlier version treated **all** converter loss as MT3608 chip loss. That was wrong. The converter loss is split here into:

- SS34 diode conduction loss,
- L1 winding loss,
- estimated L1 core loss,
- MT3608 internal MOSFET conduction loss,
- MT3608 switching loss,
- gate-drive and quiescent loss.

The MT3608 junction temperature is calculated only from the losses physically attributed to the MT3608 package.

Inputs:

- Vin = 3.0 V (minimum 1S), Vout = 5.0 V.
- fsw = 1.2 MHz, L = 22 uH, D = 1 - Vin/Vout = 0.4.
- Inductor ripple `dIL = Vin*D/(fsw*L) = 0.045 A`.
- L1: Bourns SRP6060FA-220M, DCR = 55 mohm max.
- D1: SS34, Vf assumed 0.40 V at 0.4 A, 0.45 V at 0.72 A, 0.50 V at 1 A; sensitivity 0.35-0.55 V.
- MT3608 switch: RDS(on) 80 mohm typ, 150 mohm max at 25 C; hot multiplier 1.4 for the max case.
- Switch rise+fall time: 20 ns typ, 60 ns max (datasheet does not provide this directly).
- Gate charge estimate: 5-15 nC (not a datasheet guarantee).
- Quiescent/control: 1.6-2.2 mA at Vin.
- MT3608 thetaJA = 250 C/W (datasheet, JEDEC-like board). This is not a guarantee for the sealed shark PCB.
- Ambient used for junction estimate: 40 C; sealed-case sensitivity also shown.

## 2. Bottom-up loss calculation at 3.0 V input

### 2.1 Switch current

Boost switch RMS current is approximated by:

`Isw_rms = Iin * sqrt(D)`

| Load | Iin at 85% | Isw_rms |
|---:|---:|---:|
| 0.40 A | 0.784 A | 0.496 A |
| 0.72 A | 1.412 A | 0.893 A |
| 1.00 A | 1.961 A | 1.240 A |

### 2.2 Loss table

| Load | Pout | Diode loss | L1 DCR loss | L1 core loss (est.) | MT3608 conduction typ/max | MT3608 switching typ/max | Gate + quiescent | MT3608 total typ/max | Converter total typ/max | Efficiency typ/max |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.40 A | 2.00 W | 0.160 W | 0.034 W | 0.040 W | 0.020 / 0.052 W | 0.047 / 0.071 W | 0.024 W | **0.091 / 0.183 W** | **0.325 / 0.417 W** | **86.0 / 82.7%** |
| 0.72 A | 3.60 W | 0.324 W | 0.110 W | 0.060 W | 0.064 / 0.168 W | 0.085 / 0.127 W | 0.024 W | **0.173 / 0.355 W** | **0.667 / 0.849 W** | **84.4 / 80.9%** |
| 1.00 A | 5.00 W | 0.500 W | 0.211 W | 0.080 W | 0.123 / 0.323 W | 0.118 / 0.177 W | 0.024 W | **0.265 / 0.560 W** | **1.056 / 1.351 W** | **82.6 / 78.7%** |

The core-loss number is an **estimate**, not a vendor core-loss calculation: the SRP6060FA-220M core-loss curve is not in the basic datasheet. Treat 0.04/0.06/0.08 W as a placeholder and measure inductor temperature.

### 2.3 MT3608 junction estimate

Using only the MT3608-attributed loss:

`TJ = Tamb + Pchip * thetaJA`

| Load | Pchip typ/max | TJ rise typ/max at 250 C/W | TJ at 40 C | TJ at 60 C |
|---:|---:|---:|---:|---:|
| 0.40 A | 0.091 / 0.183 W | 23 / 46 C | 63 / 86 C | 83 / 106 C |
| 0.72 A | 0.173 / 0.355 W | 43 / 89 C | 83 / 129 C | 103 / 149 C |
| 1.00 A | 0.265 / 0.560 W | 66 / 140 C | **106 / 180 C** | **126 / 200 C** |

At 1 A the **maximum-loss** case exceeds the 150 C junction limit; the typical-loss case is about 106 C. This is a real uncertainty, not a proven failure. At 0.72 A the max case is close to the limit. At 0.4 A the estimate is below the limit but still depends on copper and ambient.

## 3. Top-down cross-check

If the whole converter is assumed to be 85% efficient, total loss is:

| Load | Total loss at 85% | Residual after diode + L1 DCR + core | Comment |
|---:|---:|---:|---|
| 0.40 A | 0.353 W | 0.119 W | plausible |
| 0.72 A | 0.635 W | 0.141 W | lower than bottom-up chip estimate |
| 1.00 A | 0.882 W | 0.091 W | **not self-consistent** with bottom-up 0.265 W typical |

The 85% assumption is therefore optimistic at 1 A. The bottom-up estimate implies roughly 79-83% at 1 A, 81-84% at 0.72 A and 83-86% at 0.4 A. Measure efficiency rather than assuming 85%.

## 4. Sensitivity

| Parameter | Range | Effect |
|---|---|---|
| SS34 Vf | 0.35-0.55 V | 0.14-0.55 W diode loss; at 1 A a 0.1 V change is 0.1 W |
| L1 DCR | 55-116 mohm | 0.03-0.45 W at 1.4-2.0 A |
| Core loss | 0.03-0.15 W | changes converter efficiency and local heating |
| MT3608 RDS(on) | 80-150 mohm, x1.4 hot | chip conduction 0.05-0.32 W at 1 A |
| Switching time | 20-60 ns total | chip switching 0.05-0.18 W at 1 A |
| Gate charge | 5-15 nC | 0.018-0.054 W |
| thetaJA | 150-250 C/W with copper | TJ can change by tens of degrees |
| Ambient | 40-60 C sealed | TJ rises directly with ambient |

## 5. Conclusion

- **MT3608 is BLOCKED, not approved and not declared impossible.** The corrected analysis no longer supports the earlier 128/199/261 C “chip junction” numbers; those were total-converter losses.
- The corrected estimate is roughly 63-86 C at 0.4 A, 83-129 C at 0.72 A, and 106-180 C at 1 A (40 C ambient, 250 C/W), with the 1 A maximum case over the junction limit.
- The result depends strongly on RDS(on) hot, switching time, inductor/core loss, copper area, sealed-case ambient, and actual efficiency.
- Required before a decision: 3.0 V input, 0.4/0.72/1.0 A load; measure Vin, Iin, Vout, efficiency, MT3608 case temperature, L1 temperature, SS34 temperature, and 5 V ripple in the sealed enclosure. Do not use typical curves as guaranteed whole-product values.
- If the measured 1 A case is too hot, select a larger boost with a datasheet thermal pad/thetaJA and specified efficiency; no alternative is approved in this document yet.

## 6. Servo and 5 V headroom

The servo model and stall current are still unspecified. Other 5 V load is camera 0.10 A + buoy 0.40 A + LDO 0.02 A = 0.52 A.

| Servo current | Total 5 V | Result |
|---:|---:|---|
| 0.20 A running | 0.72 A | at the uncertain MT3608 0.72 A point |
| 0.50 A | 1.02 A | exceeds 1 A rating |
| 1.00 A | 1.52 A | exceeds 1 A |
| 1.50 A | 2.02 A | exceeds 1 A |

Do not mark the 5V rail capable. Measure servo stall and transient; use a larger boost, split rail, or load limit if needed.

## 7. Other loads

- C1-C3: 100 uF 6.3 V polymer tantalum 1206 (T520A107M006ATE070); stable at 4.2 V, but ripple/temperature at 20 kHz must be measured.
- Q1: SiSS23DN, 6.3 mohm max at -2.5 V; ~0.37 W at 6.5 A peak with 1.4x hot RDS(on); copper/thermal not verified.
- L1: SRP6060FA-220M, 22 uH, Isat 5.6 A, Irms 3.8 A, DCR 55 mohm.
- D1: SS34, 3 A/40 V.
- C7/C8: 22 uF 25 V 0805 X5R; effective capacitance at 5 V must be measured.
- TLV70033: 1 uF input C15, 1 uF output C9.

## 8. Required measurements

1. MT3608 case/ambient and 5V ripple at 3.0 V, 0.4/0.72/1.0 A, sealed enclosure.
2. Efficiency at each point; inductor and diode temperatures.
3. Q1 temperature at 6.5 A peak.
4. C1-C3 ripple/case temperature at 20 kHz.
5. Servo stall/startup and 5V transient.
6. J7 voltage drop and connector temperature.

Until these are recorded, the power tree is **calculated, BLOCKED**.
