# V4 buoy test plan

Test the buoy links before drawing the final sub PCB.

## 0. Preconditions

- LimeRC receiver source/license resolved; PP polarity normal 3.3V TTL.
- Thruster running/start/stall current measured; MX113H within 1A continuous / 1.5A peak.
- Servo model and stall current measured; +5V budget includes camera/buoy/servo.
- 5V power tree and protection current checked; MT3608 thermal test at 3.0V/0.4/0.72/1A; Q1/L1 thermal checked.
- C1-C3 polymer ripple/case temperature checked at 20kHz PWM.
- J7 50cm cable: proposed JST-PH 6P, 24AWG +5V/GND (insulation 0.9-1.5mm), separate shielded video; crimp pull test; CVBS 75 ohm VTX termination checked.
- J7/cable/gland mock-up checked for 5.0-5.5mm OD and 30mm static bend.

## 1. Buoy bench test

- Leak test the empty buoy; then with a paper towel/desiccant, not electronics.
- Float test: buoy upright, antennas vertical, cable gland above water.
- Cable strain: pull gently on the cable; the tow loop/strength member takes the load, not the solder joints.
- +5V at the buoy: measure under load (VTX + receiver + camera), then with servo stall; check J7 voltage drop and heat.
- Check 5.8G VTX and 2.4G receiver current; check heat at 25mW.
- Check Q1 and L1 temperature at the worst-case +5V load plus motor peak.

## 2. 5.8G video test

1. Camera + VTX on the bench, 1 m apart; set the receiver to the same channel.
2. Put the camera in a clear waterproof box with a 2 mm acrylic window; keep the buoy/VTX above water.
3. Test camera depth 10/20/30/40 cm; record 30 s at each.
4. Try 5.8G channels; pick the cleanest.
5. Move the receiver antenna; note nulls; keep it vertical.
6. Check video with the tank LED on/off; check white LED fill.

Pass: stable 640x480 image, no freeze, acceptable noise at 30-40 cm camera depth.

## 3. 2.4G control test

1. LimeRC remote + LimeCam receiver on the buoy; `pp` output at 115200.
2. Connect `pp` to the G030 UART2; verify channels in the debug print.
3. Run 10 minutes at 5-10 m; record dropouts.
4. Check failsafe: remote off -> motors stop, jaw open.
5. Send malformed/partial PP frames; parser must reject them and keep motors stopped.
6. At reset, all H-bridge IN1/IN2 must be 0; no motor twitch.
7. Check the `pp` output mode is enabled on the remote (LimeCam default may be off).
8. Link loss: turn off only the 2.4GHz transmitter while UART stays connected; capture UART and confirm one 2048 neutral frame, then silence; confirm G030 stops motors and opens jaw within 500ms.
9. Restore the link; confirm PP frames resume and the G030 does not require a power cycle.

Pass: no dropouts at the tank distance; failsafe works; link-loss behavior matches the source review.

## 4. Integrated tank test

1. Shark tows the buoy; cable 50 cm; buoy stays upright.
2. Drive forward/back, turn, vertical; watch the cable and buoy.
3. Open/close the jaw; check camera view.
4. Run 10 minutes; check leaks, cable tangle, buoy trim.
5. Bring the shark to the surface; check the buoy did not flood.
6. Cut power/control; confirm the shark is positively buoyant and surfaces.

Pass: buoy upright, cable not tangled, video/control stable, no leaks.

## 5. Failure handling

- Buoy flips: add keel/drop keel; move battery/electronics lower.
- Buoy pulled under: more foam/volume; shorten cable; reduce drag.
- Cable tangle: shorter cable, smoother jacket, route above the shark; add a small float bead.
- Video noisy: 5.8G channel, antenna orientation, shield the video pair, add LC/ferrite.
- Control dropouts: 2.4G antenna position, keep away from 5.8G VTX, check `pp` baud/mode.
- 5V drop: thicker 5V/GND, add 100uF at buoy, raise boost to 5.2V.

## 6. Pass criteria

- 5.8G video: stable 640x480 at 30-40 cm camera depth.
- 2.4G control: no dropouts for 10 minutes at the tank distance.
- Buoy: upright, positive buoyancy, no leaks, cable not tangled.
- Failsafe: motors stop and jaw opens on loss of control.
- Reset: H-bridges off; no motor motion before valid PP.
- Power: thruster peak within MX113H rating; +5V/+3V3 rails stable; Q1/L1/J7 not overheating; servo stall does not brown out the G030.
- MT3608: record case temperature and 5V ripple at 3.0V/0.4/0.72/1A; if 0.72A/1A exceeds the limit, the 5V architecture is not approved.
- C1-C3: case temperature and ripple within the polymer capacitor rating at 20kHz.
- J7: 24AWG crimp pull test, housing latch, 30mm bend and gland mock-up pass.
- Buoyancy: shark surfaces on power/control loss.
