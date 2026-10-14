# KITT 0.15.31 — Safe Python via KAP/2

The full release snapshot pins Agent CLI **0.87.10** with the
`sandbox.python` host operation, Assistant Runtime **0.3.22**, and
AI Workers **0.1.61** with synchronized Python `uv.lock` references.
The executor reuses the existing `python_compute` restricted AST interpreter,
rather than allowing unrestricted Python. KAP/2 grammar and Protocol 0.13.2
remain unchanged. See [release 0.15.31](docs/RELEASE_0.15.31.md).

# Ecosystem 0.15.30 — KAP/2 DOM capture after transcript virtualization

The release installer pins Reverse Proxy **5.3.6** and validates its npm package/lock versions before building. The fix locates a fresh browser-rendered KAP envelope after the submitted prompt even if old chat DOM is virtualized; collapsed malformed frames are forwarded solely to the Agent repair flow. No changes to the other component pins. See [release 0.15.30](docs/RELEASE_0.15.30.md).

undefined