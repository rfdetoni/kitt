# KITT Ecosystem 0.15.2 — Parallel automatic Goal agents and live monitor

## Scope

This release pins Agent CLI **0.86.1** with durable, host-controlled parallel fan-out of disjoint, dependency-ready implementation work in autonomous/Allow All mode. The existing GoalScheduler owns leases and verifies every item after the children have settled; child output alone cannot mark a task as DONE. For manual task plans, `plan.dispatch_ready` starts independent children in one host operation. The default concurrent children limit is four. Child subprocess admission is no longer artificially throttled by a 2-second cooldown.

The Agent CLI's **Ctrl+X, A** opens the live agent dashboard, while **Ctrl+X, E** is the model-provider endpoint shortcut. Child lifecycle events flow through local EventBus or the daemon's established session-scoped IPC.

## Allow All and command execution

- A direct, well-formed `run_command` argument vector is allowed without ordinary approval in autonomous mode. A real direct argv execution is exercised in Agent CI.
- Commands using shell wrappers, blocked executable/path escapes, opaque interpreter eval, and subprocess access from path-scoped children stay prohibited or gated. Allow All does not disable the sandbox or capability model.
- Scoped parallel children get read/edit tools; the authoritative parent/host performs build and verification checks, avoiding the previously exposed `run_command` denial.

## Immutable release pins

The root manifest pins Agent CLI `4155006ecb92d84c47fb618a9641df0a45263f01`, Protocol 0.11.0, and the Assistant Python runtime companion 0.3.2 with its own synchronized `uv.lock`. The Assistant and Proxy native source versions are unchanged. CI must verify that the manifest agrees with the actual Git/Cargo/Python/npm locks, without weakening version enforcement.

## Validation and limitations

Agent critical-contract CI, Docker/Podman runtime smoke, Windows package smoke, Assistant companion CI and root installer integration are release gates. Functional WebChat concurrency and token savings on a particular user's provider must be observed separately. Actual parallelism requires at least two independent work items with disjoint concrete file scopes and authorization under the selected profile; items with conflicting writes or unresolved dependencies execute sequentially.

## Installer

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- --preset full --channel release --yes
```
