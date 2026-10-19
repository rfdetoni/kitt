# KITT 0.16.21 — capability-first agent execution

## Release pins

- Agent CLI **0.88.17**, commit
  `c5abeff07a9a7fa2d778940733bb80486f5880a7`
  ([PR #120](https://github.com/rfdetoni/kitt-agent-cli/pull/120)).
- Protocol, Memory, Toolbox, Assistant, AI Workers, Reverse Proxy: **same
  immutable pins as 0.16.20**. No dependency upgrade is needed.
- VERSION, ecosystem.release.json, README and changelog agree on 0.16.21.

## Evidence and changes

Operator-provided Agent CLI/ChatGPT Web UI logs from 2026-10-19 showed
repeated discovery of Docker, git and CLI capabilities, a 16-operation
budget exhaustion and irrelevant repository lookups for internal plan
keywords. Most measured latency belonged to upstream model turn time,
not host process execution.

Agent CLI 0.88.17 includes:
1. Model-visible deterministic capability snapshot (including RE guest network
   isolation and bind-mounted workspace), advisory only and never an approval.
2. A single JSON use_tool format for reverse-proxy agent-loop requests instead
   of competing legacy XML examples; host tool schemas remain authoritative.
3. Repository context query filtering of planner scaffolding and internal
   criteria names.
4. A bounded discovery telemetry/checkpoint after repeated environment
   probes, without misclassifying Git mutations or Docker guest execution.
5. Conservative local task decomposition for simple single-file edits, while
   cross-file and multi-step tasks use the standard remote planner.
6. Operator-only `kitt re lab stage-wine --approve`: clone the official
   Wine-Staging patch repository on the network-enabled host into
   `~/.local/share/kitt/re-lab/workspace/sources/wine-staging`, visible
   within the managed networkless Linux guest as
   `/workspace/sources/wine-staging`. This requires an interactive operator
   terminal and refuses replacing an existing checkout.

Agent tests cover the new preflight, planning, discovery and staging cases.
No host network or credential access is granted to the agent's Linux guest,
no Windows VM disk is recreated, and existing policy/approval gates remain
in force.

## Validation limits

All Agent CI checks passed: package build, lock, contracts and full regression,
Windows packaging, Docker and Podman smokes. Root integration CI must also
pass before promoting this central pin. This release does **not** assert
end-to-end operator KITT RE staging, an automated Wine source inventory,
a general-purpose guest execution backend, or measured production speedup;
those need host-side acceptance with the user's actual workspace and
additional authorization. ChatGPT Web UI latency is an external factor.

Validate after updating the `release` channel:
```sh
kitt --version
kitt re lab status --json
kitt re lab verify --full
```
To stage the public Wine-Staging source once, on the host:
```sh
kitt re lab stage-wine --approve
```
