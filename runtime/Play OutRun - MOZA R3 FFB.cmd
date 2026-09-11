@echo off
setlocal DisableDelayedExpansion
rem OutRun 2006 Wheel and FFB v0.2.0 - contact textures and drift damping included.
rem Defaults: FFB and LEDs disabled, 1% centring, accents off. Read README.md.
rem Read project README.md before enabling or changing force settings.
rem EDIT SETTINGS BELOW in Notepad, save, then restart the game.
rem Strengths are fractions: 0.01 = 1 percent, 0.10 = 10 percent.
rem These are DirectInput commands, NOT measured wheel torque.
rem Component strengths allow 0..1; final combined output is hard-capped at 50 percent.
rem Drift damping uses 0..100 PERCENT REDUCTION, not a force strength.
rem Start with shipping defaults; no physical safety certification is implied.

rem Master switch: false disables ALL native game forces.
set "NativeFfbEnabled=false"
rem Centring: 0..1. IMPORTANT: 0 also silences every other effect.
set "NativeFfbStrength=0.01"
rem Gear changes: 0..1, 0 disables. 160ms two-sided pulse, 300ms cooldown.
set "NativeFfbShiftStrength=0"
rem Collisions: 0..1, 0 disables. 120ms two-sided pulse, 500ms cooldown.
rem Uses captured contact flags; does not infer left/right wall direction.
set "NativeFfbCollisionStrength=0"
rem Continuous wall/traffic scraping and traffic impact, 0..1; all disabled by default.
set "NativeFfbScrapeStrength=0"
set "NativeFfbTrafficStrength=0"
set "NativeFfbTrafficScrapeStrength=0"
rem Surface endpoints: 0..1 each, blended by contact type and speed.
rem Set BOTH to 0 to disable surface rumble. Start with both off.
set "NativeFfbRoadStrength=0"
set "NativeFfbOffroadStrength=0"
rem Raw-speed reference at full rumble: 0.05..10, NOT km/h.
rem Higher values make rumble build more slowly with speed.
set "NativeFfbRoadFullSpeed=1"

rem Drift ROAD damping: 20 means 20 percent less on every surface; 100 silences road.
rem 0 disables the drift modifier; centring, gear and contact effects are unaffected.
set "NativeFfbDriftDampingPercent=0"
rem Experimental raw-D34 cuts, not slip-angle units. Enter MUST exceed Leave.
set "NativeFfbDriftEnter=2000"
set "NativeFfbDriftLeave=1000"
set "NativeFfbDriftMinimumSpeed=0.1"
rem Existing road oscillator frequency during estimated drift: 6..10 Hz.
set "NativeFfbDriftFrequency=8"

rem Calibration: centre -0.25..0.25, force deadzone 0..0.25.
rem This does not change the separate steering-input deadzone.
set "NativeFfbCentre=0"
set "NativeFfbDeadzone=0.02"
rem Leave polarity unchanged; reversing it can pull AWAY from centre.
set "NativeFfbInvert=false"
rem true retains test logging; false reduces effect logging for long sessions.
set "NativeFfbDiagnostics=true"

rem Native R3 + ES RPM LEDs. Leave Pit House and SimHub CLOSED while enabled.
rem Test LEDs first with NativeFfbEnabled=false; see runtime/NATIVE-RPM-LEDS.md.
rem No rotation, firmware, calibration or force-preset commands are sent.
set "NativeRpmLedsEnabled=false"
set "NativeRpmLedsFirstRpm=4000"
set "NativeRpmLedsFullRpm=8000"
set "NativeRpmLedsDiagnostics=true"

