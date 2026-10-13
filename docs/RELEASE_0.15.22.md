# KITT 0.15.22 — KAP/2 compact model contract

The full ecosystem release is composed from current module main heads and validated in CI. This change concerns **model-facing text only**: trusted host HTTP/JSON, IPC Envelope v1, approvals, capabilities and tool-validation rules are unchanged.

## Components

- kitt-protocol 0.12.0: canonical TypeScript/Python KAP/2 decoders, tabular and nested fields, literal source bodies, strict bounds and contract documentation
- kitt-reverse-proxy 5.2.0: compact prompts; schema-checked operation shorthand; deterministic response/repair validation; CDP and ChatGPT DOM recovery accept complete K2 envelopes
- kitt-agent-cli 0.87.0: structured K2 final decoding from shared SDK; version and protocol pins synchronized
- kitt-assistant native 0.1.35, runtime 0.3.15; kitt-ai-workers 0.1.58: updated compatible dependency versions and locks
- memory and toolbox: existing IPC contracts remain unchanged and their pins are carried forward

## Examples

```text
K2 T repo.read
path: README.md
K2/END
```

```text
K2 F
tasks[2]{id,status}:
  T01,done
  T02,pending
K2/END
```

```text
K2 T repo.write_file
path: src/index.ts
content<<CODE
export const ready = true;
CODE
K2/END
```

The host must validate every tool schema and authorization before execution. An operation name is shorthand only when exactly one declared tool supports it via its operation enum. Invalid or incomplete frames are not executed. No independent privilege is conferred by K2 syntax.

## Validation

CI validates Rust/Python/TypeScript contract parity, tool and response validation, strict parser errors, proxy recovery from UI and network tap, and installed end-to-end composition. The KAP/1 decoder remains supported for historic host data; new model prompts request KAP/2.

## Deferred extensions

Stateful artifact handles, revision-aware writes, read-only batch execution, positional-only arguments, differential plans and response-final early cancellation must have host capability and identity contracts plus explicit cross-module validation before they can be enabled for autonomous execution. They are not silently inferred from K2 text.
