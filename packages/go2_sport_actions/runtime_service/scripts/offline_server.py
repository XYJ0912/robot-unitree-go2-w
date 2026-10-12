# SPDX-License-Identifier: Apache-2.0
"""Private loopback test fixture; never starts a physical backend."""
from concurrent.futures import ThreadPoolExecutor
import sys

import grpc
import robonix_contracts_pb2_grpc as contracts
from go2_sport_runtime import provider


def main():
    provider.init({"backend": "catalog"})
    assert not provider._manager.configured
    assert not provider.skill._mcp_handlers
    server = grpc.server(ThreadPoolExecutor(max_workers=2))
    for suffix, method, handler in (
        ("Execute", "ExecuteAction", provider.execute),
        ("Status", "GetActionStatus", provider.status),
        ("Cancel", "CancelAction", provider.cancel),
    ):
        base = getattr(contracts, f"RobonixServiceUnitreeGo2SportRuntime{suffix}Servicer")
        implementation = type("Offline" + suffix, (base,), {method: staticmethod(handler)})()
        register = getattr(contracts, f"add_RobonixServiceUnitreeGo2SportRuntime{suffix}Servicer_to_server")
        register(implementation, server)
    port = server.add_insecure_port("127.0.0.1:0")
    assert port
    server.start()
    try:
        print(f"127.0.0.1:{port}", flush=True)
        sys.stdin.read()
    finally:
        server.stop(0).wait()
        provider.shutdown()
    assert provider._daemon_process is None


if __name__ == "__main__":
    main()
