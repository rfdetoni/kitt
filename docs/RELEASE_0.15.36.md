# KITT 0.15.36 — reliable first-task submission

Pinned reverse-proxy **5.3.11** commit
`9dfae74f57b8239c5b9b419967ed5ee8fe037155`.
No changes to Protocol **0.13.3**, Agent CLI **0.87.11**, Assistant,
AI Workers, Memory or Toolbox.

## Incident

The 14 October 2026 18:46 logs prove that the initial KAP/2 planning
response reached the Agent CLI. The first T00 execution prompt was
present in the ChatGPT rich text composer but was never dispatched.
The editor changed 12,371 normalized characters into 12,374. The
reverse proxy raised `ui_automation_error` before dispatch twice;
a subsequent retry found the UI still generating.

## Fix and bounded behavior

The reverse-proxy 5.3.11 extends its proven large-rich-editor repair
strategy to prompts over 8 KiB. It performs one explicit text replacement
instead of a huge keyboard replay, reads back the text after controlled
React reconciliation, rechecks before clicking Send, and refuses to
send any still-mutated or truncated prompt. Regressions cover recovery
from three extra characters and fail-closed behavior.

The installer already consumes exact commits from
`ecosystem.release.json`, so it needs no source-code change.
Root integration tests and a live authenticated WebChat retest
remain separate from passing source CI.
