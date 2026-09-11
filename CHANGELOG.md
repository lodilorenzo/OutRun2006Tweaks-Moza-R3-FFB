# Changelog

## v0.2.0

- Initial public release.
- Integrate continuous barrier scraping, experimental traffic impact/contact
  textures, and the drift estimate I tested with road damping.
- Add `NativeFfbDriftDampingPercent` (0–100): 20 reduces road feedback by 20% on
  every surface, independently of configured normal endpoints. Zero disables the
  modifier; 100 silences road during a fully blended drift. Centring, other effects
  and LEDs are not damped. No separate peak-strength setting is shipped.
- Retain phase-continuous road feedback, 100ms blend, conservative contact/unknown
  exclusion and neutral rearm, fresh-input/lifecycle stops and finite device lease.
- Use a hard **50% combined DI cap**. Individual strength settings retain their
  numeric meanings.
- Ship a rebuilt Win32 DLL, complete twenty-file patch, disabled force/LED/damping
  defaults, editable launcher controls and synthetic contact/drift/combined tests.
  Wheel mapping/buttons and the LED worker are included.
- I tested the integrated patch across three sessions, including the 20%-softer
  drift preset, and encountered no problems. The neutral-path DLL has byte-identical
  PE sections to the tested build; detector generalization and hang/expiry/disconnect
  safety remain unresolved.
- No water, landing or crash-animation effect is claimed. No private captures,
  game assets, user configurations or debug symbols are published.
