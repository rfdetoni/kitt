# K.I.T.T. Ecosystem 0.15.5 — unified Windows/Linux VM helper

## Coordinated versions

- Agent CLI **0.86.7** introduces `kitt vm create` / `kitt vm wizard`.
- Assistant runtime **0.3.5** aligns the Agent version floor and immutable uv.lock source.
- Installer/ecosystem **0.15.5** updates immutable release SHA pins.
- All other ecosystem packages remain on compatible prior pins.

## Usage

```sh
kitt vm create
```

The CLI asks for Windows or Linux, then the path to an operator-owned
`.iso` or standalone `.qcow2`. It reuses existing isolated guest
wizards for CPU/RAM/disk setup, edition/distribution choice and final
confirmation. For unattended setup:

```sh
kitt vm create --os windows --source ~/ISOs/Windows11.iso --variant official --yes
kitt vm create --os linux --source ~/ISOs/debian.iso --distro debian --tools wine --yes
```

The helper does not download guest operating systems or run installers.
QEMU host prerequisites, isolation, guest lifecycle and actual real VM
boot validation remain separate responsibilities. `kitt` and `kitt -p`
continue to work as regular coding agent commands.

See `kitt-agent-cli/docs/VM_CREATION_HELPER.md` for examples and limitations.
