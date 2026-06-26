<p align="center">
  <img src="assets/assayforge-logo.svg" alt="assay" width="440">
</p>

<p align="center"><i>A self-contained, deterministic work-session completion gate.</i></p>

<p align="center">
  <a href="https://github.com/blacksmithers/assay/actions"><img src="https://github.com/blacksmithers/assay/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/assay-forge/"><img src="https://img.shields.io/pypi/v/assay-forge.svg" alt="PyPI"></a>
  <img src="https://img.shields.io/pypi/pyversions/assay-forge.svg" alt="Python versions">
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License: Apache 2.0">
  <img src="https://img.shields.io/badge/types-mypy%20strict-blue.svg" alt="mypy strict">
</p>

<p align="center">
  <code>pip install assay-forge</code> &nbsp;•&nbsp; <code>import assay</code>
</p>

---

`assay` takes a **work session** (a ticket plus the agent's recorded acceptance
checks, implementation-step completions, file changes, and test results), runs
four independent coverage checks, and reports a **completion gate** — with **no
LLM, fully deterministic**. Same input, same result, every time.

It is a faithful Python port of the SpecForge `@specforge/assayforge` engine,
extracted as a standalone library, and is the **work-session gate** of
[SpecSmither](https://github.com/blacksmithers/specsmither) (sitting beside the
planning gate, [crucible](https://github.com/blacksmithers/crucible)). The output
is **byte-equivalent to the reference TypeScript engine**, verified by differential
tests across single-check and full-lifecycle flow snapshots.

## Why

- 🎯 **Deterministic** — pure logic, no model calls. Reproducible in CI.
- 📦 **Self-contained** — pure Python; only `pydantic` and `pyyaml` at runtime.
- 🔬 **Faithful** — output matches the reference TS engine (differential-tested).
- 🎚️ **Configurable** — every check and severity knob lives in config.
- 🏷️ **Typed** — ships `py.typed`; passes `mypy --strict`.

## Install

```bash
pip install assay-forge      # → import assay
# or
uv add assay-forge
```

Requires Python ≥ 3.11.

## Quick start

```python
from assay import assay, AssayContext, AssayOptions, deterministic_id_generator

context = AssayContext.model_validate(work_session_dict)

result = assay(context, AssayOptions(mode="action", action="check-imp-step"))

print(result.passed)        # overall gate: no finding has severity 'error'
print(result.next_step)     # in action mode: what to do next (+ guidance)

# Canonical camelCase JSON (matches the reference engine):
result.to_json_dict()
```

## What it computes

`assay(context, options) → AssayResult`: four independent checks over the
normalized work-session event tables, then a single gate
`passed = no finding has severity 'error'`.

| Check | Reads |
|---|---|
| `acceptance-coverage` | `acceptanceChecks[]` vs the ticket's acceptance criteria |
| `implementation-coverage` | `implStepCompletions[]` vs the ticket's implementation steps |
| `file-action-coverage` | `fileChanges[]` vs the ticket's planned files (+ justification states) |
| `test-result-presence` | `testResults[]` vs the ticket's test specification (+ skip/failure justification) |

Two modes:

- **`action`** — computes `next_step` (the next thing the agent should do) with
  per-finding verbosity dispatch. Requires `options.action`.
- **`check`** — computes a `summary` (`pending_by_action`, `total_pending`,
  `blocking_issues`).

Determinism is anchored by an injectable id generator (`uuid_id_generator`
default, `deterministic_id_generator` for tests) and a `meta` block
(`engine_version`, `generated_at`, `config_hash`).

## Configuration

```python
from assay import load_defaults, merge_config, config_hash

config = merge_config(load_defaults(), {"checks": {"test-result-presence": {"enabled": False}}})
context = AssayContext.model_validate({**work_session_dict, "config": config})
```

Severity of every check (and the per-justification severity knobs) is config-driven.
`load_defaults()` returns the packaged `AssayforgeConfig` (data asset at
`assay/config/data/defaults.yml`).

## Public API

```python
from assay import (
    assay, ENGINE_VERSION,                                  # entry point
    AssayContext, AssayOptions, AssayResult,                # core models
    uuid_id_generator, deterministic_id_generator,          # id generators
    load_defaults, load_config, merge_config, config_hash,  # config helpers
    AssayforgeConfigSchema, validate_config, HARDCODED_DEFAULTS,
    CHECK_REGISTRY, get_file_action_severity,               # checks
    resolve_next_step, applicable_actions, action_applies,  # next-step
    compose_finding_guidance, compose_next_step_guidance,   # guidance
    compose_check_summary, interpolate,
    OPERATIONS, OPERATION_NAMES, is_operation_name,         # operations vocab
    types,                                                  # full type namespace
)
```

## Development

```bash
uv sync --all-extras --dev
uv run ruff check src tests
uv run mypy
uv run pytest                 # incl. differential vs the TS engine
```

Fidelity is verified against committed golden output captured from the reference
engine (`fixtures/golden/`), so CI needs no Node tooling.

## Releasing

`assay-forge` publishes to [PyPI](https://pypi.org/project/assay-forge/)
automatically via GitHub Actions
([`publish.yml`](.github/workflows/publish.yml)) using **Trusted Publishing**
(OIDC — no API tokens stored in the repo).

**One-time PyPI setup** (by a maintainer): add a *pending publisher* for the
`assay-forge` project — owner `blacksmithers`, repository `assay`, workflow
`publish.yml`, environment `pypi`.

**Cut a release:**

1. Bump the version in `pyproject.toml` and `src/assay/__init__.py`, and add a
   `CHANGELOG.md` entry.
2. Tag and push — the tag triggers the workflow (build → `twine check` →
   publish):
   ```bash
   git tag v0.1.0
   git push origin main --tags
   ```

The workflow can also be run manually from the **Actions** tab
(`workflow_dispatch`). Build locally any time with `uv build` (artifacts in
`dist/`).

## Status

`0.1.0` — a **complete** port, **verified byte-for-byte against the reference TS
assayforge engine** across the single-check and full-lifecycle flow surfaces,
both `action` and `check` modes.

## License

Apache 2.0 © Gabriel Augusto Gonçalves / blacksmithers
