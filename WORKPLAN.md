# Work Plan (authoritative)

## Baseline

- [x] Import the prior, independently authored geometric and font-state probes without erasing versions.
- [x] Capture v1 human results as *user reported*, not machine-verified: metric PASS; token undecoded; positional shaping PASS; scroll-to-font scaling PASS (corrected false negative).
- [x] Add original font generators and HarfBuzz verification source.
- [x] Add read-only cross-browser Playwright evidence collection and CI entry point.
- [x] Inspect Chromium, Firefox and WebKit Actions runs, correct prerequisite classification, and record results in [2026-10-14 browser evidence](docs/results/2026-10-14-browser-evidence.md).

## First automated findings

- [x] Cross-engine native font shaping, order-sensitive geometry, and manual variable-font `ADDR` addressing confirmed by CI.
- [x] Scroll → `ADDR` → geometry confirmed in Chromium and WebKit; Firefox reports unsupported prerequisites, not falsification.
- [x] WebKit dynamic `anchor-size()`/container-query invalidation discrepancy isolated; track reduction in [issue #2](https://github.com/cohereworks/form-state-observatory/issues/2).
- [x] Publish per-engine GitHub Actions summaries without converting non-gating research hypotheses into required tests.
- [ ] Preserve machine-readable evidence beyond GitHub Actions' 30-day artifact retention without broadening untrusted PR workflow privileges.

## Hypotheses

- [x] Distinguish token shaping from CSS classification: both `liga` and `calt` decode successfully in Chromium/Firefox, but WebKit records correct geometric widths while its anchored container-query labels remain `unclassified`.
- [x] Confirm CSS-selected `ADDR` variation changes browser shaping and width with the live string fixed in Chromium, Firefox, and WebKit.
- [x] Observe scroll-timeline → `ADDR` → glyph-width address gating in Chromium and WebKit; Firefox lacks the required timeline/scope features. Do not count unsupported as falsified.
- [ ] Assess textarea row-count vs line-identity observability and characterize layout/scroll constraints.
- [ ] Develop a small social scheduling SPA with form-state-only presentation changes after primitive capabilities are measured.

## CI gate semantics

Basic HTML reachability, event-driven editable control mutation and font generation are **required**. New browser feature experiments are **non-gating observations** until their preconditions and portability are established. Promote capabilities to explicit regression assertions only after reproducibility review. Preserve both successes and failures.
