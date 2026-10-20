# V4 buoy test plan

Test the buoy links before drawing the final sub PCB.

## 1. Buoy bench test

- Leak test the empty buoy; then with a paper towel/desiccant, not electronics.
- Float test: buoy upright, antennas vertical, cable gland above water.
- Cable strain: pull gently on the cable; the tow loop/strength member takes the load, not the solder joints.
- 5V at the buoy: measure 5V under load (VTX + receiver + camera).
- Check 5.8G VTX and 2.4G receiver current; check heat at 25mW.

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
5. Check the `pp` output mode is enabled on the remote (LimeCam default may be off).

Pass: no dropouts at the tank distance; failsafe works.

## 4. Integrated tank test

1. Shark tows the buoy; cable 50 cm; buoy stays upright.
2. Drive forward/back, turn, vertical; watch the cable and buoy.
3. Open/close the jaw; check camera view.
4. Run 10 minutes; check leaks, cable tangle, buoy trim.
5. Bring the shark to the surface; check the buoy did not flood.

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
