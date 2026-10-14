# Browser evidence: 2026-10-14

Project: [Form-State Observatory](../../README.md) · PR [#1](https://github.com/cohereworks/form-state-observatory/pull/1)

## Verified runs and provenance

- [Run 38514504623](https://github.com/cohereworks/form-state-observatory/actions/runs/38514504623): initial cross-browser feature evidence, commit `33cf4d6`.
- [Run 38514743061](https://github.com/cohereworks/form-state-observatory/actions/runs/38514743061): fixed inconclusive classifier and static container canary, commit `ec67fa2`.
- [Run 38514985655](https://github.com/cohereworks/form-state-observatory/actions/runs/38514985655): five-case static differential, commit `d0846ef`.
- [Run 38515205128](https://github.com/cohereworks/form-state-observatory/actions/runs/38515205128): dynamic anchored-container invalidation, head commit `838809b`; Actions source merge SHA `898254bb0ee69feae8610fad88a1492f413055ed`.

Each run executed separate Chromium, Firefox, and WebKit Playwright jobs. The tests preserve structured `evidence.json`, screenshots, traces, font asset hashes, runtime feature detection and browser versions. Artifacts in Actions have a 30-day retention setting: **this report is durable, but does not replace the full artifacts**.

## Run 38515205128 summary

| Observation | Chromium 156.0.8078.4 | Firefox 157.0 | WebKit 27.2 |
|---|---|---|---|
| Metric glyph count via font geometry | observed | observed | geometry observed, CSS label failed |
| Known-token shaping (`liga` and `calt`) | observed | observed | shaping observed, CSS label failed |
| Contextual order-sensitive shaping | observed | observed | observed |
| Manual `ADDR` FeatureVariations selection | observed (60/108/156px) | observed (60/108/156px) | observed (~60/108/156px) |
| Scroll timeline → `ADDR` → geometry | observed (48→156px) | inconclusive: prerequisites unavailable | observed (~48→156px) |
| Static ordinary/absolute/anchor-positioned/anchor-sized container queries | 5/5 matched | 5/5 matched | 5/5 matched |
| Dynamic input→anchor-size→container query invalidation | passed | passed | **width changed, query failed to update** |

The Firefox scroll result is **not a falsification**: `CSS.supports('animation-timeline:scroll()')` and `CSS.supports('timeline-scope:--probe')` were false. A bug in an earlier runner version incorrectly discarded this prerequisite and was repaired before the final run.

### Dynamic canary

Native input edits: `A → ABCDEFGH → A` with field-sizing and a probe metric font.

- Chromium / Firefox: width `16 → 128 → 16px`, `@container` readout `unmatched → matched → unmatched`.
- WebKit: width `16.015625 → 128.015625 → 16.015625px`, `@container` readout **`unmatched → unmatched → unmatched`**.
- Each static canary, including combined `position-anchor` and `anchor-size()`, matched correctly in all three engines. The observed discrepancy is associated with **live geometry/query invalidation**, not general support for these features.

See [issue #2](https://github.com/cohereworks/form-state-observatory/issues/2) for reduction and upstream-reporting criteria. Do not treat an apparent engine bug as a standards violation until containment and anchor rules have been checked.

## Research status / limits

The verified finite-domain computation is the mapping from browser-maintained input and scroll state, through OpenType shaping or variable-font features, into observable numeric geometry. This **does not yet demonstrate arbitrary live-text decomposition**, dynamic DOM schema allocation, or general SPA equivalence. Browser support is not uniform.

The probe HTML is zero-JavaScript; Playwright-driven user edits and evidence capture are instrumentation only. User reports from the earlier Chrome suite remain separately attributed, not silently converted into CI evidence.

## Artifact ZIP snapshots (as retrieved from Actions)

- Chromium: SHA-256 `033464109e680002062ef40b5bcdb86bccfac5c354fa76df996746393e8e0913`
- Firefox: SHA-256 `8eef0b98055b48c3e6639baadad4d91cfffebca0153b228cbc692ef56d16ab3f`
- WebKit: SHA-256 `577ffa94003420067c99d842e11e1d602d8cac9d3f274d126622772f687e99c7`

These hashes attest the exact downloaded ZIP byte streams, not a permanently published artifact. Keep source, CI output and screenshots linked by run IDs until durable storage is added.
