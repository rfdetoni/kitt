# KITT 0.15.27 — Dual observers for ChatGPT Web response completion

## Incident and fix

The October 14 incident logs show Reverse Proxy 5.3.1 submitting a
63k-character ChatGPT Web prompt; the CDP tap saw five POSTs but found
only one of three anchor matches and was discarded. DOM selectors found
zero assistant nodes even after the answer visibly included `K2/END`.
The CLI received `ui_timeout` after roughly 210 seconds.

The 5.3.3 Reverse Proxy (commit
`05aa12d3578448142742dbf746fb7c078a488152`) implements two
independent result observers. The first correlated and *fully parsed*
KAP/2 result wins after stability confirmation. DOM requires a fresh
assistant-owned turn; CDP requires an origin-allowed matching request
and exactly one answer candidate. The loser is cancelled. No upstream
generation is aborted, no tool is authorized by model text, and no blind
request replay occurs.

The CDP correlator now considers one strong long-prompt anchor when the
request is unique; multiple competing candidates fail closed. DOM probes
also examine recent reply markdown when role/test-id attributes change.

## Immutable component changes

- Root version: `0.15.27`
- Reverse Proxy: **5.3.3**, commit `05aa12d3578448142742dbf746fb7c078a488152`
- Protocol, memory, toolbox, assistant, Agent CLI and AI Workers:
  **unchanged pins from 0.15.26**.

This hotfix intentionally does **not** pull Protocol 0.13.2 and Agent
0.87.9 into the same root release, because the broader upgrade has a
known Assistant Cargo.lock conflict. The proxy accepts existing
pre-negotiation KAP/2 requests; the additional header is optional for
the older Agent.

## Acceptance

Reverse Proxy 5.3.3 CI and Docker checks passed at its PR head.
The root release needs `ecosystem-main`, `installer-portability`
and `ecosystem-integration` gates at this exact manifest SHA before
merging. A real authenticated web replay of the user's session remains
operator-side acceptance, not an automated CI claim.
