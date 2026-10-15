# KITT ecosystem 0.15.49 — multi-model specialist agents

## Versions
- Agent CLI 0.87.25: 4138895c84b673c8dfef54ddb8f7276ee4ca1eb4
- Assistant Runtime 0.3.32: 6ef66e21db7b37375a53e5c6998088edb61586bc
- AI Workers 0.1.71: d8e7d3fa768368c5c4d91a9592558238541d7e08
- Unchanged: Protocol, Memory, Toolbox, Reverse Proxy.

## Configure
Register model/provider profiles using the existing Model Manager or .kitt-router.json. Different profiles may reference different direct providers or KITT reverse-proxy instances (e.g. 127.0.0.1:3000 and :3001).

```bash
kitt agents list
kitt agents model code --mode auto
kitt agents model critic --mode preferred --primary review-proxy --fallbacks review-direct,execute --reasoning high
kitt agents model investigator --mode auto --local-only
kitt agents model creative --mode fixed --primary creative-proxy
```

In TUI: `/agent model critic preferred review-proxy review-direct,execute`; `/agent inspect critic` shows the policy. The existing profile registry manages credentials and network trust. No new provider HTTP transport or credentials are stored in the agent plugin.

## Design
- Agent LLM policies may be declared in trusted plugin TOML [agents.<id>.llm], overridden in bounded workspace-local .kitt-agent-models.json.
- Selection is made by host at admission and snapshotted in the child SQLite lineage; worktree or process restart does not silently switch models.
- Each child applies its own selected model to semantic/context and execution. Reverse-proxy sessions remain child-scoped.
- ProviderCircuitPool fallback respects the configured list, existing endpoint trust and offline/local_only or remote_egress=deny constraints. Streams are never replayed after visible output.
- No protocol or schema migration.

## Validation
Agent CLI branch CI: release critical tests, Docker/Podman runtime smoke and Windows package smoke all succeeded before publication. Downstream CI verifies Python/Rust packages and clean main installation.
