# K.I.T.T. Ecosystem 0.16.31

Fix an operator-visible Agent/Proxy binding mismatch: a v5 Agent request for `gemini-web` cannot silently be fulfilled by an instance exposing only `chatgpt-web`. The reverse proxy returns 409 `agent_model_mismatch` before sending the prompt to WebChat; rebind the role to the desired instance. Normal non-Agent compatible OpenAI requests are unaffected.

Pins:
- Agent CLI 0.88.30: `dd63d72b1108bc15f8099d7eb28774be0c4b2ca8`
- Reverse Proxy 5.4.16: `d992cbedb6b6a10644a8ed58d14c6210cbd1ae66`
- Assistant Runtime 0.4.21: `190139808f9999f4b8fc2c74919425bcab1d22b2`
- Other component pins remain unchanged from 0.16.30.

Verification: Proxy CI and Docker, Assistant CI, Agent PR Checks and ecosystem release composition. The actual local Bubblewrap installation, VM guest and local System One models cannot be validated from source CI alone.
