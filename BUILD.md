# Build, test and install v0.2.0

**Using the included build?** Run `python verify.py` to check its hashes, then go
to [section 5](#5-install-manually-into-a-compatible-game-copy). The DLL is
`runtime/dinput8.dll` (Win32 Release); no compiler is needed to install it.
The steps below are for rebuilding the included source patch.

## Requirements

Windows, Git, CMake, Visual Studio C++ tools and a Windows SDK. The original R2
build used **Visual Studio 2026 / MSVC 19.51, Win32 Release**. Python 3.10+ is
optional for the source-release verifier. Dependency downloads require internet;
this is not an offline source bundle. No firmware/driver installation is performed.

Use Command Prompt. Replace `C:\src\OutRun2006-Wheel-FFB-v0.2.0` below with this
folder's location, and stop on any command failure.

## 1. Verify and obtain the pinned upstream source

```bat
cd /d "C:\src\OutRun2006-Wheel-FFB-v0.2.0"
python verify.py
git clone --no-checkout https://github.com/emoose/OutRun2006Tweaks.git upstream
git -C upstream checkout --detach 08e5efb4deea4066c440307ec009c868a30562d3
git -C upstream submodule update --init --recursive
```

Do not apply the patch to latest upstream or another mod. The version-specific
hook addresses and early shutdown integration must stay together.

## 2. Optional clean-source regression check

From the repository root, before or after applying the patch:

```bat
python verify.py --upstream upstream
```

This exports the pinned commit from the local Git repository to a temporary
directory, applies the published patch and runs its actual C++ fake-COM FFB and
RPM LED protocol/model tests.
It does not modify the supplied checkout, fetch dependencies, launch OutRun,
enumerate devices or send forces. It requires MSVC/Windows SDK, but not the
upstream submodules. No private collision capture is needed.

## 3. Apply and configure

From the repository root:

```bat
git -C upstream apply --check "../source/native-ffb.patch"
git -C upstream apply "../source/native-ffb.patch"
cmake -S upstream -B upstream/build -G "Visual Studio 18 2026" -A Win32 -DCMAKE_BUILD_TYPE=Release -DCMKR_SKIP_GENERATION=ON -DCMAKE_POLICY_VERSION_MINIMUM=3.5
```

The complete patch changes eleven production files and adds nine test files:

- `CMakeLists.txt`, `cmake.toml`: header and Windows SDK `dxguid.lib` integration.
- `src/native_ffb.hpp`: models, experimental drift estimate, percent road damping,
  gates and dedicated DirectInput output device with a hard 50% cap.
- `src/contact_models.hpp`: barrier/traffic contact textures and impact arbitration.
- `src/native_rpm_leds.hpp`, `src/native_rpm_leds.cpp`: RPM thresholds, serial encoder,
  atomic mailbox, exclusive R3 port discovery and isolated LED worker.
- `src/hooks_forcefeedback.cpp`: settings, existing car hook and surface lookup.
- `src/input_manager.cpp`, `src/input_manager.hpp`: fresh input and early cleanup.
- `src/overlay/hooks_overlay.cpp`: lifecycle/focus/pause/shutdown stop integration.
- `src/input_names.hpp`: stable save/load and display names for all extended SDL buttons.
- `tests/native_ffb_test.cpp`, `tests/run-native-ffb-tests.cmd`: no-hardware FFB checks.
- `tests/native_rpm_leds_test.cpp`, `tests/run-native-rpm-led-tests.cmd`: all 1024 LED
  masks, checksum/escaping, threshold and mailbox expiry/clearing checks.
- `tests/contact_models_test.cpp`, `tests/drift_feedback_test.cpp`,
  `tests/combined_effects_test.cpp`, `tests/legacy_road.hpp`,
  `tests/run-contact-tests.cmd`: synthetic contact/estimator/percent-damping and
  combined-mix tests with independent pre-drift road equivalence. Private captures
  are not bundled or required. An optional locally supplied contact CSV can be replayed.

### Verify dependency pins before compiling

`source/provenance.json` records all five submodule commits, FetchContent commits
and the nested Zycore commit. Compare with:

```bat
git -C upstream submodule status --recursive
git -C upstream/build/_deps/sdl-src rev-parse HEAD
```

Repeat `rev-parse HEAD` for **every** `fetch_dependencies` entry relative to
`upstream/build/_deps`, and for `zydis-src/dependencies/zycore`. Check the
submodules against the `submodules` map. Tags can move; stop on any mismatch.
Use a separate dependency checkout at the recorded commit and CMake's
`-DFETCHCONTENT_SOURCE_DIR_<NAME>=absolute-path` override if necessary (for
example `FETCHCONTENT_SOURCE_DIR_SDL`), then configure and compare again.
Do not silently call a dependency update this pinned release.

## 4. Build and test

```bat
cmake --build upstream/build --config Release --target outrun2006tweaks --parallel 6
upstream\tests\run-contact-tests.cmd
upstream\tests\run-native-rpm-led-tests.cmd
```

Also run the mapping regression from the repository root:

```bat
python tests\test_wheel_mapping.py
python tests\test_wheel_mapping.py --sdl "C:\path\to\SDL3.dll"
```

The optional second check needs an SDL3 DLL matching Python's architecture (the
pinned SDL dependency above is supported); a separate SDL3 DLL is not bundled.
The test disables
physical joystick drivers and tests a virtual 128-button wheel, all mapped press/
release transitions, simultaneous buttons, shift paddles, hats and physical axes.
The first check needs only Python and is also run by `verify.py`.

