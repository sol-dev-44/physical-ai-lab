"""`lab` command line. Run `lab --help`.

Tool sets come from a Python entry point "module:function" returning a Registry,
via --tools or LAB_TOOLS, e.g. LAB_TOOLS=exp000_ir_bridge.tools:build
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from .config import Settings
from .log import EventLog, read_log, validate_log
from .registry import Registry
from .replay import replay
from .runner import CommandResult, Runner, run_path
from .summary import summarize_run


def load_tools(spec: str | None) -> Registry:
    if not spec:
        raise SystemExit("No tool set. Pass --tools module:function or set LAB_TOOLS.")
    module, _, fn = spec.partition(":")
    registry = getattr(importlib.import_module(module), fn or "build")()
    if not isinstance(registry, Registry):
        raise SystemExit(f"{spec} did not return a Registry")
    return registry


def new_run_id(experiment_id: str, suffix: str = "") -> str:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{experiment_id.split('-')[0]}-{stamp}{'-' + suffix if suffix else ''}"


def make_runner(s: Settings, a: argparse.Namespace, registry: Registry, suffix: str = "") -> Runner:
    run_id = getattr(a, "run_id", None) or new_run_id(a.experiment, suffix)
    log = EventLog(run_path(s.events_dir, a.experiment, run_id), run_id)
    return Runner(registry, log, dry_run=getattr(a, "dry_run", False))


def denial(result: CommandResult) -> str:
    p = result.checked.payload
    return f"denied by {p.rule}" + (f": {p.reason}" if p.reason else "")


# ---------------------------------------------------------------- commands
def cmd_tools(s: Settings, a: argparse.Namespace) -> int:
    for t in load_tools(a.tools or s.tools):
        flags = [
            f for f, on in (("confirm", t.requires_confirmation), ("manual", t.manual_only)) if on
        ]
        print(f"{t.name:24} {t.description}{'  [' + ', '.join(flags) + ']' if flags else ''}")
    return 0


SESSION_HELP = """\
  <tool> [json-args] [!]   request a command: fan.power | robot.forward {"seconds": 1}
                           (! confirms a tool that requires confirmation)
  y | n [note]             record whether the last command worked
  note <text>              add a note to the log
  tools                    list tools
  end | abort              close the run"""


def cmd_session(s: Settings, a: argparse.Namespace) -> int:
    registry = load_tools(a.tools or s.tools)
    runner = make_runner(s, a, registry, "null" if a.dry_run else "")
    runner.start(a.experiment)
    print(f"run {runner.log.run_id} -> {runner.log.path}\n{SESSION_HELP}")
    last = None
    status = "completed"
    try:
        while True:
            try:
                line = input(f"{runner.log.run_id}> ").strip()
            except EOFError:
                break
            if not line:
                continue
            word, _, rest = line.partition(" ")
            if word in ("end", "quit", "exit"):
                break
            if word == "abort":
                status = "aborted"
                break
            if word == "tools":
                for t in registry:
                    print(f"  {t.name:22} {t.description}")
            elif word == "note":
                runner.note(rest or "(empty)")
            elif word in ("y", "n"):
                if last is None:
                    print("  nothing to observe yet")
                    continue
                runner.observe(last, word == "y", note=rest or None)
                last = None
            else:
                raw = rest.strip()
                confirmed = raw == "!" or raw.endswith(" !")
                raw = raw.removesuffix("!").strip() if confirmed else raw
                try:
                    args = json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    print('  args must be JSON, e.g. {"seconds": 1}')
                    continue
                result = runner.request(word, args, actor="human", confirmed=confirmed)
                last = result
                if result.ok:
                    print("  sent. did it work? (y/n)")
                elif result.allowed:
                    print(f"  failed: {result.outcome.payload.error}")  # type: ignore[union-attr]
                else:
                    print(f"  {denial(result)}")
    finally:
        runner.end(status)
    print(json.dumps(summarize_run(read_log(runner.log.path)), indent=2))
    return 0


def cmd_trials(s: Settings, a: argparse.Namespace) -> int:
    """N automated sends of one tool, each observed by you (y/n)."""
    registry = load_tools(a.tools or s.tools)
    runner = make_runner(s, a, registry, "null" if a.dry_run else "")
    runner.start(a.experiment, trials=a.n, tool=a.tool)
    args = json.loads(a.args) if a.args else {}
    tool = registry.get(a.tool)
    interval = max(a.interval, tool.min_interval_s if tool else 0)
    for i in range(1, a.n + 1):
        if i > 1:
            time.sleep(interval)
        result = runner.request(a.tool, args, actor="cli", automated=True)
        if not result.allowed:
            print(f"trial {i}: {denial(result)}")
            runner.end("aborted")
            return 1
        answer = (
            input(f"trial {i}/{a.n} {'sent' if result.ok else 'FAILED'}. worked? [y/n] ")
            .strip()
            .lower()
        )
        runner.observe(result, answer.startswith("y"))
    runner.end("completed")
    print(json.dumps(summarize_run(read_log(runner.log.path)), indent=2))
    return 0


def cmd_replay(s: Settings, a: argparse.Namespace) -> int:
    source = read_log(Path(a.log))
    a.experiment = source[0].payload.experiment_id  # type: ignore[union-attr]
    registry = load_tools(a.tools or s.tools)
    runner = make_runner(s, a, registry, "replay-null" if a.dry_run else "replay")
    replay(source, runner)
    print(json.dumps(summarize_run(read_log(runner.log.path)), indent=2))
    return 0


def cmd_validate(_s: Settings, a: argparse.Namespace) -> int:
    bad = 0
    for p in a.logs:
        issues = validate_log(Path(p).read_text().splitlines())
        print(f"{'ok ' if not issues else 'BAD'} {p}")
        for x in issues:
            print(f"    line {x.line}: {x.message}")
        bad += bool(issues)
    return 1 if bad else 0


def cmd_summary(_s: Settings, a: argparse.Namespace) -> int:
    print(json.dumps(summarize_run(read_log(Path(a.log))), indent=2))
    return 0


def cmd_sync(s: Settings, _a: argparse.Namespace) -> int:
    from .supabase import Supabase
    from .sync import sync

    report = sync(
        s.events_dir,
        Supabase(*s.require_supabase()),
        site_url=s.site_url,
        secret=s.revalidate_secret,
    )
    for r in report.synced:
        print(f"synced  {r}")
    for k, v in report.skipped.items():
        print(f"skipped {k}: {v}")
    return 1 if report.skipped else 0


def cmd_agent(s: Settings, a: argparse.Namespace) -> int:
    from .agent import serve
    from .supabase import Supabase

    registry = load_tools(a.tools or s.tools)
    runner = make_runner(s, a, registry, "agent")
    runner.start(a.experiment)
    print(f"agent {s.agent_id}: run {runner.log.run_id}, {len(registry)} tools. Ctrl-C to stop.")
    try:
        serve(Supabase(*s.require_supabase()), runner, s.agent_id)
    except KeyboardInterrupt:
        pass
    finally:
        runner.end("completed")
    return 0


def cmd_discover(_s: Settings, a: argparse.Namespace) -> int:
    from .devices.broadlink_ir import discover

    for d in discover(a.timeout):
        print(d)
    return 0


def cmd_learn(_s: Settings, a: argparse.Namespace) -> int:
    from .devices.broadlink_ir import BroadlinkBlaster
    from .devices.codes import CodeBook

    blaster = BroadlinkBlaster(id="learn", host=a.host, codes=CodeBook(Path(a.codes)))
    for name in a.names:
        input(
            f"Ready to learn {name!r}: press Enter, then press the remote button once at the RM4..."
        )
        blaster.learn(name)
        print(f"  saved {name} to {a.codes}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="lab", description="Lab agent: tools, safety gate, event logs."
    )
    p.add_argument("--tools", help="tool set entry point, module:function (default: $LAB_TOOLS)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("tools", help="list tools").set_defaults(fn=cmd_tools)

    sp = sub.add_parser("session", help="interactive run: send commands, record outcomes")
    sp.add_argument("experiment")
    sp.add_argument("--run-id")
    sp.add_argument(
        "--dry-run", action="store_true", help="null test: log everything, send nothing"
    )
    sp.set_defaults(fn=cmd_session)

    sp = sub.add_parser("trials", help="N automated sends of one tool, observed by you")
    sp.add_argument("experiment")
    sp.add_argument("tool")
    sp.add_argument("-n", type=int, default=10)
    sp.add_argument("--args", help="JSON args")
    sp.add_argument("--interval", type=float, default=1.0, help="seconds between trials")
    sp.add_argument("--run-id")
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(fn=cmd_trials)

    sp = sub.add_parser("replay", help="re-issue a run's requests as a new run")
    sp.add_argument("log")
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(fn=cmd_replay)

    sp = sub.add_parser("validate", help="check logs against the contract")
    sp.add_argument("logs", nargs="+")
    sp.set_defaults(fn=cmd_validate)

    sp = sub.add_parser("summary", help="fold a log into its summary")
    sp.add_argument("log")
    sp.set_defaults(fn=cmd_summary)

    sub.add_parser("sync", help="publish local logs to Supabase").set_defaults(fn=cmd_sync)

    sp = sub.add_parser("agent", help="serve commands queued from the website")
    sp.add_argument("experiment")
    sp.set_defaults(fn=cmd_agent)

    sp = sub.add_parser("discover", help="find BroadLink devices on the network")
    sp.add_argument("--timeout", type=float, default=5)
    sp.set_defaults(fn=cmd_discover)

    sp = sub.add_parser("learn", help="learn IR codes from a remote")
    sp.add_argument("--host", required=True)
    sp.add_argument("--codes", required=True, help="code book JSON path")
    sp.add_argument("names", nargs="+")
    sp.set_defaults(fn=cmd_learn)

    a = p.parse_args(argv)
    return a.fn(Settings.from_env(), a)


if __name__ == "__main__":
    sys.exit(main())
