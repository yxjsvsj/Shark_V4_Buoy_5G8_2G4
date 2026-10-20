# V4 two-board design review

Status: review accepted; architecture confirmed; **device values and board sizes are not frozen**.

## Final V1 selection

| Board | MCU | Actuators | Notes |
|---|---|---|---|
| Shark control board | STM32G030 | 3x MX113H brushed + 1 jaw servo | No RF, no camera processing |
| Buoy RF board | STM32F407 (stripped LimeCam) | none | 2.4G LimeRC + `pp`; 5.8G VTX separate |

Video: CVBS camera -> 50 cm cable -> 5.8G VTX on buoy -> tank-edge receiver.
Control: LimeRC remote -> buoy 2.4G -> `pp` -> 50 cm cable -> G030.
4-in-1 brushless ESC is **not** used in V1.

## P0 gates before schematic freeze

### 1. LimeRC firmware source and license

- Confirm the receiver source is legally available and compilable, including:
  - exact RF chip/module and pin map;
  - pairing/flash storage;
  - HSE/PLL clock (V3 project uses 24 MHz; original LimeCam code uses 25 MHz - resolve this);
  - NRF2/SPI2, USART1, `pp` output;
  - PP polarity (normal 3.3V TTL vs inverted).
- Hardware CC BY-SA 4.0 does not automatically grant source modification rights. The public HEX may be personal/non-commercial only.
- If only HEX is available:
  - do not assume `nrfPhotoTask_Suspend()` can be stubbed;
  - do not assume a new F407 board will run the original HEX;
  - prefer using the original LimeCam board as the buoy receiver, or obtain source/permission.
- Do not switch to G030+nRF24 as a shortcut: it still requires a LimeRC-compatible protocol implementation.

### 2. Power tree

- 1S protected battery -> Q1 SiSS23DN -> `VMOTOR` -> 3x MX113H.
- 1S -> 5V boost -> camera/buoy VTX/receiver/servo.
- 5V -> 3.3V LDO, or a dedicated 3.3V buck-boost for G030/F407.
- Do not stack a second boost without checking the original LimeMini power design.
- Budget: MT3608 +5V/1A at 3.0V/85% is ~1.96A input; L1 is SRP6060FA-220M (22uH, 5.6A Isat, 3.8A Irms). TLV70033 is 200mA max.
- **MT3608 thermal rejection:** with 250C/W thetaJA, TJ is ~199C at 5V/0.72A and ~261C at 1A in 40C ambient. The package also exceeds 0.6W PD at 0.72A. The 5V architecture is BLOCKED until the boost is replaced or the load is reduced/split. See `power_budget.md`.
- Q1: SiSS23DN-T1-GE3, 20V/50A, 6.3mohm max at VGS=-2.5V, PowerPAK 1212-8S. AON7403 has no published -2.5V RDS(on) and is not approved for 1S.
- Servo stall current is not measured; do not assume 0.2A. With 0.52A other load, 0.5A servo already exceeds the 1A boost.
- C1-C3 are 100uF 6.3V polymer tantalum 1206; the 100uF/0805 X5R assumption is rejected because of DC-bias loss.
- Check DW01A/FS8205A or chosen protection continuous/peak current; check battery 30C and connector.
- 3.3V LDO from 1S is not acceptable for a stable 3.3V rail; use boost/buck-boost or 5V-derived LDO.

### 3. Motor and MX113H validation

- MX113H: 2-8V, 1A continuous / 1.5A peak, SOT-23-6, Rds(on) 0.4Ω.
- Measure each thruster with prop: running current, start-up peak, stall current, thrust.
- If stall/peak exceeds 1.5A, change driver or motor.
- Check SOT-23-6 thermal/copper; add 100uF + 100nF at each H-bridge.

### 4. Cable and video

Recommended 6-core pinout:

| Pin | Net | Direction |
|---|---|---|
| 1 | +5V (cable label +5V_BUOY) | shark -> buoy |
| 2 | GND_PWR | power return |
| 3 | CVBS_VIDEO | shark -> buoy |
| 4 | GND_VIDEO | video return |
| 5 | PP_DOWN | F407 TX -> G030 RX |
| 6 | TELEM_UP | G030 TX -> F407 RX |

- Use a separate shielded video pair/coax, not only the overall shield.
- J7: proposed **JST-PH 6P** (2A at 24AWG, 24-30AWG). JST-SH 1A/28-32AWG is incompatible with 24AWG and must not remain.
- J7/cable mechanical: mated body ~13.9 x 4.5 x 8.0mm; cable OD ~5.0-5.5mm; 30mm static / 55mm dynamic bend. Top-entry plus bend is tight in the 55mm buoy; mechanical fit PENDING. See `mechanical/j7_assembly.md`.
- CVBS is 75 ohm; check whether the VTX input has a 75 ohm termination to avoid double termination.
- 50 cm is for shallow testing; for 50 cm depth plus float/connector margin, make a longer version.
- Define connector, strain relief, neutral buoyancy and max depth.

### 5. Board sizes

- Shark: first pass ~26x40-46 mm; target 20x30 only after layout feasibility.
- Buoy: target 30x30 mm, allow 30x35 mm; 4-layer, double-sided; VTX can be a separate module.
- Do not freeze the outline before component placement and thermal check.

## Safety

- H-bridges must be off at reset (IN1=IN2=0).
- `pp` parser must validate frame format and ranges; reject malformed frames.
- LimeCam link loss: one neutral PP frame after ~100ms, then silence. Use the 500ms frame timeout as the freshness detector; do not rely on last values. See `pp_link_behavior.md`.
- Independent watchdog; low-voltage and leak -> safe state.
- 500 ms `pp` timeout -> motors 0, jaw open.
- Shark must be positively buoyant enough to surface on power/control loss.

## Order of work

1. Resolve LimeRC source/license/clock/pin/PP polarity.
2. Measure thruster current/thrust and MX113H thermal.
3. Finish G030 schematic with final power tree and cable pinout.
4. Only then finish F407 schematic, after firmware/hardware correspondence is proven.
5. Layout first, then freeze board sizes.

## P0 remediation

See p0_status.md for the P0/P1 status table, evidence and remaining BLOCKED items. The G030 candidate schematic is `hardware/g030_control/sch/Schematic1/Shark_Sub_G030.esch2`; it is format-validated but has not been opened in JLCEDA, has generic symbols, no footprint binding, and no ERC. `g030_schematic_draft.md` + `g030_netlist_draft.csv` remain the connection-level reference.

## Repo note

The design docs are under `hardware/V4_Buoy_5G8_2G4/` in the new repository:
https://github.com/yxjsvsj/Shark_V4_Buoy_5G8_2G4


