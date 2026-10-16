# KITT 0.16.12 — DeepSeek generation continuation

Pins the merged Reverse Proxy **5.4.8** with DeepSeek provider plugin
**1.2.0**. All other component SHAs remain unchanged.

When DeepSeek offers an inline `Continue` action on the current assistant
answer, the UI response monitor can resume **once**, without resubmitting the
original prompt. Detection is scoped to a freshly observed assistant response
card and rejects ambiguous matches, obsolete conversation turns, and page-wide
controls. The monitor waits for post-click answer progress and cannot return
the pre-click partial text as a completed KITT action. Additional interruptions
or missing progress require manual intervention.

Security boundaries remain unchanged: never automate login, consent,
authorization, model tool approvals, or policy-gated runtime commands.

Regressions cover matching exact labels, disabling controls, duplicate buttons,
stale output, origin restrictions and single-click semantics. A real authenticated
DeepSeek Web UI run is still required to verify current DOM selectors; GitHub CI
tests do not establish this.
