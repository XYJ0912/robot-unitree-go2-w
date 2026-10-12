# Unitree Go2 sport runtime

`robonix.service.unitree.go2.sport_runtime` is a separate Service package bundled
in the same checkout as the seven Go2 Skills. It owns the existing ActionManager
and Go2 SDK daemon; its only public contracts are the service lifecycle,
execute, status and cancel interfaces. It exposes no MCP tools.

Build this directory as a package:

```bash
rbnx validate runtime_service
rbnx build runtime_service
```

The parent `examples/seven-skills.yaml` starts this service once and the seven
Skill processes independently. Configuration and action timing are unchanged.
`backend: catalog` is motion-disabled; `external` or `managed` uses the existing
operator-approved daemon setup. Merely starting the service sends no action.

Client IDL copies in the parent package must match this package; regression tests
check that equality and real loopback gRPC calls with a motion-disabled backend.
This package can be built independently without the parent's Python modules.

License: Apache-2.0 (see LICENSE).
