# KITT 0.15.19 — Daemon bootstrap and REA MCP framing

## Incident (2026-10-13 17:48–17:49 UTC)

In the Windows API Observatory workspace, the Agent CLI daemon attempted
three startups without ever becoming ready. Its log included 280 authenticated
`auth` and 280 `ping` requests and three occurrences of
`MCP read loop ended with error: Separator is not found, and chunk exceed
the limit`. The Reverse Proxy 5.1.6 started, received no LLM request and
was later shut down with SIGTERM.

## Root causes and fixes

1. MCP stdio transport used asyncio's default ~64 KiB stream-reader limit
   while its published JSON-RPC frame allowance was 2 MiB. Agent CLI 0.86.16
   now aligns those limits and rejects oversized frames explicitly.
2. The detached daemon launcher polled authenticated readiness every 100 ms
   and gave up after 10 seconds even though optional REA MCP initialization
   may take longer. Assistant Runtime 0.3.13 now waits up to 45 seconds and
   uses 750 ms polling.
3. Another startup call could stop and replace an authenticated daemon
   which was still in `starting`. The launcher now waits for it rather than
   replacing it.

## Pinned main revisions

- Agent CLI 0.86.16: `482e0b8e24fab85936a711e540f64caef301afe0`.
- Assistant Runtime 0.3.13: `1f00e1bcc95ee64041732482a2fa7ebe9d19d437`.
- Reverse Proxy 5.1.6: `8f57a52bcaabc020ab3ae2866de25a17ab0ae407` (unchanged).
- Other four component revisions unchanged.

## Update the host without touching Docker/Podman

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- \
  --preset full --channel release --yes
```

No VM/RE lab provisioning flags are requested. This may restart host KITT
services but does not intentionally alter Docker/Podman containers, images,
volumes or the Windows VM.

## Validation

Regression coverage now includes real 128 KiB MCP subprocess output,
explicit oversized frame rejection and preservation of an already-starting
daemon. The installer and ecosystem manifests must pass CI; the user-hosted
REA binary still requires a real startup smoke test.
