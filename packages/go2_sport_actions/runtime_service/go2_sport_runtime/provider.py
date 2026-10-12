# SPDX-License-Identifier: Apache-2.0
"""Internal gRPC service backed by the existing single-owner chassis daemon."""
import os
from pathlib import Path
import signal
import stat
import subprocess
import threading
import time

from robonix_api import Err, Ok, Service
RUNTIME_ID = "unitree_go2_sport_runtime"
RUNTIME_NAMESPACE = "robonix/service/unitree_go2_sport_runtime"
from go2_sport_runtime import catalog as core
from go2_sport_runtime.daemon_owner import ManagedDaemon
from go2_sport_runtime.runtime import ActionManager, PLANS
import go2_sport_actions_pb2 as messages

skill = Service(id=RUNTIME_ID, namespace=RUNTIME_NAMESPACE, md_path="")

def endpoint(leaf):
    return skill.grpc(f"{RUNTIME_NAMESPACE}/{leaf}")

_manager = ActionManager()
_managed_daemon: ManagedDaemon | None = None
_daemon_process = None
_daemon_lock = threading.RLock()


def _stop_managed_daemon() -> bool:
    global _daemon_process
    process = _daemon_process
    if process is None or process.poll() is not None:
        _daemon_process = None
        return True
    for sig, timeout in ((signal.SIGINT, 3.0), (signal.SIGTERM, 2.0)):
        try:
            os.killpg(os.getpgid(process.pid), sig)
            process.wait(timeout=timeout)
            _daemon_process = None
            return True
        except ProcessLookupError:
            _daemon_process = None
            return True
        except subprocess.TimeoutExpired:
            continue
    return False


def _ensure_managed_daemon() -> str:
    global _daemon_process
    managed = _managed_daemon
    if managed is None:
        return ""
    with _daemon_lock:
        if _daemon_process is not None and _daemon_process.poll() is None:
            return ""
        if not managed.ready_to_activate():
            return "existing Go2 operator and staged-motion runtime acknowledgement is missing"
        if not managed.binary.is_file() or not os.access(managed.binary, os.X_OK):
            return f"Go2 sport daemon is not built: {managed.binary}"
        previous_inode = None
        try:
            previous_inode = managed.socket_path.stat().st_ino
        except FileNotFoundError:
            pass
        try:
            _daemon_process = skill.spawn(
                managed.argv(), env=managed.environment(), log="sdk-daemon.log",
                cwd=Path(__file__).resolve().parents[1])
            deadline = time.monotonic() + 5.0
            while time.monotonic() < deadline:
                if _daemon_process.poll() is not None:
                    _stop_managed_daemon()
                    return "Go2 sport daemon exited during startup; see sdk-daemon.log"
                try:
                    current = managed.socket_path.stat()
                except FileNotFoundError:
                    current = None
                if (current is not None and stat.S_ISSOCK(current.st_mode)
                        and current.st_ino != previous_inode):
                    return ""
                time.sleep(0.05)
        except OSError as exc:
            _stop_managed_daemon()
            return f"Go2 sport daemon startup failed: {exc}"
        _stop_managed_daemon()
        return "Go2 sport daemon did not create its IPC socket"


def _execute_action(name: str | None, request_id: str) -> dict:
    if not isinstance(name, str) or (name not in PLANS and name != "dance"):
        return _manager.execute(name, request_id)
    error = _ensure_managed_daemon()
    if error:
        return {"accepted": False, "run_id": "", "reason": error,
                "request_id": request_id, "motion_sent": False}
    return _manager.execute(name, request_id)


@endpoint("execute")
def execute(request, _context):
    value = _execute_action(request.name, request.request_id)
    return messages.ExecuteAction_Response(
        accepted=value["accepted"], run_id=value["run_id"], message=core.dumps(value))


@endpoint("status")
def status(request, _context):
    return messages.GetActionStatus_Response(
        result_json=core.dumps(_manager.status(request.run_id)))


@endpoint("cancel")
def cancel(request, _context):
    value = _manager.cancel(request.run_id) if request.run_id else _manager.cancel_active()
    return messages.CancelAction_Response(ok=value["ok"], message=core.dumps(value))


@skill.on_init
def init(config):
    global _manager, _managed_daemon
    if config and not isinstance(config, dict):
        return Err("configuration must be an object")
    config = config or {}
    path = str(config.get("daemon_socket") or
               os.environ.get("GO2_SPORT_DAEMON_SOCKET", "")).strip()
    if path and not os.path.isabs(path):
        return Err("daemon_socket must be an absolute Unix socket path")
    backend = str(config.get("backend") or ("external" if path else "catalog"))
    if backend not in {"catalog", "external", "managed"}:
        return Err("backend must be catalog, external or managed")
    if backend == "external" and not path:
        return Err("external backend requires daemon_socket")
    try:
        replacement = ActionManager(path if backend != "catalog" else "",
            dance_variants=config.get("dance_variants", ("dance_1", "dance_2")))
        managed = (ManagedDaemon.from_config(config, path)
                   if backend == "managed" else None)
    except (ValueError, TypeError) as exc:
        return Err(str(exc))
    _manager.shutdown()
    _stop_managed_daemon()
    _managed_daemon = managed
    _manager = replacement
    return Ok()


@skill.on_activate
def activate():
    return Ok()  # Activation does not start the SDK daemon or send commands.


@skill.on_deactivate
def deactivate():
    _manager.shutdown()
    return Ok() if _stop_managed_daemon() else Err("Go2 sport daemon did not exit")


@skill.on_shutdown
def shutdown():
    _manager.shutdown()
    return Ok() if _stop_managed_daemon() else Err("Go2 sport daemon did not exit")


if __name__ == "__main__":
    skill.run()
