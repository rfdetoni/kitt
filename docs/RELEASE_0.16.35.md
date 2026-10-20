# K.I.T.T. Ecosystem 0.16.35

- Agent CLI 0.88.34: `66e8b4938bd6e15e04664fc3f336dd4e3b4082fb`
- Assistant Runtime 0.4.25: `399ac70a980f512330a17bd823f1036246a4ab2e`
- Reverse Proxy 5.4.16: `d992cbedb6b6a10644a8ed58d14c6210cbd1ae66`
- Protocol, Memory, Toolbox and AI Workers retain unchanged immutable SHA pins.

Goals now preserve bounded previous host reads across turn retries. Source edits and Markdown reports produced via `kitt_runtime.repo.write_file` enter the Goal review path set, closing a hole where successful file writes were not included in outer verification. Host sandbox policy and independent validation remain mandatory. Validate root installer ecosystem and actual local WebChat/VM deployment separately.
