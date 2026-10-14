# Work Plan (authoritative)

## Baseline

- [x] Import the prior, independently authored geometric and font-state probes without erasing versions.
- [x] Capture v1 human results as *user reported*, not machine-verified: metric PASS; token undecoded; positional shaping PASS; scroll-to-font scaling PASS (corrected false negative).
- [x] Add original font generators and HarfBuzz verification source.
- [x] Add read-only cross-browser Playwright evidence collection and CI entry point.
- [ ] Inspect first Chromium, Firefox and WebKit Actions runs and classify each outcome with retained evidence.

## Hypotheses

- [ ] Determine why the token `liga` CSS decoder remains `unclassified` despite changing geometry; compare `calt` and text-editing contexts.
- [ ] Confirm/falsify CSS-selected `ADDR` variation changes browser shaping and width with the live string fixed.
- [ ] Confirm/falsify scroll-timeline → variable-font `ADDR` → glyph-width address gating in three engines.
- [ ] Assess textarea row-count vs line-identity observability and characterize layout/scroll constraints.
- [ ] Develop a small social scheduling SPA with form-state-only presentation changes after primitive capabilities are measured.

## CI gate semantics

Basic HTML reachability, event-driven editable control mutation and font generation are **required**. New browser feature experiments are **non-gating observations** until their preconditions and portability are established. Promote capabilities to explicit regression assertions only after reproducibility review. Preserve both successes and failures.
