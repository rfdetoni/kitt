# K.I.T.T. Ecosystem 0.16.36

- Agent CLI **0.88.35**: `89d30ef447943cf27cc8d653f9329c72ce0c9a00`
- Assistant Runtime **0.4.26**: `99e0611c29901859f1205e4757191dc84ee03d2a`
- Reverse Proxy **5.4.16**: `d992cbedb6b6a10644a8ed58d14c6210cbd1ae66`
- Protocol, Memory, Toolbox and AI Workers preserve their previously verified immutable SHAs.

The host attempts all available Bubblewrap installations in `/usr/local/bin`, `/usr/bin`, `/bin` and `PATH`. It enforces version >=0.12.0 and validates real namespaces before selecting the executable. An AppArmor `uid_map` restriction is reported with the affected binary, not silently bypassed. Refreshes probes after 60 seconds. Use a targeted, administrator-approved AppArmor profile if local namespaces remain denied. Keep OS security features enabled.

Required: Agent PR Checks and Docker/Podman smokes, Assistant CI, root ecosystem-main and ecosystem-integration. This source release cannot change the target workstation AppArmor configuration.
