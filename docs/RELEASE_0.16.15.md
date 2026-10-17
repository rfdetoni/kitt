# KITT 0.16.15 — offline, signed Clean-Room RE pipeline

Pins Agent CLI 0.88.10, Protocol 0.14.1, Assistant 0.1.55/Runtime 0.4.10 and Workers 0.1.80.

Added `kitt re cleanroom build-image` for a locally supplied SHA-pinned base image, GGUF model and llama-cli binary, and `kitt re cleanroom run` for signed-spec admission, isolated offline patch generation, host-enforced DLL-only source checks, independently signed networkless OCI test execution and tamper-evident digest-chain receipts. Reserved spec-extractor/wine-implementer personas can no longer use shared-context retained children.

Security preconditions remain external: independent reviewer key, legitimate Windows license, physically/OS-isolated analyst, independently reviewed base/model/toolchain, prepared Wine/ReactOS sources, and actual Windows Oracle conformance tests. The current Oracle pilot validates only one fixed benign event scenario; even green signed tests return NEEDS_INDEPENDENT_ORACLE_CONFORMANCE. Image creation or passing mocked tests is not 100% Clean-Room certification. No direct Reverse Proxy policy changes were required; the Agent host owns authorization.
