# KITT Ecosystem 0.15.3

## Fixed behavior

- Agent 0.86.2 requests structured KAP completion and validation reports, including typed issue objects. It no longer instructs these consumers to put JSON into the model-facing envelope.
- Independent read-only validation receives planned/current files as explicit inputs even when no mutation snapshot is recorded.
- Untrusted fallback profiles are excluded; an unavailable selected provider retains its own connection diagnostic rather than being masked by an unauthorized alternate port.
- Malformed process vectors such as an empty list nested in argv are rejected as input errors before policy evaluation. Allow All does not bypass shell, sandbox or file scope checks.
- Proxy 5.1.1 detects competing actions/fields before upstream repair, including a malformed prefix followed by another ACTION.

## Compatible composition

Agent 4831ee3bd98fef4e9530a38380c2f698c4736370, Proxy b932de2fb3921c1ca9def3fd1dbb3ce66578cfe3 and Assistant 95e0834e858e1399e418df686a469812cd476c50 are immutable pins. Assistant Python runtime 0.3.3 requires Agent 0.86.2 and synchronizes uv.lock and CI's Agent reference. Native/HUD Assistant 0.1.34, Protocol 0.11.0 and remaining components are unchanged; contract v4 and KAP/1 grammar are unchanged.

## Evidence and limits

Existing regressions reproduce the missing validator inputs, unauthorized fallback masking, malformed argv diagnostic and unnecessary repair of competing actions on the previous source. The corrected local suites pass: Agent 277 tests (one skipped) and Proxy 218 tests; Python/TypeScript report interoperability covers typed OK and FAIL reports. The Assistant daemon suite requires Unix sockets, which the local execution environment denies; CI validates the real daemon and release installers.

The attached Gemini session confirms 33 button submissions accepted by the WebChat. These changes do not make provider refusals or unproven task requirements successful. Update the full release composition and restart Agent and Proxy to load the fixes:

```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- --preset full --channel release --yes
```
