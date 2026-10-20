# KITT Ecosystem 0.16.37

- Agent CLI 0.88.36: `d76ef6ae56033dd78b19807a2feef61e176293b6`
- Assistant Runtime 0.4.27: `297a5bff3db57ba0e7c4e7517d93152848e9d20c`
- Reverse Proxy 5.4.16: `d992cbedb6b6a10644a8ed58d14c6210cbd1ae66`
- Protocol, Memory, Toolbox and AI Workers: unchanged immutable component pins.

The Agent process runner no longer attempts read-only binding of `/etc/resolv.conf` to itself when that file is a symlink into `/run`; network-isolated workspaces keep DNS disabled, while explicitly network-enabled profiles can access canonical resolver targets without exposing unrelated host sockets. The KITT host still enforces its existing Bubblewrap 0.12.0 minimum, tool capabilities and user autonomy policy. Release checks do not replace a real end-to-end run on Ubuntu with systemd-resolved and authenticated ChatGPT UI capture.
