# K.I.T.T. Ecosystem 0.16.30

## Release pins

- Agent CLI **0.88.30**: `dd63d72b1108bc15f8099d7eb28774be0c4b2ca8`
- Reverse Proxy **5.4.15**: `23d86ef31e0d61c4ab8e2db12c9d465e8a6b41d8`
- Assistant Runtime **0.4.21**: `190139808f9999f4b8fc2c74919425bcab1d22b2`
- Protocol: `ac9baf8b4b8f03e839471c7bbb7d5e52e970a9ec`
- Memory: `646a213672833c42f0e4eacf1faf048261e5a4c6`
- Toolbox: `d5e0cf8fde2af18778ee900e67b56a302831ebf1`
- AI Workers: `1d228e3e451cbab7d463149f13230bd8f800bbbf`

## Contract boundaries

All changes remain within existing Agent/Proxy responsibilities. Agent controls tools, memory, routing and authorized workspace/VM operations; the Reverse Proxy controls transport, browser sessions and the structural Agent Contract v5 boundary. Host strong sandbox requirements are unchanged; default allow-all never bypasses the host's capabilities, sandbox or user ASK/DENY settings.

## Verification

Required: Agent PR Checks, Proxy CI, Assistant CI, ecosystem-main/integration checks. Authenticated browser sessions, strong Bubblewrap host installation, Windows/Wine Oracles and actual Laya/Ollaya decision-model accuracy are external environment checks and are not certified by repository CI alone.
