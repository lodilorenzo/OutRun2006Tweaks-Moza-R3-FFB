# Native RPM LEDs — v0.2.0

MOZA **R3 + ES** only. Keep the MOZA driver installed; **Pit House and SimHub must
stay closed** while native LEDs are enabled. The port cannot be shared. No SDK,
fake-game helper, firmware update, calibration or rotation change is required.

## Enable

1. Install the v0.2.0 DLL and launcher following [BUILD.md](../BUILD.md), preserving
   your existing tuned launcher, INIs and saves. Both FFB and LEDs ship disabled.
2. Use `Play OutRun - MOZA R3 FFB.cmd` to verify steering, pedals and buttons with
   Pit House closed and the game focused. Close the F11 overlay before driving.
3. Exit and set `NativeRpmLedsEnabled=true` in the copied launcher, leaving
   `NativeFfbEnabled=false`. Restart and check the LEDs when accelerating/shifting,
   then pause, F11, Alt-Tab and exit to check clearing.
4. Only after input/LED checks pass, follow the [low-force procedure](../README.md#defaults-and-safety)
   before enabling FFB. Do not enable FFB to fix an input problem or reuse high
   tuned strengths for a first combined test on another setup.

## Settings

| Setting | Launcher default | Meaning |
|---|---:|---|
| `NativeRpmLedsEnabled` | false | Opt-in LED worker, independent of FFB enablement |
| `NativeRpmLedsFirstRpm` | 4000 | RPM for the first LED |
| `NativeRpmLedsFullRpm` | 8000 | RPM for all ten LEDs; other thresholds evenly spaced |
| `NativeRpmLedsDiagnostics` | true | Once-per-second RPM/requested-mask logging |

Restart after changing enablement or thresholds. Valid range:
`100 <= first < full <= 20000`. Out-of-range RPM clears the bar. DLL diagnostics
are off by default; the launcher enables them. Launcher arguments override INIs.

RPM comes from the game's smoothed dashboard value at player-car +0x20C, not from
speed/gear synthesis. Tune thresholds for the chosen car: there is no automatic
car-specific redline, flashing or Pit House threshold synchronization.

## Transport and diagnostics

The worker discovers only a unique present R3 serial interface (`346E:0005`,
MI_00); it never guesses COM4 or falls back to another device. It opens exclusively
at 115200/8N1, with no handshake. Only legacy `41 13 FD DE` LED-mask frames are sent
to base address 0x13, never legacy telemetry to wheel address 0x17. No motor,
rotation, device force-preset or calibration commands are sent.

Serial I/O runs separately from SDL input and DirectInput FFB, at roughly 30 Hz
with a 100ms write timeout. A fault disables LEDs until restart, without changing
input/FFB. Samples expire after 250ms; menus/pause, focus loss, overlay, stale input
and disconnect request clearing. Normal shutdown attempts zeros and waits up to
one second before requesting I/O cancellation. No automatic reconnect is attempted.

Look for `Native RPM LEDs` in `OutRun2006Tweaks.log`: Win32 error 170 means close
Pit House/SimHub (or process enumeration failed); 1168 means no unique R3 port was
resolved. An opened port or requested mask is not by itself proof of physical LEDs.

## Validation and limits

I successfully tested gameplay with the exact included DLL. My local 2026-09-09
log shows native FFB and LEDs active together, 271 dashboard RPM/mask
samples matching the thresholds, and LED-worker shutdown with error 0. I also
physically confirmed the standalone LED pattern. Hardware-free C++ tests cover
all 1024 masks, checksum/escaping, RPM thresholds and mailbox expiry/clearing.

I consider this a smoke test, not a hardware safety certification.
**Clearing is best effort, not a hardware watchdog:** a crash, forced termination,
disconnect or faulty driver can leave LEDs lit. Physical clearing for every
lifecycle path, stalled-driver cancellation and long-session reliability have not
been independently established. Keep wheel power-off accessible when using FFB.

Protocol reference: [francisdb/moza-rev](https://github.com/francisdb/moza-rev), MIT,
commit `6a3cf66c734dde29126e6d9b296adeab4479d005`. Encoder written from the wire
format; no MOZA SDK or GPL AZOM code is bundled.
