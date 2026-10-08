# KITT Ecosystem 0.14.3 — Chat draft submission

Reverse Proxy 5.0.2 fixes a selector path matching the reported Gemini behavior: the draft is filled, but only manually clicking the send button submits it. A last visible disabled control previously masked enabled controls and forced Enter fallback. The proxy now finds an enabled visible match across the selector cascade and logs the chosen dispatch method.

Existing acceptance checks still prevent an ignored click or detached composer from being treated as a successful submission. No automatic second send occurs after uncertain acceptance. WebChat owns token limits.

The release manifest pins Proxy 5.0.2 with the existing compatible Agent 0.85.0, Protocol 0.10.0, Assistant 0.1.33 / runtime 0.3.0 and Workers 0.1.57 revisions. No wire or dependency change requires consumer bumps.

The submission regression covers a disabled candidate hiding an active send control. The required Chromium CI exercises native/ARIA states, English/Portuguese selectors and exact multiline prompt submission. No authenticated Gemini session was executed.
