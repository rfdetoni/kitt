# KITT 0.15.53 — current-turn WebChat capture

The release composition pins Reverse Proxy 5.3.16 at
`77bbce9137860016a23c5bdbdde03c96d8582320`. The proxy distinguishes a newly
rendered response from prompt examples before applying content exclusions,
and retains rendered line boundaries in mutation snapshots. This addresses
reproduced capture timeouts after a successful plan, including roleless DOM.

Agent CLI remains 0.87.29; no Agent/Protocol wire change or automatic replay is
needed. Its existing no-action-received handling for an uncaptured provider
response remains in force.

All seven release pins are refreshed to the component mains observed during
this release, including the existing Agent CLI, Assistant and AI Workers
updates. The installer still installs immutable SHAs in release mode.
`VERSION` and `ecosystem.release.json` advance together to 0.15.53.

Validation: 282 proxy tests, 10 Chromium integration tests, 31 authoritative
KAP/2 cases, generated schema/parser parity, typecheck/build/fast build,
package dry-run, zero reported dependency audit vulnerabilities, and 80 root
installer tests. Both new browser regressions fail on the previous proxy main.
The live authenticated ChatGPT session and a full native ecosystem installation
were not available in this environment.
