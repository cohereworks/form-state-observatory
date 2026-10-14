# CSS live-state font probes

This is a deliberately pathological proof-of-concept: use OpenType shaping and font metrics as a deterministic transducer from otherwise-unreadable live form-control values into geometry that CSS can observe.

## Run

```bash
python -m pip install -r requirements.txt
python generate_fonts.py
python -m http.server 8000
```

Open `http://localhost:8000/` in a current Chromium/Safari/Firefox build.

The generated font binaries are intentionally not checked into this bundle. `generate_fonts.py` is the source of truth and emits them under `generated/`.

## Probes

1. **ProbeMetric** — every printable ASCII glyph advances exactly 1em. With `field-sizing: content`, live input width encodes character count.
2. **ProbeToken** — GSUB ligatures map `ALICE`, `BOB`, `CAROL`, `DAVE` to synthetic glyphs with advances 8, 12, 16, 20em. This is direct bounded text → numeric geometry.
3. **ProbeContext** — contextual GSUB substitutions encode the order and position of `A/B/C` after a `^` sentinel. The mapping is injective over `^[ABC]{1,3}`. Examples verified through HarfBuzz:
   - `^A` → 2.5em
   - `^B` → 3em
   - `^C` → 3.5em
   - `^AB` → 6.5em
   - `^BA` → 5em
   - `^ABC` → 30.5em
   - `^CBA` → 15.5em
4. **Scroll × font** — a scroll timeline drives font size while a shaped token supplies a deterministic em coefficient. This composes two independent browser-maintained state channels into geometry.

## What this proves

The browser does not need to expose `input.value` to CSS for bounded values to become CSS-observable. A font can implement a finite transducer:

```text
live control text
    ↓
OpenType GSUB/contextual shaping
    ↓
synthetic glyph sequence
    ↓
hmtx advances
    ↓
intrinsic control geometry
    ↓
anchor-size()
    ↓
container-query predicates
```

The contextual font is the important probe: it demonstrates **order-sensitive** encoding, not merely length or a character multiset.

## Known boundary

This still does not expose an arbitrary textarea line as an independently addressable object. Scroll gives us an address register; the remaining hard problem is projecting the addressed substring/line into its own shaping/layout channel.

A promising next experiment is a custom variable-font axis controlled by scroll position, combined with OpenType FeatureVariations/contextual rules, to test whether the selected address can gate which token contributes geometric signal.
