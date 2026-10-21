# Round 7 blockers

Date: 2026-10-21. Baseline: `62098cf`.

## Hard blockers

1. **GUI netlist export** - the JLCEDA export dialog opened, but the Protel type selector could not be changed reliably through the available automation. No GUI netlist exists. `g030_export.net` remains provisional.
2. **Full DRC log** - no object/net/coordinate/rule/page export. Aggregate 138 warnings (137 NETOBJECTONGRID + 1 CHECKFLOATPIN) is unchanged. No DRC-clean claim.
3. **NC flags** - U5.6, U6.4 and unused U1 pins are absent rather than explicitly marked; CHECKFLOATPIN remains.
4. **J8** - actual symbol is still HDR1X5 2.54 mm. TC2030 6-pad 1.27 mm is a proposal, not implemented.
5. **Depth sensor** - no sensor, connector, symbol, footprint, net or firmware. PA4/PA5 cannot be I2C; PB6/PB7 is the proposed bus.
6. **MS5837-02BA range** - 5 m absolute pressure is ~1503 mbar, above the specified 1200 mbar operating range (extended linear range is 10-2000 mbar). Accuracy at 1.5 bar is not guaranteed by the operating specification.
7. **LimeRC PP polarity** - receiver boots PP + inverted + output-disabled. Normal TTL must be selected and captured. No hardware inversion/auto-detect in Shark.
8. **LimeRC RF module** - actual module is AS01-ML01S; F407 E01C-ML01S compatibility is not verified.
9. **LimeRC video** - receiver video is OV2640 digital, not CVBS. Shark CVBS is an independent chain. No VTX 75 ohm termination test.
10. **5 m cable** - 24AWG/JST-PH is inadequate for a 10 m loop at 0.72-1 A. 18-20AWG power or separate connector required; exact IP68 connector TBD.
11. **MX113H thermal** - 1 A continuous at 25 C, 0.4 ohm, 220 C/W; sealed-hull 1 A is not approved. Three motors at 1 A are not simultaneous continuous.
12. **J2-J4** - JST-SH 1 A connectors vs 1.5 A peak; no margin.
13. **5V converter** - MT3608 BLOCKED; TPS61022 is a candidate, not in the schematic, not footprint-verified.
14. **Battery protection/reverse polarity** - protected pack assumed; no board fuse/PTC or reverse-polarity FET.
15. **Pressure/water test** - no 5 m or 7.5 m test; no housing/O-ring/gland qualification.
16. **Thruster measurements** - running, start, stall and low-voltage thrust are all unmeasured.
17. **Servo/VTX current** - servo stall and real VTX current are unmeasured.
18. **F407** - exact firmware build, RF module, 25 MHz clock, pairing, PP polarity and third-party licenses remain unverified.
19. **License** - LimeRC repository is GPL-3.0; OSHW page says CC BY-SA 4.0 and includes a commercial-use restriction sentence. Legal review required.

## Soft blockers / decisions

- Q1 magnetic switch: hold-to-run vs self-latch (`DECISION_REQUIRED`).
- Leak probe DC excitation causes electrolysis; AC/pulsed drive is preferred.
- J7 connector series and 5 m cable construction.
- Whether to use the 02BA with calibration or a 2 bar sensor with specified accuracy at 1.5-1.8 bar.
- Whether an IMU is required for depth control; not committed.
