# KITT Ecosystem 0.14.2 — Reject ambiguous repair decisions

Reverse Proxy 5.0.1 closes a gap between strict parsing and HTTP recovery. Ambiguous responses and duplicate verdict fields were rejected locally, but a model-side repair could select one interpretation and turn the request into HTTP 200. The Proxy now stops with HTTP 409 / agent_contract_invalid before requesting such a repair. It also stops if ambiguity first appears during a syntax repair.

The response exposes no final result or tool call. The caller can begin a fresh decision turn with the existing continue recovery action. Unique local recovery, faithful syntax/schema repairs, attempt budgets and cancellation remain unchanged. WebChat owns token limits.

The manifest pins Proxy 5.0.1 with the existing compatible Agent 0.85.0, Protocol 0.10.0, Assistant 0.1.33 / runtime 0.3.0 and Workers 0.1.57 revisions. No contract or dependency change requires consumer version bumps.

HTTP regression tests cover conflicting review verdicts, competing write-file arguments and ambiguity introduced during repair. Existing quote/whitespace preservation and structured-result integration remain covered. No fresh authenticated Gemini session was executed.
