# Changelog

## 0.1.0

Initial release — a **complete, faithful Python port** of the SpecForge
`@specforge/assayforge` work-session completion gate.

- `assay(context, options) → AssayResult`: four independent checks
  (`acceptance-coverage`, `implementation-coverage`, `file-action-coverage`,
  `test-result-presence`) over the normalized work-session event tables, then a
  single gate `passed = no finding has severity 'error'`.
- Two modes: `action` (computes `next_step` with per-finding verbosity dispatch)
  and `check` (computes a `summary`).
- Deterministic ids (`uuid_id_generator` / `deterministic_id_generator`) and a
  `meta` block (`engine_version`, `generated_at`, `config_hash`).
- Config layer: `load_defaults`, `merge_config`, `config_hash`,
  `AssayforgeConfigSchema`, safe-range validation; `defaults.yml` data asset.
- **Verified byte-for-byte against the reference TS engine** via differential
  tests over the committed test-surface golden: 21 single-check cases + 28
  full-lifecycle flow steps, plus config merge/hash parity and smoke coverage.
- Ships `py.typed`; passes `ruff` and `mypy --strict`. Runtime deps: `pydantic`,
  `pyyaml`, `typing-extensions`.
