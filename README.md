# K.I.T.T. Ecosystem

Meta-repository for architecture, compatibility and release coordination. Runtime code belongs to product/component repositories.

| Repository | Responsibility | Primary stack |
|---|---|---|
| kitt-agent-cli | coding agent | Python + Rust |
| kitt-assistant | always-on personal assistant + ephemeral HUD | Rust + Tauri/TypeScript |
| kitt-reverse-proxy | web chat -> API bridge | TypeScript |
| kitt-memory | shared memory engine | Rust |
| kitt-protocol | cross-product contracts | JSON Schema + Rust/Python/TypeScript SDKs |
| kitt-toolbox | shared low-level utilities | Rust |
| kitt-ai-workers | demand-driven ML workers | Python |

The ecosystem shares protocols and versioned components, not source trees or Git submodules.
