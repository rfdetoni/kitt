# KITT 0.16.13 — DeepSeek server-stopped Continue footer

The operator provided a screenshot of an authenticated DeepSeek reply showing
**"Servidor está temporariamente indisponível"**, **"Parado"** and a
**"Continuar"** control at the response footer. A manual click restarted
generation of the same message.

- Pins Reverse Proxy 5.4.9 / DeepSeek plugin 1.2.1 at an immutable main SHA.
- Scans only the current fresh assistant message card for exact continuation
  controls, including footer siblings nested beyond the answer body.
- Supports native buttons and `role=button`; never searches outside the
  assistant card, clicks consent/login/authorization prompts or replays the
  original user prompt.
- After one continuation, partial pre-click output cannot become a completed
  Agent tool call. Second pauses or stalled progress require operator action.
- A stopped + server-unavailable card without a safely identifiable control
  is a manual-intervention condition, not a successful model completion.
- Adds screenshot-like DOM regressions. npm lock/version updated in the Proxy;
  no unrelated ecosystem pins change.

The image does not provide HTML markup or live browser instrumentation;
the exact DeepSeek DOM remains to be validated in the operator environment.
