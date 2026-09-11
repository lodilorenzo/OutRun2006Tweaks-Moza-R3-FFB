# Map wheel buttons in the game

Use the **updated DLL and launcher together** (see [BUILD.md](../BUILD.md)).
The old DLL can detect extended slots but displays "Unknown Button" and writes
empty binding names, so those assignments disappear when loaded again.

1. Back up your launcher and `OutRun2006Tweaks.input.ini` (if present) before editing.
   Keep FFB disabled for the input check. Close other input/force tools.
2. Start through `Play OutRun - MOZA R3 FFB.cmd`, not the bare EXE.
3. Open **Controls → Configuration**, or F11 → **Configure Input Bindings**.
   In **Controllers**, select **MOZA R3 OutRun**.
4. In **Bindings**, select an action, click **+ Add binding**, release all controls,
   then press and release the desired wheel button. Keep the wheel centred and
   pedals released while the editor listens. Click an existing binding to replace
   it; its adjacent **X** removes it without removing your keyboard fallback.
5. Click **Save bindings**. Return to the game, test the actions, then restart via
   the same launcher and check they persisted. Settings are saved in
   `OutRun2006Tweaks.input.ini` beside the game.

Useful actions: Start (pause), A (confirm), B/Back (back), Change View,
Gear Up/Down, Selection Up/Down/Left/Right, Music Next/Previous, HUD Toggle and
Overlay. Keep F11 bound as an emergency route back to the editor.

**Check duplicate actions:** upstream defaults also bind A/B to shifting,
Y to Change View, and Back to Music Next. Adding a button does not remove its
other bindings. Remove unwanted gamepad entries action by action, preserving
keyboard inputs. The live Reading indicator helps spot accidental duplicates.
Sign In/License menus may require the same buttons also bound to X/Y respectively.

## Button reference

These are **SDL slot names**, not claims about labels printed on your rim.
Physical button numbers below are zero-based SDL/DirectInput indexes; Windows
controller panels may show one-based numbers. Press the physical control you
want rather than guessing from an Xbox-style label.

| Raw button | Editor label (Xbox style) / saved name |
|---:|---|
| 0, 1, 2, 3 | A, B, X, Y |
| 4, 5 | Back, Start |
| 6, 7 | Left Bumper / LB, Right Bumper / RB |
| 18, 19 | LS / L3, RS / R3 |
| 20 | Guide |
| 21 | Misc 1 / Misc1 |
| 22 | Right Paddle 1 / Paddle1 |
| 23 | Left Paddle 1 / Paddle2 |
| 24 | Right Paddle 2 / Paddle3 |
| 31 | Left Paddle 2 / Paddle4 |
| 32 | Touchpad |
| 33–37 | Misc 2–6 / Misc2–Misc6 |
| 12 | Existing negative RS-Y slot (left shift paddle) |
| 13 | Existing positive RS-Y slot (right shift paddle) |

The labels Paddle1–4 above are spare **gamepad** slots, not the wheel's existing
shift paddles. The shift paddles remain on the two RS-Y halves to preserve saved
gear bindings. As before, opposing shift paddles share an axis: do not expect
independent simultaneous presses. The editor's existing RS-Y +/- display is
reversed; bind by pressing the paddle and check the action's live reading.

The driver reports 128 button slots. A live scan found the 24 listed above;
unobserved slots are not assigned. This uses every remaining SDL button slot
while retaining the original steering/pedals/shift-axis/hat mapping. Different
rims or Pit House modes can report different numbers. New buttons outside this
list require revising the slot mapping or adding raw-button support.

The existing hat-0 D-pad mapping is preserved, but **no hat events were observed**
in this scan. If your directional controls report buttons instead, bind them to
Selection Up/Down/Left/Right with the editor. Phantom raw axis 1 remains unmapped.

No steering, pedal, keyboard or saved action bindings are automatically rewritten.
No force settings need to be enabled to map buttons.
