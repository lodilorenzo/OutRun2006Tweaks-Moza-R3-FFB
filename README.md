# OutRun 2006 Wheel & FFB — v0.2.0

Unofficial, experimental wheel-input and native force-feedback patch for
**OutRun 2006: Coast 2 Coast on Windows**, based on
[emoose/OutRun2006Tweaks](https://github.com/emoose/OutRun2006Tweaks).
Not endorsed by Sega, MOZA or upstream maintainers.

Includes a compiled Win32 Tweaks + wheel/FFB/RPM LED DLL, complete source patch,
safe editable launcher and hardware-free tests. **No game EXE/assets, saves,
personal configurations, captures, debug symbols or proprietary FFB toolkit.**
This is not a standalone game or an extra DLL to stack with another Tweaks mod.

## Install

1. Read [BUILD.md](BUILD.md#5-install-manually-into-a-compatible-game-copy), including
   EXE compatibility, backup and rollback instructions. Run `python verify.py`.
2. Close OutRun and force/telemetry tools; back up the game's DLL/PDB and launcher.
3. Copy `runtime/dinput8.dll` and `runtime/Play OutRun - MOZA R3 FFB.cmd` beside the
   compatible game EXE. Move any old PDB to backup; matching symbols are not bundled.
   Preserve INIs, saves and tuned launchers. Bare-EXE launch does not apply the preset.
4. Start with **FFB and LEDs disabled**. Follow [wheel setup](runtime/WHEEL-BUTTONS.md)
   to assign and save buttons, then [native LED setup](runtime/NATIVE-RPM-LEDS.md).
   Keep Pit House/SimHub closed while native LEDs are enabled.

Keep LICENSE.md and THIRD-PARTY-NOTICES.txt with redistributed files.

## Implemented effects

- Physical-steering centring, gear jolts and blended road/off-road texture.
- Barrier onset pulses and continuous barrier scraping.
- Experimental traffic impact pulses and continuous traffic-contact texture.
  Only one wall/traffic impact envelope wins; suppressed impacts are not queued.
- **Drift road damping:** `NativeFfbDriftDampingPercent` is a **0–100 percentage
  reduction**, not an absolute force strength. **20 means 20% less** road texture
  on every surface, 0 disables the modifier, and 100 silences road texture during
  a fully blended estimated drift. Centring, gear/contact effects and LEDs are
  unaffected. Changing normal road endpoints does not require recalculating
  damping.
- Native R3/ES RPM LEDs with configurable dashboard-RPM thresholds.

Drift uses the provisional raw-D34 estimator I tested, not a verified physical
slip angle or exclusive game action flag. Its entry/recovery cuts, speed
floor and 6–10 Hz texture frequency are configurable. It preserves surface/speed
scaling and oscillator phase, blends over 100 ms, and requires neutral rearming
after attach, contact, unknown data or a sampling gap. Unknown clears the modifier;
existing global stop gates still stop immediately. See [settings](BUILD.md#editable-ffb-settings).

**All implemented effects are present in one DLL.** The published launcher keeps
FFB/LEDs disabled, 1% centring configured and accents/damping zero. Water splashes,
surface-transition accents, general airborne/landing feedback and crash-flight
animation shake are **not implemented**.

## Compatibility and safety

Upstream is pinned to `08e5efb4deea4066c440307ec009c868a30562d3`; do not apply the
patch to latest upstream. The wrapper retains upstream version/resource metadata;
that displayed version is not my project's version.

MOZA R3 `346E:0005` mapping retains physical steering axis 0, accelerator 2, brake 5,
24 observed buttons and the existing D-pad hat. Persistent extended SDL button
names, input binding, LEDs and early cleanup are retained. Other wheels/platforms,
OutRun 2 SP/SDX, TeknoParrot and FXT remain unvalidated. This is reconstructed arcade
feedback, not original cabinet physics or universal wheel support.

**v0.2.0 uses a hard 50% combined DirectInput cap.** Individual strength numbers
still mean 0–1 DI-command fractions; overlaps can clip at the shared cap. Percentages are **not measured
motor torque**. One finite constant-force effect is refreshed from the existing
player hook; no new device backend or automatic countersteer is introduced.

Before enabling force: secure the wheel, clear travel, keep physical power-off
reachable, set base output to 10% or less, then close Pit House when using native
LEDs. Start with input-only, then 1% centring and verify direction and pause/focus/
overlay/exit stopping. Add one accent at low strength at a time. On a hang,
unexpected sustained pull or failed stop, **power the wheel off and end the test**.
Do not deliberately stall or disconnect under force without a separate procedure.

## Validation limits

I tested the integrated v0.2.0 all-effects patch across three sessions and
encountered no problems. The neutral-path public rebuild has byte-identical PE
sections to the tested DLL; only non-loaded debug-path data differs. I consider
this a combined hardware smoke validation, not a universal detector-accuracy, exact
drift-timing, torque or exhaustive lifecycle claim.
Traffic solidity/ghost discrimination and collision-corrupted drift classification
remain imperfect. Aggressive unknown/contact suppression can miss legitimate drifts.

Hardware-free checks cover actual production models, independent legacy-road
comparison, damping 0/20/50/100 across different endpoints, clocks/resets, contact
arbitration, all-effects mixing, hard device cap, fake-COM cleanup, LED protocol,
button names and virtual SDL mapping. I do not require private captures to
reproduce the published tests. They do not prove physical stopping or LED clearing.

The finite 100 ms lease depends on driver/device behavior. Historical intermittent
hang/input loss, stalled-update expiry, disconnect handling and long-session
reliability remain unresolved. LED clearing after a crash/fault is best effort.

## Source, integrity and licensing

`source/native-ffb.patch` is the complete **twenty-file** patch, including nine test
files; `source/provenance.json` records upstream/dependency/toolchain pins.
`runtime/dinput8.dll` is the compiled Win32 release; `VERSION` and `CHANGELOG.md`
track this independent project. [BUILD.md](BUILD.md) explains rebuilding and tests:

```bat
python verify.py
python verify.py --upstream C:\path\to\pinned-upstream
```

`manifest.json` pins the shipped files. Hashes detect accidental changes; they do
not authenticate me as the publisher. Rebuilt bytes may differ by compiler, paths
and timestamps.
MIT terms and original/reference attribution are retained in LICENSE.md and
THIRD-PARTY-NOTICES.txt. Dependency sources are obtained separately. No rights to
Sega game content or proprietary MOZA software are granted.
