// Compile with the patched upstream src and pinned SDL include directories.
// No SDL library, game or hardware is needed: only the actual naming functions.
#define _CRT_NONSTDC_NO_DEPRECATE // Upstream uses the POSIX spelling stricmp.
#include "input_names.hpp"
#include <cassert>
#include <set>

int main()
{
    std::set<std::string> names;
    for (int i = 0; i < SDL_GAMEPAD_BUTTON_COUNT; ++i)
    {
        const auto button = static_cast<SDL_GamepadButton>(i);
        const auto name = InputNames::iniNameForButton(button);
        assert(!name.empty() && names.insert(name).second);
        assert(InputNames::buttonFromIni(name) == button);
        for (auto type : { SDL_GAMEPAD_TYPE_XBOX360, SDL_GAMEPAD_TYPE_PS5, SDL_GAMEPAD_TYPE_NINTENDO_SWITCH_PRO })
        {
            const auto display = InputNames::displayNameForButton(button, type);
            assert(!display.empty() && display != "Unknown Button");
        }
    }
    assert(!InputNames::buttonFromIni("not-a-button"));
    assert(InputNames::buttonFromIni("mIsC6") == SDL_GAMEPAD_BUTTON_MISC6);
}
