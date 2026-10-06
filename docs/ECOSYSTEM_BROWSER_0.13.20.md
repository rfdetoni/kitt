# Ecosystem 0.13.20

## Included corrections

Reverse Proxy 4.9.15 captures omitted CDP POST bodies passively and learns original replies inside positional RPC arrays and nested JSON strings. Matching starts at actual click/Enter, preserving time spent composing a prompt. Source extraction remains bounded and learned against an intact DOM response; raw contract recovery still requires a previously trusted, fully correlated and successfully completed stream. No browser request is replayed, private endpoint fixed or missing contract content invented.

ChatGPT uses the same human stable-Chrome authentication bootstrap as Gemini, including managed services. Automation attaches after return to the exact provider origin, outside login routes and without an open Google/OpenAI auth popup. Stable Chrome must be installed or configured with KITT_CHROME_BIN. Provider-side acceptance of a real Google login cannot be proven by these fixtures.

Agent CLI 0.83.18 fixes the reproduced `Refusing provider egress` on port 3001 by trusting an explicitly selected managed instance's exact origin before router persistence, like the existing explicit model command. Other ports/providers stay denied; listing/starting services and workspace configuration do not grant trust. The separate connection-refused failure at port 3000 requires a running service.

## Consumer consistency

Assistant 0.1.21/runtime 0.2.34 and AI Workers 0.1.44 lock Agent 0.83.18 at the same SHA as this composition. Assistant runtime/lifecycle CI now validates that exact revision. Package/editable-lock and native workspace/Cargo metadata agree. Protocol 0.9.1, Memory 0.9.2 and Toolbox retain their previous immutable revisions and wire contracts; HUD dependency locks are unchanged. VERSION and ecosystem.release.json agree at 0.13.20.

Existing Proxy, Agent and root verification workflows also run on fix/** branches so the same gates can validate changes before main promotion when PR creation is unavailable; release workflows remain main-only.

## Evidence

The positional RPC and omitted-body regressions failed before correction; the required real Chromium gate passed four UI/CDP cases, including a slow composer, omitted POST bodies, fragmented UTF-8 and raw recovery on a second turn with damaged DOM, with one browser POST per turn. Proxy TypeScript/build and 200 tests pass. Agent full tests pass with its split runtime companion: 230 tests, 12 subtests and one skip; its 217 release-critical tests and 12 subtests, Windows/Docker/Podman gates pass. Root local installer/architecture tests pass 58 checks. Component and composition CI must all pass before final publication.

The supplied logs do not include live Gemini network bodies; the generic RPC fixture proves support for this wire class, not every current authenticated provider layout. Human authentication is neither automated nor bypassed.
