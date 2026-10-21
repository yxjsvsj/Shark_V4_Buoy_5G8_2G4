# Round 7 depth-control hardware review

Date: 2026-10-21. Baseline: `62098cf`.

Status: **PROPOSED / NOT IN REVB / SENSOR CHARACTERIZATION REQUIRED.**

## 1. Requirement and pressure

- Maximum working depth target: 5 m freshwater.
- 5 m freshwater gauge pressure: `rho*g*h = 1000 * 9.81 * 5 = 49.05 kPa` (490.5 mbar).
- Absolute pressure at 5 m with 1013 mbar surface: about **1503 mbar**.
- 7.5 m equivalent validation: about **1737 mbar**.
- Static depth target: +/-0.2 m, which is about **+/-19.6 mbar**.
- These are design targets, not a pressure-vessel qualification.

## 2. Pin choice: PA4/PA5 are not I2C

STM32G030K8T6 datasheet Table 13:

- PA4: SPI1_NSS/I2S1_WS, SPI2_MOSI, TIM14_CH1.
- PA5: SPI1_SCK/I2S1_CK.
- Neither PA4 nor PA5 has an I2C alternate function.

I2C1 is available on:

- PB6 = I2C1_SCL
- PB7 = I2C1_SDA
- PA9/PA10 = I2C1 SCL/SDA (already used by motor PWM)
- PB8/PB9 = I2C1 SCL/SDA (free)

**Proposed depth interface: I2C1 on PB6/PB7**, which are currently spare. This is the lowest-conflict choice because it does not disturb the six motor PWM pins or the SWD pins.

Do not use PA4/PA5 for I2C. They may be used for SPI or a spare GPIO, but not this sensor.

## 3. Sensor choice

### Bar02 / MS5837-02BA

- Supply 1.5-3.6 V; 3.3 V compatible.
- I2C address 0x76 (7-bit).
- 24-bit ADC; 0.016 mbar RMS at OSR 8192.
- Operating pressure range 300-1200 mbar; extended linear range 10-2000 mbar.
- Relative accuracy +/-2 mbar in 300-1100 mbar; overpressure 10 bar.
- At 5 m the absolute pressure is ~1503 mbar: **above the specified 1200 mbar operating range**, although inside the 2000 mbar extended range. The accuracy at 1503 mbar is **not guaranteed by the published operating-range specification**.
- The sensor is a candidate only if TE confirms 1.5-1.8 bar operation, or if it is calibrated/characterized against a reference at 5 m and 7.5 m.

### MS5837-30BA

- 0-30 bar, 0.2 mbar resolution, but absolute accuracy is +/-50 mbar (0-6 bar, 0-45 C), which is about 0.5 m. That is **not sufficient** for a +/-0.2 m target without individual calibration.
- Use only if a calibrated absolute accuracy better than 20 mbar can be demonstrated.

### Recommendation

Use **MS5837-02BA / Bar02** for prototype characterization, not as a production-verified 5 m sensor. A 2 bar absolute sensor with specified accuracy at 1.5-1.8 bar is preferred; if no such part is available, calibrate the 02BA at the actual working pressure and temperature.

## 4. Proposed circuit

Add a 4-pin sensor connector J10:

| Pin | Signal | Notes |
|---|---|---|
| 1 | +3V3 | 100 nF + 470 nF local; sensor 1.5-3.6 V |
| 2 | GND | short return to MCU ground |
| 3 | SCL | PB6 / I2C1_SCL; 4.7k pull-up to +3V3 |
| 4 | SDA | PB7 / I2C1_SDA; 4.7k pull-up to +3V3 |

- Add 22-100 ohm series resistors at the MCU side for cable/probe protection if the sensor is remote.
- Add ESD/TVS only if the sensor cable leaves the hull; a potted 4-wire pigtail is preferred.
- The Bar02 breakout is not a 5 m watertight assembly. Use the bare MS5837 with the specified O-ring in a sealed pressure port, or a potted/ oil-filled housing. The sensor port must see ambient water; the electronics side must stay dry.
- Keep the I2C leads short and away from motor PWM. Use a ground guard and a local 100 nF at the sensor.
- The module's onboard pull-ups (if any) must be checked; do not parallel excessive pull-ups.

This interface is **not present in RevB**. PB6/PB7 are currently NC in the schematic. Do not mark it READY until the actual symbol, footprint, connector and netlist are added and checked.

## 5. Depth-control behavior

- Sample pressure/temperature at 10 Hz; discard the first conversion after reset.
- Convert absolute pressure to depth using a surface reference captured at boot:
  `depth_m = (P_abs - P_surface) / (rho * g)`, with rho ~1000 kg/m3 freshwater.
- 1 mbar is about 1.02 cm of freshwater; +/-0.2 m is about +/-19.6 mbar.
- Low-pass the depth estimate; use a 0.05 m deadband and a slow PI loop for the vertical thruster.
- Limit vertical command and ramp; do not use the vertical motor as a depth hold without a timeout.
- If pressure is stale (>200 ms), out of range, or CRC/calibration fails: command motors 0 and jaw open; do not keep the last depth.
- Auto-depth is enabled only with a valid surface reference, valid pressure, no leak, and valid PP link. Loss of PP or leak -> surface/stop.
- A 5 m depth change changes buoyancy via hull compression and trapped air; the controller needs integral authority but must avoid integrator windup.
- IMU is optional and not committed. If added, use a free SPI/I2C bus and do not take PB6/PB7 or the motor pins without a new pin review.

## 6. Missing evidence

- No actual pressure sensor symbol/footprint in RevB.
- No 5 m/7.5 m pressure test.
- No sensor accuracy characterization at 1.5-1.8 bar.
- No housing/O-ring/gland design.
- No depth-control firmware.
- No vertical thruster thrust measurement.
