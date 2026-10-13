# KITT 0.15.11 — Linux native build prerequisite preflight

## Correction

The release installer checks for the `cc` C compiler/linker before repository synchronization and native Cargo builds on Linux when a Rust component is selected. Previously a fresh host could successfully bootstrap Rust and download the full ecosystem, then fail at `cargo build` with `error: linker \`cc\` not found`.

For Debian/Ubuntu install `sudo apt install build-essential pkg-config`; for Fedora use `sudo dnf install gcc gcc-c++ make`. The installer does not invoke `sudo` or modify host packages. `--portable` intentionally does not require the native linker; ALSA remains optional (the Assistant already falls back to `--no-default-features` without its development libraries).

## Scope

KITT installer **0.15.11** only. Component SHAs and REA/VM image tags remain exactly those from 0.15.10. Existing users can install the prerequisite and rerun the same official `curl ... | sh -s -- ...` command without clearing state.

## Validation

A targeted unittest asserts that missing `cc` is a prerequisite failure for Linux native builds but not for portable installs, and checks the actionable distribution hint. CI `ecosystem-main`, `installer-portability` and `ecosystem-integration` must pass before merge.
