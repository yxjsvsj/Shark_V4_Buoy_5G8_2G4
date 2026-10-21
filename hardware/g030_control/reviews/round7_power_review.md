# Round 7 power and magnetic-switch review

Date: 2026-10-21. Baseline: `62098cf`.

Status: **CALCULATED / NOT MEASURED / MT3608 BLOCKED / SWITCH DECISION REQUIRED.**

## 1. Current Q1 / R5 / SW1 circuit

The current circuit is:

- Q1 SiSS23DN-T1-GE3 P-MOS, source pins 1-3 to VBAT, drain 5-8 to VMOTOR.
- R5 100k from VBAT to PWR_GATE.
- SW1 reed switch from PWR_GATE to GND.
- C14 100nF from PWR_GATE to VBAT.

Behavior:

| Condition | Q1 | VMOTOR | Result |
|---|---|---|---|
| Magnet present, SW1 closed | VGS = -VBAT, on | battery voltage | system powered |
| Magnet removed, SW1 open | VGS = 0, off | 0 V (loads discharge) | system off |
| MCU reset with magnet present | Q1 stays on | battery voltage | MCU restarts; MX113H inputs have 15k pull-downs, so IN1/IN2 default low -> outputs high-Z |
| MCU firmware hang with magnet present | Q1 stays on | battery voltage | watchdog reset is required; otherwise PWM state depends on firmware |
| Battery removed | off | 0 V | safe |

This is a **hold-to-run** switch, not a latch. It is acceptable only if the user intentionally keeps the magnet in place. A bump or dislodged magnet removes power and thrust; positive buoyancy is then the only recovery.

### Decision required

Choose one:

1. **Keep hold-to-run** - simplest, no standby drain after magnet removal, but the magnet is a critical external part and can be lost.
2. **Magnetic toggle/self-latch** - a reed pulse toggles a P-MOS latch or a small supervisor; MCU can hold power and release it on fault. Adds state, off-state leakage, and a way for the MCU to become the only thing that can turn off a stuck system. Needs a hardware default-off and a manual override.

Do not silently freeze option 2. Current design is option 1.

### Protection gaps

- No board fuse/PTC, reverse-polarity MOSFET, or ideal diode is drawn. The XT30 is keyed, but keying is not reverse-polarity protection.
- The protected 1S pack is assumed to provide overcharge/over-discharge/overcurrent; this must be a specified pack requirement.
- No TVS on the motor outputs or battery input.
- Q1 gate has no Zener/clamp; VGS max is within the 1S range, but cable transients are not covered.
- C14 is 100nF; gate pull-up 100k gives a slow turn-off. Verify no transient reverse current through the body diode.

## 2. Load and current budget

| Load | Nominal | Worst case |
|---|---:|---:|
| Camera | 0.10 A | TBD |
| Buoy VTX/receiver | 0.40 A | TBD |
| Jaw servo | 0.20 A | stall TBD |
| G030/LDO | 0.02 A | 0.03 A |
| 5V total | 0.72 A | >1 A if servo stalls |
| Three MX113H motors | 3 x running current | 3 x 1.5 A peak = 4.5 A |
| Battery continuous estimate | ~4.96 A at 1 A/motor | ~6.46 A peak |

The 4.96 A figure is a **budget**, not a measurement. MX113H thermal derating may reduce the allowable continuous motor current below 1 A.

## 3. MT3608 vs TPS61022

### MT3608

- Input 2-24 V, but the relevant point is 3.0 V.
- 5 V output, 1 A advertised; the datasheet thermal limit is the binding constraint.
- Corrected chip loss: 0.090/0.184 W at 0.4 A, 0.172/0.356 W at 0.72 A, 0.264/0.561 W at 1 A.
- TJ at 40 C and 250 C/W: 63/86 C, 83/129 C, 106/180 C.
- The 0.72 A max case is marginal; the 1 A max case exceeds the 150 C junction limit.
- L1 SRP6060FA-220M: 22 uH, 5.6 A Isat, 3.8 A Irms.
- Board area for one rail plus passives: roughly 65-75 mm2; a split two-rail solution is roughly 150 mm2.
- JLCEDA symbol/footprint: already present.

### TPS61022

- Input 0.5-5.5 V; start-up 1.8 V; output 2.2-5.5 V; 8 A valley current limit.
- 2 x 2 mm VQFN-7, 1 MHz.
- 94.7% typical at 3.6 V -> 5 V, 3 A; 3.0 V/1.5 A is a design target, not a guaranteed datasheet point.
- 1 uH inductor, 10 uF input and at least 30 uF effective output for <=1.5 A.
- RthetaJA 50.9 C/W on the TI EVM; at 0.72 A and ~90% efficiency the converter loss is roughly 0.4 W, IC share lower; expected rise is far below MT3608.
- Board area roughly 60-80 mm2.
- JLCEDA symbol/footprint: **not yet verified**.

### Recommendation

Prefer TPS61022 with a **1.5 A continuous target at 3.0 V**, conditional on WEBENCH/bench data. Keep split MT3608 as fallback. Do not change the RevB schematic until the TPS61022 symbol, footprint, inductor and output capacitor are bound and the actual load is measured.

## 4. Unknowns

- Servo stall current and simultaneous servo/camera/VTX load.
- Real VTX current, especially at 5.8 GHz transmit.
- Motor running/start/stall current at 3.0 V and 4.2 V.
- Battery pack continuous/peak rating and PCM behavior.
- Enclosure ambient at 5 m, copper temperature, and 5 V ripple.
- Whether the selected 5V receiver/VTX accepts the cable drop at 5 m.

No value above is a measured result.
