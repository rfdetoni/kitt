# KITT ecosystem 0.15.52 — prevent ambiguous WebChat replay

## Pins
- Agent CLI 0.87.28: f5eaff224b80c02ceaaf390bc3b84e0943d95abf
- Assistant Runtime 0.3.35: 18131cbd1a4dfdae48c55daf407eef5c595e3a8a
- AI Workers 0.1.74: 6c1af00a9935ebe93aa409db1017f6c38e0455a8
- Protocol, Memory, Toolbox, Reverse Proxy unchanged.

## Evidence
2026-10-15 13:44–13:51: successful 242.6s plan followed by three failed, submitted T00 browser prompts in the same session. Reverse-proxy 5.3.15 confirmed composer cleared; zero fresh assistant nodes/KAP frames, repeated ui_timeout. The Agent CLI scheduler retried without another operator send_input. No KAP action executed.

## Fix
GoalStepExecutor classifies the specific ambiguous KITT reverse proxy ui_timeout and marks the contract item BLOCKED / ENVIRONMENT, preserving durable state and requiring explicit operator resume after inspecting/authenticating the WebChat session. It does not reuse old K2 markers or automatically replay a potentially finished browser turn. Regression verifies no scheduler retry and explicit resumption of T00. Existing review/progress UX unaffected.

## Limits
This fix prevents unsafe repetitive requests, but does not fix the underlying ChatGPT Web DOM capture problem. Root cause requires inspection of the live authenticated page. The logs also show RSS above the configured proxy budget and a large initial prompt; neither alone proves a capture defect. CI and end-to-end install gates decide release eligibility.
