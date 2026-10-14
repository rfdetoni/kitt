# KITT 0.15.38 — canonical KAP/2 tool invocation for Goals

## Exact revision pins

- Agent CLI **0.87.13**, `d50e3fe6aa4258fa24e2c69645968f6c845c18a0`
- Assistant Python Runtime **0.3.25**, `11c9fee34db10c87dce8b73a8c2c7cc442456f23` (native unchanged)
- AI Workers **0.1.64**, Evals/Evolution **0.1.61**, `5a53de290ae861e3bee4a24dea07b603bbafecfa`
- Reverse Proxy **5.3.11** at `44b487262924c4fd4cf240a6421ee53a1b24712f` (dependency lock and CI workflow updates; runtime capture logic unchanged), Protocol **0.13.3**, Memory and Toolbox: unchanged versions

## Root cause and resolution

The 14 October 2026 19:05 logs showed that T00 messages were sent
successfully, but the model reported INCOMPLETE without a host tool
call. Agent CLI 0.87.12 corrected the tool-first Goals prompt and
bounded reports without tool evidence. A follow-up audit discovered
that the CLI's `parse_tool_call` bridge still recognized legacy
`<kitt-tool>` envelopes but did not decode the new model-issued KAP/2
`K2 T kitt_runtime` tool requests.

Agent CLI 0.87.13 routes K2 T parsing through the canonical Protocol
0.13.3 `decode_kap2_frame`, then through the existing tool policy
and dispatch. Structured K2 F remains final-only. Malformed tool
actions fail closed. Automated regressions exercise nested arguments,
malformed frames and normal completion. No unreviewed tool authority
or permissions were added.

## Installation and verification

This release updates `ecosystem.release.json`; the root installer
already fetches exact revision pins and therefore needs no code
changes. The root policy and Linux/Windows/macOS install gates must
pass before a stable release is confirmed. Source CI is not proof of
a complete authenticated ChatGPT Web session; rerun the observatory
T00 and verify the actual K2 T tool receipt and host-owned evidence.
