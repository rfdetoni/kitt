# KITT 0.15.31 — bounded Python execution in KAP/2

## Component revisions

- Agent CLI `0.87.10`: `6a76c27f4e71962a644d174e9187f4d386f794f7`
- Assistant native `0.1.41`, Python runtime `0.3.22`: `ebc7a183f976a3a4b9684bbd9f218e6ded6458da`
- AI Workers `0.1.61`, Evals/Evolution `0.1.58`: `67add9866a1019147d8c8fe2c2e3c4347ff6c397`
- Protocol `0.13.2`, Memory, Toolbox and Reverse Proxy `5.3.6`: SHAs unchanged from 0.15.30.

## Feature

KAP/2 keeps exactly one `K2 T` action per assistant turn. The Agent now
recognizes `operation: sandbox.python` in `kitt_runtime`, using an ordinary
`arguments.code<<PY` literal. The host delegates to its existing
`python_compute` AST interpreter and retains `compute.safe` capability,
approval/policy boundaries, limited execution time and resource quotas.
Result JSON is structured, with `stdout`, `result` and `steps`.

The interpreter explicitly disallows imports, code-defined functions/classes,
filesystem, networking, shell and arbitrary Python. No full-Python sandbox,
persistent session or batch operation is activated in this MVP.

## Release pins and installer

The root `ecosystem.release.json` pins exact validated component SHAs.
Agent `pyproject.toml`, `uv.lock`, and runtime version agree at 0.87.10.
Assistant Runtime and AI Workers refresh their own `uv.lock` revisions.
Root `VERSION` is now 0.15.31. Existing installer logic reads the manifest,
so no new installer flags or duplicated installation paths are required.

## Verification

Agent PR Checks and Docker passed at the exact Agent commit. Assistant and
AI Workers CI plus root installation/integration gates must pass for this
composed snapshot. Independent authenticated WebChat end-to-end
reproduction is not proven by unit tests.

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh |
  sh -s -- --preset full --channel release --yes
```
