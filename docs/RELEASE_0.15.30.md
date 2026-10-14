# KITT 0.15.30 — reverse-proxy KAP/2 capture on virtualized DOM

## Composition
The root distribution now pins Reverse Proxy **5.3.6** at `0d46efc9cc3b666230c67b8c3821f5c7b7d4600f`. All other six component SHAs remain unchanged from 0.15.29; there are no new shared protocol dependencies.

The proxy can identify a fresh malformed but delimited KAP/2 reply after a sufficiently long exact-tail anchor from the submitted prompt when the browser has replaced its old conversation DOM. It forwards only this validated-fresh unparsed text to the existing agent-owned contract repair path. Successful tool completion still requires strict KAP parsing by the host; the default WebChat reader remains DOM-only.

## Lock and installer
The root `ecosystem.release.json` pins the proxy revision and `VERSION` is advanced to **0.15.30**. The source-free installer now checks `package.json` and both npm lockfile version fields before building the reverse-proxy, failing closed on drift. The reverse-proxy 5.3.6 commit synchronizes `package.json` and `package-lock.json`, and standalone installers select the latest stable tag or `main` as already documented.

## Verification and limitations
Proxy fix-branch CI and Docker validation are prerequisites for promoting the pinned SHA. Root ecosystem integration, source audit and portable installer gates must verify this exact manifest after promotion. A real authenticated browser regression is still required to establish the live ChatGPT Web UI has recovered the full KAP/2 reply; unit/Chromium fixture tests do not prove that.

## Install
```sh
curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh -s -- --preset full --channel release --yes
```
The release channel installs the specific component revisions from `ecosystem.release.json`.
