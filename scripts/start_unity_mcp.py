#!/usr/bin/env python3
"""Start the Unity editor for this project and wait until its MCP server
is reachable, with no manual clicking.

The in-editor half lives in Unity/Assets/Editor/McpAutoStart.cs, which
starts the MCP-for-Unity local HTTP server and connects the bridge on
every editor load. This script is the outer half: it launches the editor
if needed and blocks until http://127.0.0.1:8080/mcp answers.

Usage:
    python3 scripts/start_unity_mcp.py            # start if needed, wait
    python3 scripts/start_unity_mcp.py --restart  # kill editor, relaunch
    python3 scripts/start_unity_mcp.py --status   # probe and exit

Exit codes: 0 = MCP reachable, 1 = failure/timeout.
After the first successful run in a Claude Code session, run /mcp there
once so the session (re)connects to the UnityMCP server.
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT = os.path.join(REPO_ROOT, "Unity")
MCP_URL = "http://127.0.0.1:8080/mcp"
LOG = "/tmp/unity_editor_mcp.log"
WAIT_SECONDS = 600


def unity_binary():
    version_file = os.path.join(PROJECT, "ProjectSettings", "ProjectVersion.txt")
    with open(version_file) as f:
        version = f.read().split()[1]
    path = os.path.expanduser(f"~/Unity/Hub/Editor/{version}/Editor/Unity")
    if not os.path.exists(path):
        sys.exit(f"FAIL: Unity {version} not found at {path}")
    return path


def _post(payload, session_id=None, timeout=3):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    req = urllib.request.Request(MCP_URL, data=json.dumps(payload).encode(),
                                 headers=headers)
    return urllib.request.urlopen(req, timeout=timeout)


def mcp_reachable():
    """True when the endpoint completes an MCP initialize handshake.

    Note: the headless server process answers this even when no Unity
    editor is attached to it, so this alone does not prove a working
    bridge; see unity_attached().
    """
    try:
        with _post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": "2025-06-18",
                               "capabilities": {},
                               "clientInfo": {"name": "start_unity_mcp",
                                              "version": "1.0"}}}) as resp:
            return resp.status == 200
    except Exception:
        return False


def unity_attached(deadline_seconds=8):
    """True when a Unity editor session is attached to the MCP server.

    A Unity-backed tools/call answers within ~2s when the editor bridge
    is connected; with no editor it hangs emitting only SSE pings, so a
    short deadline separates the two states.
    """
    try:
        with _post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": "2025-06-18",
                               "capabilities": {},
                               "clientInfo": {"name": "start_unity_mcp",
                                              "version": "1.0"}}}) as resp:
            sid = resp.headers.get("mcp-session-id")
        _post({"jsonrpc": "2.0", "method": "notifications/initialized"},
              sid).close()
        start = time.time()
        with _post({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                    "params": {"name": "read_console",
                               "arguments": {"action": "get",
                                             "types": ["error"],
                                             "count": 1}}},
                   sid, timeout=deadline_seconds) as resp:
            while time.time() - start < deadline_seconds:
                line = resp.readline().decode(errors="replace")
                if not line:
                    return False
                if line.startswith("data:") and '"result"' in line:
                    return True
        return False
    except Exception:
        return False


def editor_pids():
    out = subprocess.run(
        ["pgrep", "-f", f"Editor/Unity.*{PROJECT}"],
        capture_output=True, text=True).stdout.split()
    return [int(p) for p in out]


def launch_editor():
    env = dict(os.environ, DISPLAY=os.environ.get("DISPLAY", ":0"))
    with open(LOG, "ab") as log:
        subprocess.Popen(
            [unity_binary(), "-projectPath", PROJECT],
            stdout=log, stderr=log, env=env,
            start_new_session=True)
    print(f"Unity launching (log: {LOG})")


def stop_editor():
    pids = editor_pids()
    for pid in pids:
        os.kill(pid, signal.SIGTERM)
    deadline = time.time() + 30
    while time.time() < deadline and editor_pids():
        time.sleep(1)
    for pid in editor_pids():
        os.kill(pid, signal.SIGKILL)
    if pids:
        print("Unity editor stopped")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--restart", action="store_true",
                    help="stop any running editor first")
    ap.add_argument("--status", action="store_true",
                    help="probe MCP endpoint and exit")
    args = ap.parse_args()

    if args.status:
        reach = mcp_reachable()
        attached = unity_attached() if reach else False
        print(f"server endpoint: {'up' if reach else 'DOWN'} at {MCP_URL}")
        print(f"unity session:   {'attached' if attached else 'NOT attached'}")
        print("PASS" if attached else "FAIL")
        sys.exit(0 if attached else 1)

    if args.restart:
        stop_editor()

    if editor_pids() and unity_attached():
        print(f"PASS: Unity attached to MCP at {MCP_URL}")
        return

    if not editor_pids():
        launch_editor()
    else:
        print("Unity already running; waiting for its MCP bridge "
              "(use --restart if it never connects)")

    start = time.time()
    while time.time() - start < WAIT_SECONDS:
        if unity_attached():
            print(f"PASS: Unity attached to MCP at {MCP_URL} "
                  f"after {int(time.time() - start)}s")
            return
        if not editor_pids():
            sys.exit(f"FAIL: Unity editor exited; see {LOG}")
        time.sleep(3)
    sys.exit(f"FAIL: timed out after {WAIT_SECONDS}s; see {LOG} and the "
             "Unity console for MCP-FOR-UNITY / McpAutoStart messages")


if __name__ == "__main__":
    main()
