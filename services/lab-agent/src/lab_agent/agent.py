"""The home agent: registers tools, then claims queued commands and runs them.

Only outbound HTTPS to Supabase; no inbound ports. Polls for now (one cheap RPC
every couple of seconds); Supabase Realtime can replace polling later without
changing anything else, because claim_next_command stays the single entry point.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx

from .events import now_ts
from .registry import Registry
from .runner import Runner
from .supabase import Supabase


def register_tools(db: Supabase, registry: Registry, agent_id: str) -> None:
    db.upsert(
        "tools",
        [
            {
                "name": t.name,
                "description": t.description,
                "requires_confirmation": t.requires_confirmation,
                "args_schema": t.args_schema(),
                "agent_id": agent_id,
            }
            for t in registry
        ],
        on_conflict="name",
    )


def handle(db: Supabase, runner: Runner, cmd: dict[str, Any]) -> str:
    result = runner.request(
        cmd["tool"],
        cmd.get("args") or {},
        actor="agent",
        confirmed=bool(cmd.get("confirmed")),
        remote=True,
    )
    if not result.allowed:
        status, text = (
            "rejected",
            f"{result.checked.payload.rule}: {getattr(result.checked.payload, 'reason', '')}",
        )
    elif result.ok:
        status, text = "done", "sent"
    else:
        status, text = "failed", result.outcome.payload.error  # type: ignore[union-attr]
    # run_id is a foreign key to runs, and runs exist only after `lab sync`, so name the
    # local run in the result instead. A failed status update must not stop the agent.
    try:
        db.update(
            "commands",
            {"id": cmd["id"]},
            {
                "status": status,
                "result": f"{text} (run {runner.log.run_id})",
                "finished_at": now_ts(),
            },
        )
    except httpx.HTTPError as e:
        print(f"  could not record result for command {cmd['id']}: {e}", flush=True)
    return status


def serve(
    db: Supabase,
    runner: Runner,
    agent_id: str,
    *,
    poll_s: float = 2.0,
    max_age_s: int = 60,
    stop: Callable[[], bool] = lambda: False,
) -> None:
    register_tools(db, runner.registry, agent_id)
    while not stop():
        claimed = db.rpc(
            "claim_next_command", {"agent": agent_id, "max_age": f"{max_age_s} seconds"}
        )
        if claimed:
            for cmd in claimed:
                print(f"{cmd['tool']} {cmd.get('args')}: {handle(db, runner, cmd)}", flush=True)
            continue
        time.sleep(poll_s)
