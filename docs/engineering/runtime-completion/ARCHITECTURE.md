# KITT Ecosystem Runtime Architecture

## 1. Authority & Trust Boundaries

The K.I.T.T. ecosystem enforces strict separation between orchestration, privilege enforcement, UI presentation, and isolated execution:

```
  [Rune Native / WebGPU UI] ──(loopback HTTP + Origin + X-Kitt-Csrf)──▶ [kittd settings_web Control Plane]
             │                                                                       │
       (no secrets)                                                       (host-side bearer tokens)
                                                                                     ▼
  [kitt-agent-cli] ──(RPC / RemoteRuntimeDriver)──▶ [runtime_worker.py HTTP+TLS] ◀──┘
                                                           │
            ┌──────────────────────────────────────────────┼───────────────────────────────────┐
            ▼                                              ▼                                   ▼
   [gpu_manager.py]                               [cas_store.py]                        [mount_sources.py]
   Host flock ledger                              Workspace-isolated CAS                 Host-only GitHub/S3 SigV4
   (RESERVING->ACTIVE->                           + FastCDC / Zstd L3                    (read-only verified digests)
    RELEASING/INDETERMINATE)                      + Refcount GC
```

## 2. Key Subsystems

1. **Contract Layer (`kitt-protocol` `v0.14.4`)**:
   - Canonical Rust (`src/runtime.rs`), Python (`sdk/python/kitt_protocol/runtime.py`), TypeScript (`sdk/typescript/src/runtime.ts`), and JSON Schema (`schemas/runtime-capabilities.schema.json`) types verified by `check_contract_parity.py`.
2. **Host GPU Exclusivity & Multi-Vendor (`gpu_manager.py`, `runtime_worker.py`)**:
   - File-locked (`fcntl.flock`) atomic reservation state machine across workers on the same host, paired with Docker/Podman metadata lease containers and `inspect`-before-unknown rollback.
   - Supports NVIDIA (Docker `--gpus`, Podman CDI `--device nvidia.com/gpu=...`, MIG UUIDs), AMD ROCm (`/dev/kfd`, `/dev/dri/renderD*`, `ROCR_VISIBLE_DEVICES`/`HIP_VISIBLE_DEVICES`), and Intel XPU (`ZE_AFFINITY_MASK`).
3. **Storage, Compression & Migration (`cas_store.py`, `workspace_snapshot.py`, `migration.py`, `remote_cache.py`)**:
   - Workspace-isolated SHA-256 CAS with fixed 256 KiB and Gear-hash FastCDC chunking (`export_workspace_v2`).
   - Adaptive Python 3.14 stdlib Zstd (`compression.zstd`) bypassing payloads `< 4096` bytes or incompressible magic headers (`\x89PNG`, `\x1f\x8b`, `PK\x03\x04`, `\xff\xd8\xff`, Zstd, `GGUF`) and bounding decompression windows (`window_log_max=20`).
   - 10-step transactional migration (`cold`, `warm`, CRIU-gated `live`) with pre-cutover rollback.
4. **Gateway & Debian VM Policy (`kitt-reverse-proxy` `v5.4.33`, `kitt-agent-cli` `v0.89.14`)**:
   - Dedicated `--vm-api-key` denies `/v1` & `/v1/kitt/*` (`403 vm_scope_forbidden`) and restricts models via `--vm-allowed-models`.
   - `kitt vm prepare` enforces cryptographically verified Debian images (SHA-512 + GPG keyring), sealed read-only base images (`chmod 0o400`), KVM/TCG detection, and guest cache cleanup.
