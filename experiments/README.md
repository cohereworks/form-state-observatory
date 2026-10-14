# Experiment archive

Experiments are versioned and generally independent. Each retains its zero-JS demonstration and, where necessary, a separately instrumented diagnostic harness. Do not edit frozen human-observed versions to simplify later testing; fork new versions instead.

- `geometric-oracles/`: range/textarea geometry and CSS state probes; spec-derived, not established by browser tests.
- `font-state/v1/`: original human-tested font geometry, ordered encoding, scroll composition.
- `font-state/v2/`: generated fonts and diagnostics, GSUB `liga`/`calt`, variable-font `ADDR`, scroll-driven addressing.

Human feedback is provisional evidence. CI test results provide engine/version/OS-scoped observations, not universal conclusions. The machine-readable report is the evidence unit.
