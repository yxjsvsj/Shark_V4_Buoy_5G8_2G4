# Round 7 next actions

Date: 2026-10-21. Baseline: `62098cf`.

## Order of work

1. **Manual EDA gate (first)**
   - Open RevB in JLCEDA Pro, select `导出 -> 网表文件`, choose **Protel**, export to a timestamped filename.
   - Save the GUI export outside the provisional file and run `verify_g030_netlist.py` against it.
   - Run DRC, export the full object/page/rule log, and attach it.
   - Add explicit NC flags to U5.6, U6.4 and unused U1 pins; verify connector shield/mechanical pads.
   - Do not edit the schematic further until this baseline is captured.

2. **Decide the magnetic switch**
   - Hold-to-run or self-latch. If self-latch, define default-off, MCU hold, manual override, and off-state leakage.
   - Update `01_POWER` only after the decision; do not silently add a latch.

3. **Measure loads**
   - Servo stall at 5 V.
   - Real VTX/receiver current.
   - Three thruster running/start/stall at 3.0/3.7/4.2 V.
   - Pack continuous/peak capability.
   - Sealed-hull ambient and case temperatures.

4. **Select the 5 V converter**
   - If measured 5V load <=0.4 A per rail: split MT3608 is feasible.
   - If 5V load is 0.7-1.5 A: use TPS61022 after symbol/footprint/inductor/cap review.
   - Update schematic only after a real JLCEDA symbol/footprint is bound.

5. **Redesign the 5 m buoy cable**
   - 18-20AWG power pair or separate IP68 power connector.
   - 75 ohm coax for CVBS.
   - Series/TVS on PP and telemetry.
   - Strain relief, gland, cable mass/buoyancy and bend radius.
   - Measure drop/ripple at 0.72/1/1.5 A over the final length.

6. **Depth sensor**
   - Bind a real pressure sensor symbol/footprint on PB6/PB7 (I2C1).
   - Add J10 + 4.7k pull-ups + local decoupling + ESD.
   - Characterize 02BA at 1.5-1.8 bar, or select a 2 bar part specified at that pressure.
   - Define surface reference, filtering, auto-depth PI, stale-sensor failsafe and leak/PP interlocks.

7. **Motor drive**
   - Replace J2-J4 if measured stall >1 A.
   - Derate MX113H to <=0.7 A continuous in the sealed hull or select a lower-RDS(on) driver.
   - Add current limit/fuse and stall detection.
   - Measure bidirectional vertical thrust.

8. **J8**
   - Replace HDR1X5 with Tag-Connect TC2030 6-pad or another real 1.27 mm pogo footprint.
   - Verify pad order, cable orientation, and no 2.54 mm header remains.

9. **LimeRC/F407**
   - Set receiver to PP + normal TTL and capture the UART.
   - Verify AS01-ML01S vs E01C-ML01S pin/antenna/firmware compatibility.
   - Confirm 25 MHz, pairing, video link and GPL/CC licensing.
   - Do not freeze the buoy RF PCB before this.

10. **Pressure and tank testing**
    - 5 m and 7.5 m static pressure test of the hull and sensor port.
    - Cable/gland pull and bend test.
    - Positive buoyancy and trim test.
    - Only then consider a limited shallow powered test with a current-limited supply and no personnel nearby.

## Still forbidden

No battery-only power, no PCB order, no production Gerber, no claim of 5 m capability, no claim of ERC/DRC pass, no claim that the provisional netlist is a GUI export.