Test the actual C++ button-name save/load functions from an MSVC-enabled Command
Prompt (all SDL buttons, unique names, case-insensitive reload and labels):

```bat
cl /nologo /std:c++20 /EHsc /W4 /WX /I"upstream\src" /I"upstream\build\_deps\sdl-src\include" tests\wheel_button_names_test.cpp /Fo:"%TEMP%\outrun-button-names.obj" /Fe:"%TEMP%\outrun-button-names.exe"
if errorlevel 1 exit /b 1
"%TEMP%\outrun-button-names.exe"
```

This only uses headers/CRT; it neither links SDL nor accesses hardware.

Output: `upstream\build\bin\dinput8.dll` and its matching PDB. The DLL contains
Tweaks plus native FFB and RPM LEDs; it is not a second add-on beside another Tweaks DLL.
The corresponding prebuilt DLL is included at `runtime/dinput8.dll`; PDB symbols
are not distributed. Rebuilt bytes may differ because of compiler/SDK/debug paths/
timestamps. **Use the v0.2.0 DLL for the integrated contact/drift settings.**
Apply the complete patch to a clean pinned checkout, not on top of another patch.
I tested the integrated patch across three sessions and encountered no problems.
The included neutral-path DLL has byte-identical PE sections to that tested build; only
non-loaded debug-path data differs. Its upstream version/resource metadata
remains unchanged.

## 5. Install manually into a compatible game copy

1. Power off the wheel and close OutRun, FXT and all force/telemetry tools.
2. Use a legally owned, already working Tweaks-compatible C2C installation.
   The supported EXE SHA-256 is recorded in `manifest.json`. Check it using
   `Get-FileHash -Algorithm SHA256` in PowerShell. Stop on a mismatch. I do not
   provide an EXE replacement. Do not stack with FXT/WheelFfb.
3. Back up the game's DLL/PDB and existing FFB launcher to a separate folder;
   verify backup hashes. Back up saves/settings as a precaution.
4. Copy the included `runtime/dinput8.dll` beside `OR2006C2C.exe`, or use your
   freshly rebuilt DLL. For the included DLL, move any old `dinput8.pdb` to the
   backup folder: matching symbols are not bundled. If using your own rebuild,
   you may install its matching PDB instead.
   Copy the included `runtime/Play OutRun - MOZA R3 FFB.cmd` there, only after
   preserving any tuned launcher. Do not overwrite EXE, INIs or saves.
   Keep `LICENSE.md` and `THIRD-PARTY-NOTICES.txt` with redistributed builds.
5. With FFB and LEDs still disabled, use the copied launcher to test steering, pedals,
   buttons and paddles. Follow [Wheel button setup](runtime/WHEEL-BUTTONS.md) to
   assign controls, save them and check persistence after restarting. Click the
   game to focus it; close the F11 overlay before driving. Keyboard Enter/Escape
   remain available.
6. With Pit House/SimHub closed, test native LEDs with FFB still off using
   [RPM LED setup](runtime/NATIVE-RPM-LEDS.md). Follow README.md's secured-wheel/
   low-force procedure before enabling FFB. Keep rotation and driver settings unchanged.

The launcher supplies `UseNewInput=true`, `InputBackend=2`, a 2% input deadzone,
R3 identity/axis mapping and `VibrationMode=0`. Its overrides take precedence over
saved settings. Bare-EXE launch is not an equivalent configuration.

Read-only preview, without launching or accessing hardware:

```bat
"runtime\Play OutRun - MOZA R3 FFB.cmd" --check
```

