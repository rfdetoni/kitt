# KITT ecosystem 0.15.39 — lazy reverse-engineering environments

This release pins KITT Agent CLI **0.87.15**, which builds on the
validated **0.87.14** RE manager/TUI and adds a host-owned mission lease
and automatic cleanup of guests started by each operator-requested lab run.

## User-facing behavior

- `kitt` launches normally without booting pods, Linux/Windows VMs, or RE
  containers. Discovery is side-effect-free.
- `/re` opens the Agent CLI manager. Choose Windows or Linux to create or
  enroll a private guest profile, start/stop it, configure lazy startup, or
  build its pinned QEMU image. The setup helper asks for the operator's
  own ISO/QCOW2; KITT never downloads a guest operating system.
- The RE `full` toolbox can be built explicitly and opened from `/re`
  in a temporary terminal session. The toolbox is ephemeral and has no
  network access, but is **not a VM-grade hostile-binary isolation boundary**.
- `kitt re status` reports installed REA, container runtimes, and
  enrolled guests; `kitt re auto windows on` enables operator-owned
  lab-triggered startup after enrollment.
- `kitt vm lab run` leases lazy guests exclusively and stops only
  instances this invocation started, on success or error. VMs that were
  already running stay running. A concurrent second lazy mission is
  blocked instead of racing guest shutdown.
- REA MCP registration still requires `kitt plugins enable kitt-rea`
  and compatible host installation. The TUI shows setup guidance
  rather than silently acquiring packages or escalating privileges.

## Release composition

No Protocol, Memory, Toolbox native, Assistant, AI Workers, or Reverse Proxy
interface change is required. `ecosystem.release.json` pins each
component to an immutable SHA; the Agent CLI package version and
`uv.lock` are synchronized at **0.87.15**.

## Verification and remaining constraints

The Agent CLI PR runs Python release-critical and RE/VM contract checks,
smoke tests on Windows, Podman and Docker, and a Docker build. These
checks exercise interface and lifecycle logic but do not prove a complete
Windows/KVM hardware boot or an authenticated forced-command SSH probe.
Host shutdown/power failure can still leave resources requiring manual
recovery; timed idle eviction, privileged OS provisioning, host-wide
crash-proof reference counting and full VM lab E2E are not included.

See `kitt-agent-cli/docs/RE_LAZY_ENVIRONMENTS.md` for setup and
security guidance.
