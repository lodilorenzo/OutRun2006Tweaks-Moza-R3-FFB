"""No-force regression: python tests/test_wheel_mapping.py [--sdl path/to/SDL3.dll]
Optional DLL must match Python's architecture. All physical SDL drivers are disabled.
"""
import argparse
import ctypes as C
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
# SDL enum order, including slots that previously could not be saved by Tweaks.
BUTTONS = 'a b x y back guide start leftstick rightstick leftshoulder rightshoulder dpup dpdown dpleft dpright misc1 paddle1 paddle2 paddle3 paddle4 touchpad misc2 misc3 misc4 misc5 misc6'.split()
OBSERVED = {0, 1, 2, 3, 4, 5, 6, 7, 12, 13, 18, 19, 20, 21, 22, 23, 24, 31, 32, 33, 34, 35, 36, 37}
EXTENDED = 'Guide Misc1 Paddle1 Paddle2 Paddle3 Paddle4 Touchpad Misc2 Misc3 Misc4 Misc5 Misc6'.split()


def check_mapping():
    text = (ROOT / 'runtime/Play OutRun - MOZA R3 FFB.cmd').read_text()
    mapping, = re.findall(r'^set "SDL_GAMECONTROLLERCONFIG=(.*)"$', text, re.M)
    guid, name, *fields = mapping.rstrip(',').split(',')
    assert guid == '0300ee506e3400000500000000000000'
    pairs = [field.split(':', 1) for field in fields]
    bindings = dict(pairs)
    assert len(pairs) == len(bindings), 'Duplicate SDL target'
    sources = [value for _, value in pairs if re.fullmatch(r'b\d+', value)]
    assert len(sources) == len(set(sources)) == 24, 'Duplicate/missing physical button'
    assert {int(value[1:]) for value in sources} == OBSERVED
    for key, value in {'a': 'b0', 'b': 'b1', 'leftx': 'a0', 'righttrigger': 'a2',
                       'lefttrigger': 'a5', '+righty': 'b13', '-righty': 'b12',
                       'dpup': 'h0.1', 'dpright': 'h0.2', 'dpdown': 'h0.4',
                       'dpleft': 'h0.8', 'platform': 'Windows'}.items():
        assert bindings[key] == value, key
    assert set(bindings) == set(BUTTONS) | {'leftx', 'righttrigger', 'lefttrigger', '+righty', '-righty', 'platform'}
    assert not any('a1' in value for value in bindings.values()), 'Phantom Y mapped'
    patch = (ROOT / 'source/native-ffb.patch').read_text()
    for name in EXTENDED:
        assert re.search(r'^\+\s*\{ SDL_GAMEPAD_BUTTON_\w+,\s*"' + name + r'",\s*"[^"]+"', patch, re.M), name
    print('PASS: all 24 observed buttons mapped uniquely; old controls retained; extended save/display names present.')
    return mapping, bindings


