# KITT 0.15.16 — Reverse Proxy 5.1.4

Synchronized ecosystem release pins with the latest validated Reverse Proxy
`c8a27842fcb939ed96cd83ca490c791b17ddad31`. The integrated proxy
adds real editor editability validation and native large-textarea injection
with post-input content verification.

The other six component SHAs are unchanged. Existing cross-component
contracts and installer options remain unchanged.

## Host-only update (preserves Docker/Podman lab)

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- \
  --preset full --channel release --yes
```

Do not add `--with-re-lab`, `--with-vm-containers`, or `--vm-pull-images`.
No Docker or Podman images, containers or volumes are intentionally modified
by the host-only installer. It may stop/restart KITT-managed host services.

## Evidence and limitations

The Reverse Proxy regression tests exercise mocked native textarea
interaction for a 65 KiB prompt, alongside prompt-integrity refusal.
Authenticated live ChatGPT Web verification still depends on the user-hosted
browser session and is not asserted by these tests.
