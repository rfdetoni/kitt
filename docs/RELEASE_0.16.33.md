# K.I.T.T. Ecosystem 0.16.33

## Pins

- Agent CLI **0.88.32**: `f399bf69b6506b7d61c95b9e691f0537cbee8e91`
- Assistant Runtime **0.4.23**: `fa6fad55cc47d4c8c0652d9f1406c27db599c8bf`
- Reverse Proxy **5.4.16**: `d992cbedb6b6a10644a8ed58d14c6210cbd1ae66`
- Protocol: `ac9baf8b4b8f03e839471c7bbb7d5e52e970a9ec`
- Memory: `646a213672833c42f0e4eacf1faf048261e5a4c6`
- Toolbox: `d5e0cf8fde2af18778ee900e67b56a302831ebf1`
- AI Workers: `1d228e3e451cbab7d463149f13230bd8f800bbbf`

Corrects Agent detection for repeated read-only batches and classifies repeated policy and sandbox host failures as non-resolvable blockers. No API/daemon protocol, Rust or unrelated component changes. Installer cross-platform CI validates only the tested checkout; authenticated WebChat, Bubblewrap installation and virtual machine guest verification need the target host.
