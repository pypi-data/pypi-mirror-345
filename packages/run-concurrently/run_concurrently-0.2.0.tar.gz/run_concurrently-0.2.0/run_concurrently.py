#!/usr/bin/env python3
"""
run_concurrently.py – tiny, dependency-free alternative to `npx concurrently`

Usage:
    python run_concurrently.py "cmd 1" "cmd 2" ... "cmd N"

Example:
    python run_concurrently.py "npm run dev" "pytest -q" "uvicorn app:app --reload"
"""

from __future__ import annotations

import argparse
import asyncio
import os
import signal
import sys
from typing import List

# ──────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────
ANSI_RESET = "\x1b[0m"
ANSI_COLORS = [
    "\x1b[31m",  # red
    "\x1b[32m",  # green
    "\x1b[33m",  # yellow
    "\x1b[34m",  # blue
    "\x1b[35m",  # magenta
    "\x1b[36m",  # cyan
]


def colour(index: int) -> str:
    """Pick a stable colour for a given command index."""
    return ANSI_COLORS[index % len(ANSI_COLORS)]


def _make_process_group_kwargs() -> dict:
    """
    Cross-platform helper to ensure every child is launched in its *own*
    process group, so we can send signals (SIGINT/SIGTERM) to the whole tree.
    """
    if os.name == "nt":  # Windows
        import subprocess  # local import to keep std-lib only

        return {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    else:  # POSIX
        return {"preexec_fn": os.setsid}


# ──────────────────────────────────────────────────────────────────────────
# Core async runner
# ──────────────────────────────────────────────────────────────────────────
async def _stream_output(idx: int, cmd: str, proc: asyncio.subprocess.Process) -> None:
    """
    Forward the combined stdout/stderr of *proc* to our own stdout,
    prefixing each line with an index and colour.
    """
    prefix = f"{colour(idx)}[{idx}] {cmd.split()[0]:<10}│{ANSI_RESET} "
    while True:
        line = await proc.stdout.readline()
        if not line:  # EOF
            break
        # output already includes newline
        sys.stdout.write(prefix + line.decode(errors="replace"))
        sys.stdout.flush()


async def _run_one(idx: int, cmd: str) -> int:
    """
    Launch *cmd* as a shell subprocess and wait for it, while streaming output.
    Return the subprocess's exit code.
    """
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        **_make_process_group_kwargs(),
    )

    try:
        # forward output until the process finishes
        await _stream_output(idx, cmd, proc)
        return await proc.wait()
    except asyncio.CancelledError:
        if proc.returncode is None:
            try:
                if os.name == "nt":
                    proc.send_signal(signal.CTRL_BREAK_EVENT)
                else:
                    os.killpg(proc.pid, signal.SIGINT)
                await asyncio.wait_for(proc.wait(), 3)
            except (asyncio.TimeoutError, ProcessLookupError):
                proc.kill()  # hard stop
                await proc.wait()
        raise


async def _main_async(cmds: List[str]) -> int:
    """
    Run all *cmds* concurrently.  If any exits with non-zero, cancel the rest
    and return that exit status; otherwise 0.
    """
    loop = asyncio.get_running_loop()
    tasks = [
        asyncio.create_task(_run_one(idx, cmd), name=f"cmd-{idx}")
        for idx, cmd in enumerate(cmds, start=1)
    ]

    # Relay Ctrl-C to children and cancel tasks
    stop = asyncio.Event()

    def _cancel_all(*_: object) -> None:
        if not stop.is_set():
            stop.set()
            for t in tasks:
                t.cancel()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _cancel_all)

    # Wait for tasks; react to the first failure
    try:
        while tasks:
            done, _pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_COMPLETED
            )
            for t in done:
                tasks.remove(t)
                try:
                    code = await t
                except asyncio.CancelledError:
                    continue
                if code != 0:  # propagate failure
                    _cancel_all()
                    return code
    finally:
        # ensure remaining children are killed
        for t in tasks:
            t.cancel()
    return 0


# ──────────────────────────────────────────────────────────────────────────
# CLI entry-point
# ──────────────────────────────────────────────────────────────────────────
def _parse_args() -> List[str]:
    parser = argparse.ArgumentParser(
        description="Run multiple shell commands concurrently "
        "with coloured, prefixed output."
    )
    parser.add_argument("commands", nargs="+", help="Commands to run (quote each)")
    return parser.parse_args().commands


def main() -> None:
    cmds = _parse_args()
    try:
        exit_code = asyncio.run(_main_async(cmds))
    except KeyboardInterrupt:
        exit_code = 130  # conventional code for SIGINT
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
