# KITT 0.15.18 — Slow active WebChat response support

This release addresses a request that the authenticated ChatGPT Web was
still processing, but the KITT agent/proxy request failed at exactly 240 seconds.

## Component pins
- Agent CLI 0.86.15 — 78907e6568b77f88ec050ab6ba750980c76505c4
- Reverse Proxy 5.1.6 — 8f57a52bcaabc020ab3ae2866de25a17ab0ae407
- Assistant Runtime 0.3.12 — 1324431670314a9d1a1c4b09fc801d7fd8843d9f
- Protocol, Memory, Toolbox and AI Workers remain at previous main SHAs.

## Behavior
- A KITT agent-loop request through the Reverse Proxy carries a default
  900-second deadline, and the Agent HTTP transport waits up to 960 seconds.
- The UI reader can monitor active generation for up to 900 seconds, but
  does not count arbitrary page mutations as model progress.
- Progress diagnostics record timing, streaming state and length, not output text.
- An ambiguous submitted request is never automatically replayed.

## Host-only update without Docker/Podman changes

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- \
  --preset full --channel release --yes
```

No RE lab or VM container flags are passed, so no Docker/Podman images,
volumes or VMs are provisioned or recreated. Host KITT-managed services
can be stopped/restarted as part of installation.

## Validation

The Agent and Proxy CI include regressions covering transport deadlines,
idle DOM mutations, and active generation budgets. A live authenticated
ChatGPT Web run is needed to confirm the slow-response outcome on the
operator's actual browser.
