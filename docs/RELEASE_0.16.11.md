# KITT 0.16.11 — DeepSeek and ChatGPT Web capture resilience

This release updates only the Reverse Proxy pin in `ecosystem.release.json`.
All remaining component pins stay unchanged.

- Reverse Proxy **5.4.7**: DeepSeek provider plugin **1.1.0** isolates the
  answer DOM from DeepThink/reasoning panels (5.4.6).
- WebChat contract recovery deterministically truncates only a surplus
  public-facing `reasoning_summary` after full shape validation; it does
  not change tool calls, content, approvals or execution evidence.
- When CDP fails to match the submitted ChatGPT prompt and the DOM cannot
  prove a fresh assistant answer, `ui_capture_unverified` reports an
  explicit `continue` recovery status through the existing Agent CLI.
  **Do not automatically replay** a submitted prompt or infer a stale reply.
- Adds synthetic DOM, contract and failure-mapping regressions and synchronizes
  the Reverse Proxy package and npm lock.
- Chromium memory pressure and live ChatGPT/DeepSeek DOM changes remain
  operator-side runtime observations, not CI-verified E2E.

Operator guidance: regular logs should use `--log-content metadata`.
With a browser above the configured RSS cap, first close unnecessary tabs,
review capacity and restart explicitly rather than disabling the resource guard.
