# KITT disposable VM autonomy — installer and operator setup

The `--with-vm-lab` flag is **opt-in**. It requires a Linux host with
`qemu-system-x86_64`, `qemu-img` and `ssh` installed, automatically includes
the Agent CLI in module resolution, and aborts before installation if a
prerequisite is missing. It does **not** install host packages with sudo,
create guest images, relax firewalls or silently enable allow-all.

Example:

```sh
./install.sh --preset full --channel edge --with-vm-lab --yes
kitt vm doctor --profile ~/.kitt/vm/profile.json
kitt vm run --profile ~/.kitt/vm/profile.json --goal 'Investigate Wine Win32 event compatibility'
```

For a pin-locked release use `--channel release` after the coordinated
Agent/Assistant ecosystem manifest and locks have been promoted.

To provision the VM once, prepare a private standalone qcow2 image with
Python 3.14+, KITT Agent and a non-root SSH account. Configure sshd with
an operator-owned SSH public key with `restrict,command=` forced to
`python3 -m kitt.vm_worker --workspace <disposable-workspace>`. Store the
private key and pinned host key on the host, chmod 600. The guest must
already contain the working source copy; nothing is mounted from the host.
Record the complete base image SHA-256 in a mode-0600 JSON profile.

QEMU uses `restrict=on,ipv6=off` and one 127.0.0.1 hostfwd rule for
SSH. Optional `gateway_port` forwards guest `10.0.2.100:3000` to a
preapproved host LLM gateway on 127.0.0.1; set zero to deny all guest
outbound network access. The host gateway must separately enforce auth,
token budgets and destination policy.

See Agent documentation `docs/VM_SUPERVISOR.md` and
`docs/VM_AUTONOMY_SECURITY.md` for contract, limitations and checks.

QEMU VM snapshot teardown and actual KITT guest behavior require a real
operator-provisioned VM; CI does not prove hypervisor isolation.
Artifacts are advisory until independently reviewed on the host.
