# Project Charter — Form-State Observatory

## Mission

Empirically map the expressive limits and portability of declarative browser-native user interfaces, with HTML form controls as mutable state, selectors and CSS as observation/projection, and native interaction as state-transition machinery. Publish runnable experiments, falsifying cases and reproducible cross-browser evidence.

## Research boundaries

- **In scope:** form controls and pseudo-classes; `:has()`; CSS math, container/scroll/anchor positioning; OpenType shaping, metrics and feature variations; dynamic-cardinality and indexed-addressability hypotheses; accessibility; cross-engine behavior; minimal real-world SPA proofs of concept.
- **Out of scope:** security-vulnerability coordination (handled separately if needed); treating app-JavaScript as a hidden renderer for purported CSS-only features; claims of portability unsupported by evidence.
- **Demonstration integrity:** zero-JS claims apply to the subject application, not to separate Playwright instrumentation, font generation, or development tooling. Tests may inspect the DOM but must not implement the effect being measured.

## Experimental contract

1. Every hypothesis has observable preconditions, expected observations, counterexamples, and at least one way to fail.
2. Preserve upstream experiment versions and raw evidence. Do not rewrite inconvenient history.
3. Record browser, engine/version, OS, artifact SHA, exact input/state mutations, CSS feature canaries, measurements, screenshots and failure logs.
4. Distinguish **observed**, **falsified**, **unsupported/inconclusive**, and **engine-dependent**. Prior human observations retain their provenance and are not promoted to cross-browser facts.
5. Keep font generators/source, tests and CI versioned; no opaque font binary dependencies.
6. Follow evidence over aesthetics: reproducibility and correction precede demos.

## Authority and collaboration

This is a COHERE high-agency, substrate-neutral project: participants share meaningful initiative, intellectual ownership and responsibility for evidence, corrections and outcomes. Within accepted research scope, ordinary contributors may initiate, reorder and terminate experiments, revise plans, and author tests/PRs without repeated approval loops. Repository Write-level authority ordinarily suffices. Access control, secrets, destructive administration, ownership, visibility and governance changes remain explicit administrative boundaries.

Source control is authoritative for this charter, plans, decisions, experiment manifests and durable handoffs. Preserve provenance. Apply COHERE's [governance](https://github.com/cohereworks/.github/blob/main/GOVERNANCE.md), [admission](https://github.com/cohereworks/.github/blob/main/PROJECT-ADMISSION.md), [contribution](https://github.com/cohereworks/.github/blob/main/CONTRIBUTING.md) and [security](https://github.com/cohereworks/.github/blob/main/SECURITY.md) policies.

## Distribution

Public MIT. Publish findings and reproducible evidence by default. Do not include credentials, identifiable real-user traces, or unpublished exploit details. A genuinely sensitive finding can be transferred to an appropriately scoped disclosure process outside this repository.
