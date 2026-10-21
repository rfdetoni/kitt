# K.I.T.T. Ecosystem 0.16.38

## Immutable pins

- Agent CLI 0.88.37: `2a8aaad67446553c1b0c226040aab8208e3123d3`
- Assistant Runtime 0.4.28: `9110d6e47b1a5fe98e4ecac6404db1666ef85644`
- Reverse Proxy 5.4.17: `e3fd97e11f6eb40273cdae4855f2248b26ab9308`
- Protocol, Memory, Toolbox, AI Workers retain previous pins.

## Implemented improvements

Use existing read-only `flow.execute` and `program.execute` to combine independent lookups; use `repo.batch_read`, native code navigation, context handles and memory retrieval instead of repeated file probes. Goal history remains durable across read-only graph calls; empty memory recall is tracked separately. The Contract planner discourages artificial cross-item dependencies. C/C++ edits are not accepted as compiled unless a configured Makefile-backed build passes; missing native build blocks verification. Completed but unattributed WebChat responses require explicit continuation and may never be replayed automatically.

## Verification and limits

CI gates: Agent PR Checks and Docker/Podman/Windows smokes; Proxy TypeScript CI and Docker; Assistant CI; root ecosystem-main/integration. Source CI does not prove authentic ChatGPT browser capture, local Wine/C build correctness, actual LLM selection of tooling or improved tokens per task. Confirm on the target workstation and compare like-for-like benchmarks.
