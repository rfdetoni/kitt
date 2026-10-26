# KITT 0.16.57 — ACP v1 session history and isolated cancellation

## Immutable release pins

- Agent CLI 0.88.91: `543b11a7dcafc02dc275b30f14a565d48936f14a`
- Reverse Proxy 5.4.26: `a757b21a8225645355bdd9bda0b896e1c9539c28` (unchanged)
- All other component pins remain unchanged and immutable.

## Corrections

- On ACP v1 `session/load`, the Agent replays persisted user and assistant
  messages, in order, through bounded `session/update` chunks, then returns
  `{}` to match the v1 schema.
- `session/cancel` cancels permission requests belonging only to that
  conversation, not to other concurrently active ACP sessions.
- Includes regression tests for 20 KiB history replay and concurrent-session
  permission cancellation; Agent tests, Windows, Docker and Podman PR gates.

## Validation boundaries

Release CI validates cross-repository immutable pins and end-to-end installer,
including gateway contracts and the Assistant dependency lock. External IDE
implementations and real customer sessions are not part of these tests.

## Installer reliability fix

The Linux end-to-end check exposed a redundant VCS clone: pip fetched the
pinned kitt-protocol URL while installing the already staged Agent CLI source.
A transient early EOF made the installation fail even though the local
protocol wheel was available. Main and release modes now resolve only
third-party requirements remotely and install KITT components once, from
the manifest-selected local checkouts, using --no-deps. A mocked
main-mode installer regression verifies no nested Git clone is requested.
