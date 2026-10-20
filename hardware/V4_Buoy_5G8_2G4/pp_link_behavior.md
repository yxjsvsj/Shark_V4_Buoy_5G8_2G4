# PP link-loss behavior and G030 safety logic

Status: **source review complete; hardware verification pending.**
Source: `pingyun001/LimeRC`, commit `a9beb0102be529bc43736acc8ca2f508560c46d6` (2025-12-24), GPL-3.0 repository.
This is evidence for the PP receiver behavior, not proof that a new F407 board or a different receiver build is compatible.

## 1. What happens when the 2.4 GHz link is lost

The relevant code is `SOFTWARE/LimeCam_Release/Agreement/agreement_hal.c`:

- A valid NRF packet calls `AgreementOut_copyTo_RC_Key_V3A()`, which sets `isOffline = false` and refreshes `lastRefreshTime`.
- `AgreementOut_RunHandle()` sends a frame when `isNewPackLoaded` is set.
- If no new packet arrives for more than **100 ms**, it sets channels 0-3 to **2048**, sends **one** neutral PP frame, and sets `isOffline = true`.
- After that, it sends nothing until a new valid NRF packet arrives.

Therefore the current PP behavior is:

| Condition | PP output |
|---|---|
| 2.4 GHz link valid | Continuous `pp...` frames |
| Link lost, UART still connected | Exactly one neutral frame (all four sticks 2048, switch values from the last frame) after about 100 ms, then **silence** |
| Link restored | New frames resume |
| UART/cable disconnected | No frames |

It does **not** repeat the last frame. It also does not keep sending neutral frames. The G030 can therefore distinguish a live link from a lost link by **frame freshness** (time since the last valid frame), not by the numeric channel values alone.

## 2. G030 safety rule

The G030 must implement all of the following:

1. Validate the complete PP frame (`pp`, six comma-separated fields, CR/LF, ranges, no overflow).
2. Record `last_pp_rx_ms` only when a complete valid frame is received.
3. Apply motor/jaw commands only while the frame is fresh.
4. If no valid frame arrives for **500 ms**, force motors to 0 and jaw to open.
5. The neutral frame sent at link loss is accepted as one valid frame, but it is followed by silence; the 500 ms timeout then triggers failsafe.
6. Do not treat a repeated/hold-last frame as proof of link health. The current PP receiver does not repeat, but the G030 still must use the timeout, not a “last value” assumption.

Recommended test: with the receiver connected and the transmitter on, disconnect only the 2.4 GHz link, capture UART for at least 2 s, and confirm one 2048 frame followed by silence. Repeat with the exact production receiver firmware/HEX, because this source review does not prove a different build.

## 3. Is a link-status bit required?

No additional J7 wire is required for the current PP build, because loss of RF causes loss of PP frames. The G030 can detect that with the UART timeout.

A future revision may add one of these if independent link status is required:

- a receiver GPIO `RF_LINK` asserted only while the 2.4 GHz link is valid, routed on an additional cable conductor; or
- a PP protocol extension carrying a link/freshness field, which requires receiver source changes.

Do not silently repurpose `TELEM_UP` or another functional wire. J7 has no spare pin. If a link-status conductor is required, the cable/connector must become 7-pin or the buoy must send status in a defined telemetry frame.

## 4. Magnet power switch

The current circuit is **hold-to-run**, not toggle:

- Q1 is a P-MOS high-side switch.
- R5 (100 kohm) pulls the gate to VBAT, keeping Q1 off.
- SW1 is a reed switch from the gate to GND.
- A magnet must remain near SW1 to keep the gate low and Q1 on. Removing the magnet turns the board off.

This is acceptable as a deliberate safety behavior: loss of the magnet removes power. It is **not** a short-touch on/off switch.

If a short magnet touch must toggle power, a latch is required. Do not add one without confirmation. Candidate approaches:

1. A mechanically latching/bistable reed or Hall sensor plus a flip-flop.
2. A small P-MOS/N-MOS latch with a momentary sensor, plus an MCU `POWER_HOLD` output and a defined off sequence.
3. A dedicated load-switch/PMIC with enable latch and push-button control.

Each option needs a new schematic block, a defined off behavior, and a quiescent-current check. The current design intentionally does not include any of them.

## 5. Status

- PP source behavior: **confirmed from source**.
- 500 ms G030 timeout: **design requirement; firmware/test still TBD**.
- Exact production receiver firmware: **verify by UART capture**.
- F407/LimeRC hardware compatibility: **still BLOCKED**; this document does not unblock the buoy RF PCB.
- Magnet switch: **hold-to-run confirmed**; toggle latch **not designed**.
