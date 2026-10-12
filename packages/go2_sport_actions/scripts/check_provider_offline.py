# SPDX-License-Identifier: Apache-2.0
"""Loopback gRPC test: separate generated Skill/service bindings, no SDK or Atlas."""
import asyncio
import json
import os
from pathlib import Path
import select
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import patch

from go2_sport_actions.action_provider import ActionSkill
from go2_sport_actions.skills import DEFINITIONS
from go2_sport_actions_mcp import (
    PerformAction_Request, GetActionStatus_Request, CancelAction_Request,
)

ROOT = Path(__file__).resolve().parents[1]


async def check(endpoint):
    channels = []
    def connect(**kwargs):
        assert kwargs["provider_id"] == "unitree_go2_sport_runtime"
        assert kwargs["transport"] == "grpc"
        channel = SimpleNamespace(endpoint=endpoint, closed=False)
        def close():
            channel.closed = True
        channel.close = close
        channels.append(channel)
        return channel
    with patch("go2_sport_actions.action_provider.ATLAS.connect_capability", side_effect=connect):
        for definition in DEFINITIONS:
            wrapper = ActionSkill(definition["action"])
            wrapper.init(definition["init"])
            assert wrapper.initialized and len(wrapper.skill._mcp_handlers) == 3
            reply = await wrapper.execute(PerformAction_Request(request_id=definition["action"]))
            assert not reply.accepted
            assert json.loads(reply.message)["reason"] == "physical_backend_not_configured", reply.message
            status = await wrapper.status(GetActionStatus_Request(run_id="unknown"))
            assert not json.loads(status.result_json)["known"]
            cancel = await wrapper.cancel(CancelAction_Request(run_id="unknown"))
            assert not cancel.ok
        assert len(channels) == 21 and all(c.closed for c in channels)


def main():
    runtime = ROOT / "runtime_service"
    env = dict(os.environ)
    api = subprocess.check_output(
        [env.get("RBNX_BIN", "rbnx"), "path", "robonix-api"], text=True).strip()
    env["PYTHONPATH"] = os.pathsep.join(
        [api, str(runtime), str(runtime / "rbnx-build/codegen/proto_gen")])
    process = subprocess.Popen(
        [sys.executable, "-u", str(runtime / "scripts/offline_server.py")],
        env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    try:
        ready, _, _ = select.select([process.stdout], [], [], 15)
        assert ready, "offline service did not become ready"
        endpoint = process.stdout.readline().strip()
        assert endpoint.startswith("127.0.0.1:"), endpoint
        asyncio.run(check(endpoint))
    finally:
        process.communicate("", timeout=10)
    assert process.returncode == 0
    print("PASS: seven Skill clients -> separate service gRPC, 21 calls, zero robot motion")


if __name__ == "__main__":
    main()
