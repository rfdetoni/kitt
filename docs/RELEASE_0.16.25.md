# KITT Ecosystem 0.16.25 — autonomia preservada e aprovações persistentes

## Pins imutáveis
- Agent CLI **0.88.21**: `306f312b6d9323731ff373a29b557ce54e29058b` ([PR #126](https://github.com/rfdetoni/kitt-agent-cli/pull/126)).
- Assistant **0.1.59 / runtime 0.4.14**: `c2157a88564dd8eaf79a83746ace4bc510ba152c` ([PR #53](https://github.com/rfdetoni/kitt-assistant/pull/53)).
- Reverse Proxy **5.4.14**: unchanged, `9dc9e788d77827eb5df04775a1c1b58a231764b5`.

## Correção
At attach, the TUI reads the persisted autonomy level from the daemon instead of overwriting that policy with a stale TUI copy. Explicit operator selection of `/autonomy allow-all` still calls the daemon and persists the acknowledgement. The daemon now includes the original principal identity from pending-action security snapshots in persistent approval list results; remembered `run_command` rules remain restricted to the correct executor, workspace/session and capabilities after queue refresh.

## Observed limits
In the supplied October 20 logs, the daemon repeatedly evaluated actions under `autonomy=supervised` and the user waited at several approval prompts. Planning-mode subturns explicitly say `Plan only`; execution subturns were reached, but `process.run` encountered workspace and strong-sandbox restrictions. Neither `allow-all` nor remembered approval bypasses those restrictions or creates an authorized Windows oracle.

The component CI validates daemon readback, approval identity and package integration. The ecosystem checks validate release pinning and installation; this is not evidence of successful Windows/Wine behavior in the user's live host. Restart or update the daemon and TUI together to activate these changes.
