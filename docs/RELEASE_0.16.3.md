# KITT 0.16.3 — rendered prompt exclusion and generation sequencing

Pins Reverse Proxy 5.4.2 (`689daf56c87c81117987cf8c73131ff00e01c51c`). Other component pins, their dependency locks and Agent contract v5 remain unchanged.

The supplied 5.4.1 logs show a JSON report example from the user prompt incorrectly captured during generation, followed by a repair blocked by the busy chat. Prompt/history exclusion now compares parsed JSON values despite rendering whitespace changes. DOM capture waits for idle generation, and the next request waits before both baseline collection and composer editing. This also prevents a previous answer completed during the wait from being reused as the new response. Cancellation and busy timeout preserve the draft without submitting or replaying the request.

Validation: actual logged prompt echo rejected; 268 Proxy unit tests, 14 Chromium integrations, 86 root installer/catalog tests and installed Agent/Protocol/Proxy interoperability. Authenticated live provider validation was not performed.
