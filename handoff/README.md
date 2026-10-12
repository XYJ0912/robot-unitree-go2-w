# Go2W handoff archive

`archive-20261012/` preserves the hand-written documentation, read-only
probe source, scripts, patch, and exported evidence from the original
`GO2W_HANDOFF` directory outside `source/`. It is historical material, not
the active Go2W runtime or a claim that the original Robonix source snapshot
is present in this repository. Relative `source/robonix` links and the
`check_bundle.py` script refer to the original handoff bundle and are not
expected to work from this archive.

The active Go2W commissioning code copied from the former local
`source/robot-unitree-go2w` directory is in
[`deploy/go2w-readonly-commissioning/`](../deploy/go2w-readonly-commissioning/README.md).
It remains experimental: real camera snapshot was demonstrated locally,
health is mock-only, and motion is disabled. The older directory is retained
until this new location has been checked in its intended environment.

Not copied: the separate Unitree SDK checkout (this repository already has an
SDK submodule, but at a different pinned commit), compiled outputs, virtual environments,
runtime logs, embedded Git directories, or robot imagery. The original
handoff tree remains untouched. See [Go2W status](../docs/go2w/README.md).
