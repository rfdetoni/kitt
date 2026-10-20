# K.I.T.T. Ecosystem 0.16.32

Versions and immutable pins:
- Agent CLI 0.88.31 `fbb6029a59e89b4244a377f37bde3b0b3a005d00`
- Assistant Runtime 0.4.22 `a1f7f68c019a93297688ba40268f5c216881f7c5`
- Reverse Proxy 5.4.16 `d992cbedb6b6a10644a8ed58d14c6210cbd1ae66`
- Protocol / Memory / Toolbox / AI Workers remain pinned to their 0.16.31 revisions.

The Agent tool catalog and runtime.capabilities expose Bubblewrap >=0.12 availability. This only prevents wasted process commands and does not install the host OS dependency or downgrade sandbox isolation. Verify on the target workstation separately.
