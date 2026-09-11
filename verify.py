"""Verify the DLL/source release; optionally reconstruct/test using a local upstream Git repo.
python verify.py
python verify.py --upstream upstream
No game launch, real device access, network access or checkout edits.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
PATCH_FILES = {
    'CMakeLists.txt', 'cmake.toml', 'src/hooks_forcefeedback.cpp',
    'src/input_manager.cpp', 'src/input_manager.hpp', 'src/input_names.hpp', 'src/overlay/hooks_overlay.cpp',
    'src/native_ffb.hpp', 'tests/native_ffb_test.cpp', 'tests/run-native-ffb-tests.cmd',
    'src/native_rpm_leds.cpp', 'src/native_rpm_leds.hpp',
    'tests/native_rpm_leds_test.cpp', 'tests/run-native-rpm-led-tests.cmd',
    'src/contact_models.hpp', 'tests/contact_models_test.cpp', 'tests/run-contact-tests.cmd',
    'tests/legacy_road.hpp', 'tests/drift_feedback_test.cpp', 'tests/combined_effects_test.cpp',
}


def main():
    if not __debug__:
        raise SystemExit('Run without -O: verification requires assertions.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', type=Path, help='Local Git repo containing the pinned commit')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    assert (ROOT / 'VERSION').read_text().strip() == manifest['version'] == manifest['release_tag'].removeprefix('v') == '0.2.0'
    assert manifest['hardware_validated'] is True
    assert 'runtime/dinput8.dll' in manifest['files_sha256'], 'Missing binary hash'
    for relative, expected in manifest['files_sha256'].items():
        path = (ROOT / relative).resolve()
        assert path.is_relative_to(ROOT), f'Invalid manifest path: {relative}'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, f'Hash mismatch: {relative}'
    provenance = json.loads((ROOT / 'source/provenance.json').read_text())
    assert provenance['base_commit'] == manifest['upstream_commit']
    assert provenance['hardware_validated'] == manifest['hardware_validated']
    assert provenance['combined_directinput_cap'] == manifest['combined_directinput_cap'] == 5000
    patch = ROOT / 'source/native-ffb.patch'
    assert hashlib.sha256(patch.read_bytes()).hexdigest() == provenance['patch_sha256']
    assert set(re.findall(r'^\+\+\+ b/(.+)$', patch.read_text(), re.M)) == PATCH_FILES
    launcher = ROOT / 'runtime/Play OutRun - MOZA R3 FFB.cmd'
    text = launcher.read_text()
    defaults = manifest['shipping_force_defaults'] | manifest['shipping_led_defaults']
    assert defaults['NativeFfbEnabled'] == defaults['NativeRpmLedsEnabled'] == 'false'
    assert all(defaults[key] == '0' for key in ('NativeFfbScrapeStrength', 'NativeFfbTrafficStrength',
        'NativeFfbTrafficScrapeStrength', 'NativeFfbDriftDampingPercent'))
    assert 'NativeFfbDriftPeakStrength' not in text, 'Private trial peak setting must not ship'
    for key, expected in defaults.items():
        assert re.findall(rf'^set "{key}=(.*)"$', text, re.M) == [expected], key
    assert 'leftx:a0,righttrigger:a2,lefttrigger:a5' in text and ':a1,' not in text
    assert '-UseNewInput=true -InputBackend=2 -SteeringDeadZone=0.02 -VibrationMode=0' in text
    subprocess.run([sys.executable, str(ROOT / 'tests/test_wheel_mapping.py')], check=True)
    print('PASS: v0.2.0 DLL/source hashes, provenance, twenty-file patch, 50% cap and FFB/LED/damping-disabled R3 launcher.')
    if not args.upstream:
        return

    exported = subprocess.check_output([
        'git', '-C', str(args.upstream.resolve()), 'archive', '--format=zip',
        manifest['upstream_commit'],
    ])
    with tempfile.TemporaryDirectory(prefix='outrun-wheel-ffb-source-') as temp:
        source = Path(temp)
        with zipfile.ZipFile(io.BytesIO(exported)) as archive:
            for name in archive.namelist():
                assert (source / name).resolve().is_relative_to(source), 'Unsafe source archive path'
            archive.extractall(source)
        for option in (['--check', '--whitespace=error-all'], []):
            subprocess.run(['git', '-C', str(source), 'apply', *option, str(patch)], check=True)
        for test in ('run-contact-tests.cmd', 'run-native-rpm-led-tests.cmd'):
            subprocess.run(['cmd.exe', '/d', '/c', str(source / 'tests' / test)],
                           check=True, timeout=240)
        negative = subprocess.run(['cmd.exe', '/d', '/c', str(source / 'tests/run-contact-tests.cmd'), '--self-fail'],
                                  capture_output=True, text=True, timeout=240)
        assert negative.returncode != 0 and 'HARD 50% DEVICE CAP' in negative.stdout, 'Negative Windows exit guard failed'
        preview = subprocess.run(['cmd.exe', '/d', '/c', str(launcher), '--check'],
                                 check=True, capture_output=True, text=True, timeout=10)
        pairs = re.findall(r'-([A-Za-z0-9]+)=([^\s"]+)', preview.stdout)
        values = dict(pairs)
        assert len(pairs) == len(values), 'Duplicate launcher argument'
        for key, expected in defaults.items():
            assert values[key] == expected, key
        assert values['UseNewInput'] == 'true' and values['InputBackend'] == '2'
        assert values['VibrationMode'] == '0'
    print('PASS: clean pinned-source patch application, actual C++ tests and launcher preview. No game/hardware access.')


if __name__ == '__main__':
    main()