def check_virtual(dll, mapping, bindings):
    sdl = C.CDLL(str(dll.resolve()))

    def api(name, result, *args):
        fn = getattr(sdl, 'SDL_' + name)
        fn.restype, fn.argtypes = result, args
        return fn

    hint = api('SetHint', C.c_bool, C.c_char_p, C.c_char_p)
    error = api('GetError', C.c_char_p)
    for driver in ('HIDAPI', 'RAWINPUT', 'WGI', 'DIRECTINPUT', 'GAMEINPUT'):
        # Leave only the virtual driver; never open a physical joystick here.
        assert hint(('SDL_JOYSTICK_' + driver).encode(), b'0')
    assert hint(b'SDL_XINPUT_ENABLED', b'0')
    assert hint(b'SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS', b'1')
    init = api('Init', C.c_bool, C.c_uint32)
    quit_sdl = api('Quit', None)
    assert init(0x2000), error()

    class Desc(C.Structure):
        _fields_ = [('version', C.c_uint32)] + [(name, C.c_uint16) for name in (
            'type', 'padding', 'vendor', 'product', 'naxes', 'nbuttons', 'nballs', 'nhats',
            'ntouchpads', 'nsensors', 'padding2a', 'padding2b')] + [
            ('button_mask', C.c_uint32), ('axis_mask', C.c_uint32), ('name', C.c_char_p)] + [
            (name, C.c_void_p) for name in ('touchpads', 'sensors', 'userdata', 'Update',
            'SetPlayerIndex', 'Rumble', 'RumbleTriggers', 'SetLED', 'SendEffect', 'SetSensorsEnabled', 'Cleanup')]

    class Guid(C.Structure):
        _fields_ = [('data', C.c_ubyte * 16)]

    attach = api('AttachVirtualJoystick', C.c_uint32, C.POINTER(Desc))
    detach = api('DetachVirtualJoystick', C.c_bool, C.c_uint32)
    open_joy = api('OpenJoystick', C.c_void_p, C.c_uint32)
    close_joy = api('CloseJoystick', None, C.c_void_p)
    open_pad = api('OpenGamepad', C.c_void_p, C.c_uint32)
    close_pad = api('CloseGamepad', None, C.c_void_p)
    guid = api('GetJoystickGUID', Guid, C.c_void_p)
    add_mapping = api('AddGamepadMapping', C.c_int, C.c_char_p)
    set_button = api('SetJoystickVirtualButton', C.c_bool, C.c_void_p, C.c_int, C.c_bool)
    set_axis = api('SetJoystickVirtualAxis', C.c_bool, C.c_void_p, C.c_int, C.c_int16)
    set_hat = api('SetJoystickVirtualHat', C.c_bool, C.c_void_p, C.c_int, C.c_uint8)
    get_button = api('GetGamepadButton', C.c_bool, C.c_void_p, C.c_int)
    get_axis = api('GetGamepadAxis', C.c_int16, C.c_void_p, C.c_int)
    update = api('UpdateJoysticks', None)
    jid = joy = pad = None
    try:
        desc = Desc(version=C.sizeof(Desc), type=2, naxes=8, nbuttons=128, nhats=1, name=b'OutRun virtual wheel test')
        jid = attach(C.byref(desc))
        assert jid, error()
        joy = open_joy(jid)
        assert joy, error()
        virtual_mapping = bytes(guid(joy).data).hex() + ',' + mapping.split(',', 1)[1]
        assert add_mapping(virtual_mapping.encode()) >= 0, error()
        pad = open_pad(jid)
        assert pad, error()
        for axis in (1, 2, 5):
            assert set_axis(joy, axis, -32768)
        update()
        targets = {int(value[1:]): BUTTONS.index(key) for key, value in bindings.items()
                   if key in BUTTONS and value.startswith('b')}
        # Test every advertised raw slot: unused slots must do nothing.
        for raw in range(128):
            for down in (True, False):
                assert set_button(joy, raw, down)
                update()
                assert [i for i in range(26) if get_button(pad, i)] == ([targets[raw]] if down and raw in targets else []), raw
                expected_shift = (32767 if raw == 13 else -32768 if raw == 12 else 0) if down else 0
                assert get_axis(pad, 3) == expected_shift, raw
        for raw in targets:
            assert set_button(joy, raw, True)
        update()
        assert all(get_button(pad, target) for target in targets.values()), 'Simultaneous buttons lost'
        for raw in targets:
            assert set_button(joy, raw, False)
        for hat in (0, 1, 2, 3, 4, 6, 8, 9):
            assert set_hat(joy, 0, hat)
            update()
            for key, mask in (('dpup', 1), ('dpright', 2), ('dpdown', 4), ('dpleft', 8)):
                assert get_button(pad, BUTTONS.index(key)) == bool(hat & mask)
        for raw in (-32768, 0, 32767):
            for axis in (0, 2, 5):
                assert set_axis(joy, axis, raw)
            update()
            assert get_axis(pad, 0) == raw
            assert get_axis(pad, 1) == get_axis(pad, 2) == 0, 'Phantom axis leaked'
            assert abs(get_axis(pad, 4) - (raw + 32768) // 2) <= 1
            assert abs(get_axis(pad, 5) - (raw + 32768) // 2) <= 1
        print('PASS: virtual SDL wheel: 128 slots, press/release, simultaneous buttons, paddles, hats and axes. No forces.')
    finally:
        if pad:
            close_pad(pad)
        if joy:
            close_joy(joy)
        if jid:
            detach(jid)
        quit_sdl()


if __name__ == '__main__':
    if not __debug__:
        raise SystemExit('Run without -O: tests require assertions.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdl', type=Path)
    args = parser.parse_args()
    mapping, bindings = check_mapping()
    if args.sdl:
        check_virtual(args.sdl, mapping, bindings)
