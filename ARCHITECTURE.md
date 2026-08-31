# Architecture

```text
                         kitt-protocol
                              │
              ┌───────────────┼────────────────┐
              │               │                │
      kitt-agent-cli    kitt-assistant   kitt-reverse-proxy
        Python/Rust       Rust + TS          TypeScript
              │               │
              └──────┬────────┘
                     │
                kitt-memory
                    Rust

         kitt-ai-workers        kitt-toolbox
             Python                Rust
          (on demand)            (shared)
```

## Architectural rules

1. Product repositories remain independently releasable.
2. Cross-product contracts are versioned in `kitt-protocol`.
3. Heavy workers are out-of-process and demand-driven.
4. The Assistant's always-on path is Rust only.
5. UI code never owns privileged system actions.
6. Memory is namespace/scope/sensitivity aware.
7. Local-first is the default; remote egress is explicit.
8. Prefer composition and explicit ports over framework coupling.
