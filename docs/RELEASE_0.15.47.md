# KITT ecosystem 0.15.47 — specialist agent plugins

## Component pins
- Agent CLI 0.87.23: 4e643b11f00902d7afc7ee2e6315b4724cfec4f4
- Assistant Runtime 0.3.31: 1ceebd148f56cf203474c1548c930a4c7e031da3
- AI Workers 0.1.70: 65bba9fccea8a32d7be4a22f1fd9b78e82a83cdc
- Protocol, Memory, Toolbox and Reverse Proxy versions unchanged and pinned to their current mains.

## Usage
```sh
kitt agents                   # list specialists
kitt agents create            # interactive persona/plugin wizard
kitt agents create java-reviewer --role critic
kitt plugins trust agent-java-reviewer
kitt
```
TUI `/agent` lists available specialists. `/agent run critic Review src/api.py`; `/agent team Investigate the latency regression` launches investigator + creative if both child slots are available. `/agent msg <child> <message>` uses host-scoped family messages; `/agent inbox` lists messages. `/agent auto <task>` chooses a specialist deterministically. Code-writing profiles need explicit `--paths` to narrow writable scope.

The model may discover profiles using `kitt_runtime agents.list` and request `child_spawn` with `agent_profile`; the host replaces caller-provided persona-role/tool permissions and narrows budgets before policy-gated execution. Messages queue and are delivered at child turn boundaries, not streamed into an active model call.

## Validation
The Agent PR #104 passed release-critical regression, Docker, Podman and Windows package smoke tests. Downstream Python locks/CI references were aligned to immutable commits. No new daemon, data store or KAP wire protocol.