rem END OF EDITABLE SETTINGS. Preserve the R3 identity and physical axes.
rem Physical axes: steering 0, accelerator 2, brake 5; phantom raw Y unmapped.
rem All 24 buttons observed in the wheel scan are exposed, not all 128 driver slots.
rem Requires the updated DLL for extended-button labels and saved bindings.
rem Assign actions in Controls - Configuration, then click Save bindings.
rem SDL slot labels are NOT physical rim labels; see runtime/WHEEL-BUTTONS.md.
set "SDL_GAMECONTROLLERCONFIG=0300ee506e3400000500000000000000,MOZA R3 OutRun,a:b0,b:b1,leftx:a0,righttrigger:a2,lefttrigger:a5,+righty:b13,-righty:b12,dpup:h0.1,dpright:h0.2,dpdown:h0.4,dpleft:h0.8,x:b2,y:b3,back:b4,start:b5,leftshoulder:b6,rightshoulder:b7,leftstick:b18,rightstick:b19,guide:b20,misc1:b21,paddle1:b22,paddle2:b23,paddle3:b24,paddle4:b31,touchpad:b32,misc2:b33,misc3:b34,misc4:b35,misc5:b36,misc6:b37,platform:Windows,"
set "FFB_ARGS=-UseNewInput=true -InputBackend=2 -SteeringDeadZone=0.02 -VibrationMode=0 -NativeFfbVendorId=13422 -NativeFfbProductId=5 -NativeFfbCollisionDiagnostics=false"
set FFB_ARGS=%FFB_ARGS% "-NativeFfbEnabled=%NativeFfbEnabled%" "-NativeFfbStrength=%NativeFfbStrength%" "-NativeFfbShiftStrength=%NativeFfbShiftStrength%" "-NativeFfbCollisionStrength=%NativeFfbCollisionStrength%" "-NativeFfbRoadStrength=%NativeFfbRoadStrength%" "-NativeFfbOffroadStrength=%NativeFfbOffroadStrength%" "-NativeFfbRoadFullSpeed=%NativeFfbRoadFullSpeed%" "-NativeFfbCentre=%NativeFfbCentre%" "-NativeFfbDeadzone=%NativeFfbDeadzone%" "-NativeFfbInvert=%NativeFfbInvert%" "-NativeFfbDiagnostics=%NativeFfbDiagnostics%"

set FFB_ARGS=%FFB_ARGS% "-NativeFfbScrapeStrength=%NativeFfbScrapeStrength%" "-NativeFfbTrafficStrength=%NativeFfbTrafficStrength%" "-NativeFfbTrafficScrapeStrength=%NativeFfbTrafficScrapeStrength%" "-NativeFfbDriftDampingPercent=%NativeFfbDriftDampingPercent%" "-NativeFfbDriftEnter=%NativeFfbDriftEnter%" "-NativeFfbDriftLeave=%NativeFfbDriftLeave%" "-NativeFfbDriftMinimumSpeed=%NativeFfbDriftMinimumSpeed%" "-NativeFfbDriftFrequency=%NativeFfbDriftFrequency%"

set FFB_ARGS=%FFB_ARGS% "-NativeRpmLedsEnabled=%NativeRpmLedsEnabled%" "-NativeRpmLedsFirstRpm=%NativeRpmLedsFirstRpm%" "-NativeRpmLedsFullRpm=%NativeRpmLedsFullRpm%" "-NativeRpmLedsDiagnostics=%NativeRpmLedsDiagnostics%"

rem Read-only command preview for checks; no launch, file writes or hardware access.
if /i "%~1"=="--check" (
    echo SDL_GAMECONTROLLERCONFIG=%SDL_GAMECONTROLLERCONFIG%
    echo "%~dp0OR2006C2C.exe" %FFB_ARGS%
    exit /b 0
)
if not "%~1"=="" exit /b 2
pushd "%~dp0" || exit /b 1
if not exist "OR2006C2C.exe" goto failed
if not exist "dinput8.dll" goto failed
if exist "..\.native-test.lock" goto failed
powershell.exe -NoProfile -Command "$ErrorActionPreference='Stop'; try { if (Get-Process | Where-Object ProcessName -in 'OR2006C2C','OR2FXT') { exit 1 }; exit 0 } catch { exit 1 }"
if errorlevel 1 goto failed

if /i "%NativeRpmLedsEnabled%"=="true" (
    powershell.exe -NoProfile -Command "$ErrorActionPreference='Stop'; try { if (Get-Process | Where-Object ProcessName -in 'MOZA Pit House','SimHub') { exit 1 }; exit 0 } catch { exit 1 }"
    if errorlevel 1 goto failed
)

echo Wheel and FFB v0.2.0 - experimental feedback; rebuilt combined version awaits hardware validation.
echo Native RPM LEDs enabled: %NativeRpmLedsEnabled% - Pit House/SimHub must stay closed.
echo Native FFB enabled: %NativeFfbEnabled% - no play timer, no temporary DLL swap.
echo HARD 50%% combined DI cap. Drift road damping: %NativeFfbDriftDampingPercent%%% reduction.
echo Start with forces OFF; enable and test one effect at low strength first.
echo Secure wheel, clear travel, keep power-off accessible; Pit House output 10%% or less.
echo Close other force tools. If the game hangs or force fails to stop, POWER WHEEL OFF.
echo Stalled-update expiry and disconnect behavior remain unverified.
echo Press any key to play, or Ctrl+C to cancel.
pause >nul
start "" /wait "OR2006C2C.exe" %FFB_ARGS%
set "result=%errorlevel%"
popd
exit /b %result%

:failed
echo Cannot launch: missing files, active test lock, another game, process check failed, or Pit House/SimHub open with LEDs enabled.
popd
pause
exit /b 1