## Editable FFB settings

Edit the **game-directory launcher**, save and restart. Fractions are DirectInput
command amplitude, not torque. Start at the shipped settings, not at the ceilings.

| Setting | Default | Range / meaning |
|---|---:|---|
| `NativeFfbEnabled` | false | Master switch |
| `NativeFfbStrength` | 0.01 | 0–1 centring; 0 silences all effects |
| `NativeFfbShiftStrength` | 0 | 0–1 gear pulse, 160ms / 300ms cooldown |
| `NativeFfbCollisionStrength` | 0 | 0–1 barrier pulse, 120ms / 500ms cooldown |
| `NativeFfbScrapeStrength` | 0 | 0–1 continuous barrier texture |
| `NativeFfbTrafficStrength` | 0 | 0–1 experimental traffic pulse |
| `NativeFfbTrafficScrapeStrength` | 0 | 0–1 experimental traffic contact texture |
| `NativeFfbDriftDampingPercent` | 0 | **0–100 percent reduction** of road texture; 20 = 20% less; 100 = silent road |
| `NativeFfbDriftEnter` / `NativeFfbDriftLeave` | 2000 / 1000 | Provisional absolute raw-D34 cuts; enter > leave; restart required |
| `NativeFfbDriftMinimumSpeed` | 0.1 | 0.01–10 raw speed floor, not km/h; restart required |
| `NativeFfbDriftFrequency` | 8 | 6–10 Hz for the existing road oscillator during estimated drift |
| `NativeFfbRoadStrength` | 0 | 0–1 smooth-road endpoint |
| `NativeFfbOffroadStrength` | 0 | 0–1 rough-surface endpoint |
| `NativeFfbRoadFullSpeed` | 1 | 0.05–10 raw-speed reference, not km/h |
| `NativeFfbCentre` | 0 | −0.25–0.25 physical centre calibration |
| `NativeFfbDeadzone` | 0.02 | 0–0.25 force deadzone, separate from input |
| `NativeFfbInvert` | false | Do not guess polarity; reversal can pull outward |
| `NativeFfbDiagnostics` | true | Logging only; not force enablement |

Collision probing stays disabled. Final output is hard-clamped to **50% DI** in
the live mixer and device backend; component overlap can still clip. Centring slew
remains 1000 DI units/second. The 100ms lease and software stop gates do not prove
real hardware expiry under a stalled game.

Damping is relative to the current road endpoints; no separate peak-strength
setting is used. At 20% reduction, 2%/8% road
becomes 1.6%/6.4%; changing normal endpoints retains the same percentage. Entry and
healthy recovery blend over 100ms with the existing road amplitude slew. Unknown
clears only the modifier; lifecycle stops reset immediately. Zero percent follows
the exact neutral road path. Centring/gear/contact/LED output is never damped by
this control. The percentage is also editable in the existing F11 settings UI.
Keep other force settings fixed when tuning it, and restart for launcher changes.

## Editable RPM LED settings

See [RPM LED setup](runtime/NATIVE-RPM-LEDS.md). The same launcher supplies
`NativeRpmLedsEnabled=false`, first/full thresholds of 4000/8000 RPM and diagnostic
logging. Enable LEDs explicitly and restart; keep Pit House/SimHub closed. No new
runtime dependency or MOZA SDK is installed.

## Rollback

Power off the wheel and close the game/force tools. Restore the backed-up DLL,
matching PDB (if any) and launcher together, verifying hashes. No INI/save restore
is required for these file replacements. Keep the project folder outside the game.

## Release validation record

The verifier checks DLL/source hashes, version, exact twenty-file patch scope,
50% cap, disabled FFB/LED/damping defaults and all 24 observed button mappings.
With `--upstream` it checks clean patch application, fake-COM/contact/drift/combined
and LED tests, a negative Windows exit guard and the launcher preview. Separate
C++ button-name and virtual SDL checks are described above. Toolchain/dependency
pins are unchanged; no capture, proprietary toolkit or physical wheel is required.

I tested the integrated all-effects patch across three sessions, including the
20%-damped drift preset, and encountered no problems. The neutral-path DLL's
PE sections are byte-identical to the tested build; only non-loaded debug-path
data differs. I consider this a hardware smoke validation, not universal detector
or torque certification. Crash/disconnect/expiry and long-session reliability remain
unverified.
I do not publish raw logs, captures, addresses, personal paths or game data as
evidence. `manifest.json` and `source/provenance.json` record the new binary hash
and the limited scope of component observations.
