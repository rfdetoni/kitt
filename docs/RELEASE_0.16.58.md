# KITT 0.16.58 — Confirm ambiguous UI submission before failing

- Pin Reverse Proxy 5.4.27 at 6d3a1910c0df1163d926bb6f90fb6cc16c651fa3.
- Confirm composer-cleared/streaming/response-change evidence when a
  Playwright send-button click times out; do not automatically re-send
  a message whose submission status is uncertain.
- Fix derived from Agent CLI and Reverse Proxy logs on 2026-10-26.
- Preserve Agent CLI 0.88.91 pin and every other component pin.

CI coverage: proxy UI regression/build/Chromium tests, immutable SHA checks,
main/release installer and Assistant lock. This does not validate production
browser load or guarantee no future UI-layout changes at chatgpt.com.
