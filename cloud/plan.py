"""Job plans (TOML) and the job script they compile to.

A plan says which instance to rent (in provider-neutral terms plus a preference list
of provider type names), what to sync, and the jobs to run. On the instance, jobs run
from a generated bash script under nohup, so an SSH drop never kills them; progress
goes to ~/llm-speaker/.job/ (status, progress, one log per step).

  name = "smoke"
  [instance]
  provider = "lambda"
  types = ["gpu_1x_a10", "gpu_1x_a100_sxm4"]   # preference order; first with capacity wins
  regions = []                                  # empty = any region
  max_price_per_hour = 2.0
  max_hours = 1.5                               # watchdog terminates the instance after this
  min_gpu_mem_gb = 24                           # optional sanity filter
  [sync]
  dirs = ["data/goldset/clips", "data/goldset/vad", "transcriber/context"]
  results = ["data/outputs"]
  [setup]
  commands = ["bash cloud/remote/bootstrap.sh"]
  [[job]]
  name = "whisper-turbo"
  models = ["Systran/faster-whisper-large-v3-turbo"]
  setup = []
  commands = ["uv run python asr/run_whisper.py --model large-v3-turbo --limit 4"]
"""
from __future__ import annotations

import re
import shlex
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Job:
    name: str
    commands: list[str]
    models: list[str] = field(default_factory=list)
    setup: list[str] = field(default_factory=list)


@dataclass
class Plan:
    name: str
    path: str
    provider: str
    types: list[str]
    max_price_per_hour: float
    max_hours: float
    regions: list[str] = field(default_factory=list)
    min_gpu_mem_gb: float = 0
    image: str | None = None
    ssh_key: str | None = None
    ssh_identity: str | None = None
    sync_dirs: list[str] = field(default_factory=list)
    results: list[str] = field(default_factory=lambda: ["data/outputs"])
    setup: list[str] = field(default_factory=list)
    jobs: list[Job] = field(default_factory=list)


def load(path) -> Plan:
    d = tomllib.loads(Path(path).read_text())
    inst, sync = d.get("instance", {}), d.get("sync", {})
    jobs = [Job(name=j["name"], commands=_list(j["commands"]), models=_list(j.get("models", [])),
                setup=_list(j.get("setup", []))) for j in d.get("job", [])]
    for j in jobs:
        if not re.fullmatch(r"[A-Za-z0-9_.+-]+", j.name):
            raise SystemExit(f"job name {j.name!r}: use letters, digits and _ . + - only")
    return Plan(name=d.get("name", Path(path).stem), path=str(path), provider=inst.get("provider", "lambda"),
                types=_list(inst["types"]), max_price_per_hour=float(inst["max_price_per_hour"]),
                max_hours=float(inst["max_hours"]), regions=_list(inst.get("regions", [])),
                min_gpu_mem_gb=float(inst.get("min_gpu_mem_gb", 0)), image=inst.get("image") or None,
                ssh_key=inst.get("ssh_key") or None, ssh_identity=inst.get("ssh_identity") or None,
                sync_dirs=_list(sync.get("dirs", [])), results=_list(sync.get("results", ["data/outputs"])),
                setup=_list(d.get("setup", {}).get("commands", [])), jobs=jobs)


def _list(x):
    return [x] if isinstance(x, str) else list(x)


def job_script(plan: Plan) -> str:
    """Bash driver run on the instance. Setup failures abort; a failed job step skips
    the rest of that job but not the other jobs."""
    q = shlex.quote
    lines = [
        "#!/usr/bin/env bash",
        "set -uo pipefail",
        'cd "$HOME/llm-speaker"',
        "J=.job; mkdir -p $J data/logs",
        'export PATH="$HOME/.local/bin:$PATH" HF_HUB_DISABLE_XET=1 PYTHONUNBUFFERED=1',
        "echo running > $J/status",
        "ts() { date -u +%FT%TZ; }",
        "step() {  # step NAME CMD -> logs to $J/NAME.log, records START/OK/FAIL",
        '  local name=$1; shift',
        '  echo "$(ts) START $name" >> $J/progress',
        '  if bash -c "$1" >> "$J/$name.log" 2>&1; then echo "$(ts) OK $name" >> $J/progress; return 0',
        '  else local rc=$?; echo "$(ts) FAIL $name exit=$rc" >> $J/progress; return $rc; fi',
        "}",
    ]
    for i, cmd in enumerate(plan.setup):
        lines.append(f"step setup-{i} {q(cmd)} || {{ echo failed > $J/status; exit 1; }}")
    for job in plan.jobs:
        steps = [(f"{job.name}.fetch", "python3 asr/fetch_model.py " + " ".join(q(m) for m in job.models))] \
            if job.models else []
        steps += [(f"{job.name}.setup-{i}", c) for i, c in enumerate(job.setup)]
        steps += [(f"{job.name}.run-{i}", c) for i, c in enumerate(job.commands)]
        chain = " && ".join(f"step {q(n)} {q(c)}" for n, c in steps)
        lines.append(f"{{ {chain}; }} || echo \"$(ts) SKIP-REST {job.name}\" >> $J/progress")
    lines.append('grep -q " FAIL " $J/progress && echo done-with-failures > $J/status || echo done > $J/status')
    return "\n".join(lines) + "\n"
