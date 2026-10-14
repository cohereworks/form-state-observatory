# CSS form-state oracle — v2 (diagnostic + variable-address experiment)

This revision responds to real browser observations:

- **#1 PASS**: monospace geometry/classifier tracks 1–8 characters.
- **#2 INCOMPLETE**: input geometry changes; `liga` token decoding never classifies. Do not infer that GSUB ligatures successfully apply in the browser. Added probe **2b**, which places identical token substitutions in `calt` rather than `liga`.
- **#3 PASS for supported examples**: contextual glyph advances differentiate ordering. Fixed the `^`/`^A` decoder interval overlap.
- **#4 FAIL**: original scroll × font composition did not respond in user's browser. Kept intact as a legacy negative test.

## Run

```sh
python -m pip install -r requirements.txt
python generate_fonts.py
python -m http.server 8000
```

Open `http://localhost:8000/index.html` (zero JavaScript) and `http://localhost:8000/diagnostics.html` (read-only JavaScript diagnostics via iframe).

**The package contains generator source, not font binaries.** The build creates files under `generated/` locally.

## New experiments

- **2b**: Test `calt` token substitution to determine if `liga` is special-cased in text editing. The console-free diagnostics page reveals actual measured widths and computed fonts. Avoid inferring shaping from visible boxes.
- **5**: Independently test CSS → custom variable-font `ADDR` axis → GSUB FeatureVariations → changing glyph geometry → CSS classified state. The live value stays `^ABC`; native radio controls select address 1, 2, or 3. HarfBuzz shaping verification at `ADDR=1/2/3`: 5em / 9em / 13em. This only shows *positional addressability within a bounded, synthetically encoded string*. It does NOT prove arbitrary textarea-line selection.
- **6**: Decouple the named scroll timeline from the animated font. A fixed scroll scroller and animated readouts are siblings under `timeline-scope`. Test in order: scroll progress bar, token font-size, variable axis, and resulting geometry. If the progress bar doesn't move, stop debugging the font.

## Local verification

`python verify_shaping.py` uses system HarfBuzz (via ctypes, no pip package required); tested against `libharfbuzz.so.0` on Linux. On Windows this utility is optional; the font generator runs with only requirements.txt dependencies. Browser rendering has *not* been runtime-verified in this environment because Chromium navigations are administratively blocked.

| Font | Test | Result |
|---|---|---|
| ProbeMetric | 1em advances | constructed |
| ProbeToken | `liga(ALICE)` | 8em (HarfBuzz) |
| ProbeTokenContext | `calt(ALICE)` | 8em (HarfBuzz) |
| ProbeContext | `^AB` / `^BA` | 6.5em / 5em (HarfBuzz) |
| ProbeAddress | `^ABC` at axis 0 | 4em (HarfBuzz) |
| ProbeAddress | `^ABC` at axis 1 | 5em (HarfBuzz) |
| ProbeAddress | `^ABC` at axis 2 | 9em (HarfBuzz) |
| ProbeAddress | `^ABC` at axis 3 | 13em (HarfBuzz) |

## Boundaries and next gate

The axis implementation performs contextual glyph labeling followed by variation-dependent substitution to make *only the selected position* contribute width. Browser support of the generated `fvar`/`GSUB.FeatureVariations` tables must be measured before treating this as an interoperable CSS mechanism.

When testing, record outcomes for **2b, 5 (manual), 6 (progress / scale / address)** and diagnostics widths when a classifier says `unclassified`. Native DOM mutation/radio selection is the only state driver in the zero-JS page.
