# K.I.T.T. Ecosystem 0.16.29

## Immutable component pins

- Agent CLI 0.88.27: 67bc827ab29eabd998522d6d7efe39c41fadc399
- Assistant Runtime 0.4.19 / Rust workspace 0.1.61: e1f56948c759fff36153343aa72121faa1507bca
- Reverse Proxy 5.4.14: 9dc9e788d77827eb5df04775a1c1b58a231764b5
- Protocol: ac9baf8b4b8f03e839471c7bbb7d5e52e970a9ec
- Memory: 646a213672833c42f0e4eacf1faf048261e5a4c6
- Toolbox: d5e0cf8fde2af18778ee900e67b56a302831ebf1
- AI Workers: 1d228e3e451cbab7d463149f13230bd8f800bbbf

## Changes

Agent CLI prevents retries of unchanged host subprocess calls when the required Bubblewrap sandbox is unavailable. Repeated mixed tool outcomes (failed process + unchanged repository observation) now produce a bounded no-progress block. Browser Reverse Proxy transport socket timeouts and ambiguous 408/504 results are not automatically replayed, avoiding duplicate logical WebChat requests.

Assistant Runtime updates only Python package version, Agent minimum version, uv.lock immutable SHA and CI source pins. Rust/Cargo and unrelated module versions are intentionally unchanged.

## Validation boundary

GitHub Agent PR Checks, Assistant CI, and root ecosystem integration / main-head pin checks must pass. This release does not claim authenticated WebChat, native host sandbox provisioning or Windows Oracle end-to-end conformance without those runtime environments.
