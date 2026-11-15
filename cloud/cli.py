"""Command line for the cloud harness. See cloud/README.md."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from . import ledger
from .plan import job_script, load
from .providers import ERROR, RUNNING, TERMINATED, get_provider
from .ssh import REPO, STATE, Remote, forget_host

LOGS = REPO / "data" / "logs" / "cloud"


def log(msg):
    print(time.strftime("%H:%M:%S ") + msg, flush=True)


def confirm(msg, yes):
    if yes:
        return True
    if not sys.stdin.isatty():
        raise SystemExit(msg + "\nrefusing without --yes (not a terminal)")
    return input(msg + " [y/N] ").strip().lower() in ("y", "yes")


# ---------------------------------------------------------------- selection

def choose_type(provider, plan, wait_min=0, poll_sec=120):
    t_end = time.time() + wait_min * 60
    last_log = 0.0
    while True:
        try:
            types = {t.name: t for t in provider.instance_types()}
        except Exception as e:  # a transient API or network error shouldn't end a long wait
            if not wait_min or time.time() >= t_end:
                raise
            log(f"  capacity check failed ({e}); retrying in {poll_sec:g} s")
            time.sleep(poll_sec)
            continue
        for name in plan.types:
            t = types.get(name)
            if not t:
                log(f"  {name}: unknown on {provider.name}")
                continue
            if t.price_per_hour > plan.max_price_per_hour or t.gpu_mem_gb < plan.min_gpu_mem_gb:
                continue
            regions = [r for r in t.regions if not plan.regions or r in plan.regions]
            if regions:
                return t, regions[0]
        if time.time() >= t_end:
            avail = [f"{t.name} (${t.price_per_hour:.2f})" for t in types.values() if t.regions]
            raise SystemExit(f"no capacity for {plan.types} within ${plan.max_price_per_hour}/h. "
                             f"Available now: {', '.join(avail) or 'none'}. Use --wait-capacity MIN to keep trying.")
        if time.time() - last_log >= 600:  # log every 10 min, however often it checks
            log(f"  no capacity yet for {plan.types}; checking every {poll_sec:g} s")
            last_log = time.time()
        time.sleep(poll_sec)


def choose_key(provider, wanted):
    keys = provider.ssh_keys()
    if wanted:
        if wanted not in [k for k, _ in keys]:
            raise SystemExit(f"ssh key {wanted!r} not registered with {provider.name}: {[k for k, _ in keys]}")
        return wanted
    local = {" ".join(p.read_text().split()[:2]) for p in Path("~/.ssh").expanduser().glob("*.pub")}
    match = [k for k, pub in keys if " ".join(pub.split()[:2]) in local]
    if match:
        return match[0]
    raise SystemExit(f"none of the keys registered with {provider.name} ({[k for k, _ in keys]}) matches "
                     "~/.ssh/*.pub; set instance.ssh_key in the plan")


# ---------------------------------------------------------------- lifecycle

def launch(provider, type_name, region, name, hours, image, key, plan_name):
    iid = provider.launch(type_name, region, key, name, image)
    price = next((t.price_per_hour for t in provider.instance_types() if t.name == type_name), None)
    deadline = time.time() + hours * 3600
    ledger.record_launch(provider.name, iid, type_name, region, price, plan_name, deadline)
    try:
        start_watchdog(provider.name, iid, deadline)
    except Exception:
        terminate(provider, iid)
        raise
    log(f"launched {iid} ({type_name}, {region}, ${price}/h); watchdog terminates it at "
        f"{time.strftime('%H:%M', time.localtime(deadline))}")
    return iid


def start_watchdog(provider_name, iid, deadline):
    """Detached process that terminates the instance at the deadline even if this one dies.
    Verified alive before returning: a launch without a working watchdog is not allowed."""
    LOGS.mkdir(parents=True, exist_ok=True)
    wlog = open(LOGS / f"watchdog-{iid}.log", "a")
    w = subprocess.Popen([sys.executable, "-m", "cloud", "--provider", provider_name, "watchdog", "--id", iid,
                          "--deadline", str(int(deadline))], cwd=REPO, stdout=wlog, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, start_new_session=True)
    time.sleep(3)
    if w.poll() not in (None, 0):  # 0 = instance already gone (fine); anything else = broken watchdog
        raise RuntimeError(f"watchdog exited immediately (code {w.returncode}); "
                           f"see {LOGS / f'watchdog-{iid}.log'}")
    return w


def wait_running(provider, iid, timeout=1800):
    t0 = time.time()
    while time.time() - t0 < timeout:
        inst = provider.get(iid)
        if inst and inst.status == RUNNING and inst.ip:
            return inst
        if inst is None or inst.status in (TERMINATED, ERROR):
            raise RuntimeError(f"instance {iid} is {inst.status if inst else 'gone'}")
        time.sleep(15)
    raise TimeoutError(f"instance {iid} not running after {timeout}s")


def terminate(provider, iid, ip=None):
    provider.terminate([iid])
    ledger.record_terminated(iid)
    forget_host(ip)
    e = next((e for e in ledger.entries() if e["id"] == iid), None)
    log(f"terminated {iid}" + (f" (about ${ledger.cost(e):.2f})" if e else ""))


def repo_files():
    out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                         cwd=REPO, capture_output=True, check=True).stdout.decode()
    return [f for f in out.split("\0") if f and (REPO / f).is_file()]


def pull_results(remote, plan, run_dir):
    for rel in plan.results:
        remote.pull(rel, REPO / rel)
    remote.pull(".job", run_dir)


def poll(remote, plan, run_dir, deadline):
    seen, last_pull = 0, time.time()
    while True:
        try:
            r = remote.run(f"cd llm-speaker && cat .job/status 2>/dev/null; echo ---; "
                           f"tail -n +{seen + 1} .job/progress 2>/dev/null", check=False, timeout=60)
            status, _, prog = r.stdout.partition("---\n")
            status = status.strip()
            for line in prog.splitlines():
                log("  remote: " + line)
                seen += 1
        except subprocess.TimeoutExpired:
            status = "?"
        if status in ("done", "done-with-failures", "failed"):
            return status
        if time.time() - last_pull > 300:
            pull_results(remote, plan, run_dir)
            last_pull = time.time()
        if time.time() > deadline - 300:
            log("deadline in under 5 min: stopping to collect results")
            return "deadline"
        time.sleep(30)


def cmd_run(a):
    plan = load(a.plan)
    provider = get_provider(plan.provider)
    script = job_script(plan)
    if a.instance:
        inst = provider.get(a.instance)
        if not inst or inst.status != RUNNING:
            raise SystemExit(f"instance {a.instance} is not running")
        iid, t = inst.id, None
        e = next((e for e in ledger.entries() if e["id"] == iid), None)
        deadline = e["deadline"] if e else time.time() + plan.max_hours * 3600
    else:
        t, region = choose_type(provider, plan, a.wait_capacity, a.poll_sec)
        key = choose_key(provider, plan.ssh_key)
        log(f"plan {plan.name}: {t.name} ({t.description}, {t.vcpus} vCPU, {t.ram_gb:g} GiB RAM, "
            f"{t.disk_gb:g} GiB disk, {t.arch}) in {region} at ${t.price_per_hour:.2f}/h; ssh key {key}")
        log(f"  jobs: {', '.join(j.name for j in plan.jobs)}; hard limit {plan.max_hours:g} h "
            f"(at most ${plan.max_hours * t.price_per_hour:.2f})")
        if a.dry_run:
            print("\n# job script that would run on the instance:\n" + script)
            return
        if not confirm(f"Launch {t.name} at ${t.price_per_hour:.2f}/h?", a.yes):
            return
        iid = launch(provider, t.name, region, f"llm-speaker-{plan.name}", plan.max_hours, plan.image, key,
                     plan.name)
        deadline = time.time() + plan.max_hours * 3600
    run_dir = LOGS / f"{plan.name}-{iid[:8]}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "job.sh").write_text(script)
    inst, remote, status = None, None, "error"
    try:
        inst = wait_running(provider, iid)
        log(f"running at {inst.ip}; waiting for ssh")
        remote = Remote(inst.ip, provider.ssh_user, plan.ssh_identity)
        remote.wait_ready()
        started = remote.run("test -f llm-speaker/.job/status && cat llm-speaker/.job/status", check=False)
        if started.returncode == 0 and started.stdout.strip() == "running":
            log("job already running on this instance; attaching")
        else:
            files = repo_files()
            log(f"syncing {len(files)} repo files + {plan.sync_dirs}")
            remote.push_files(files)
            remote.push_dirs(plan.sync_dirs)
            subprocess.run(remote.ssh_cmd("rm -rf llm-speaker/.job && mkdir -p llm-speaker/.job && "
                                          "cat > llm-speaker/.job/job.sh"), input=script, text=True, check=True)
            remote.run("cd llm-speaker && nohup setsid bash .job/job.sh > .job/driver.log 2>&1 < /dev/null &")
            log("job started; polling every 30 s (Ctrl-C to stop, which also terminates unless --keep)")
        status = poll(remote, plan, run_dir, deadline)
        log(f"job finished: {status}")
    except KeyboardInterrupt:
        log("interrupted")
    except Exception as ex:  # keep going to cleanup
        log(f"error: {ex}")
    finally:
        if remote:
            log("pulling results")
            pull_results(remote, plan, run_dir)
            log(f"results in {', '.join(plan.results)}; job logs in {run_dir.relative_to(REPO)}")
        if a.keep:
            log(f"--keep: instance {iid} left running (watchdog still enforces the deadline). "
                f"Terminate with: uv run python -m cloud down {iid}")
        else:
            terminate(provider, iid, inst.ip if inst else None)
    if status not in ("done",):
        sys.exit(1)


# ---------------------------------------------------------------- other commands

def cmd_types(a):
    p = get_provider(a.provider)
    print(f"{'type':26s} {'$/h':>6s} {'GPU':>10s} {'vCPU':>5s} {'RAM GiB':>8s} {'disk GiB':>9s} arch    capacity")
    for t in p.instance_types():
        if not a.all and not t.regions:
            continue
        gpu = f"{t.gpus}x{t.gpu_mem_gb:g}GB" if t.gpus else "-"
        print(f"{t.name:26s} {t.price_per_hour:6.2f} {gpu:>10s} {t.vcpus:5d} {t.ram_gb:8g} {t.disk_gb:9g} "
              f"{t.arch:7s} {', '.join(t.regions) or '-'}")


def cmd_ls(a):
    p = get_provider(a.provider)
    live = [i for i in p.list() if i.status != TERMINATED]
    print("instances on provider:" if live else "no live instances on provider")
    for i in live:
        e = next((e for e in ledger.entries() if e["id"] == i.id), None)
        extra = (f" ${ledger.cost(e):.2f} so far, deadline {time.strftime('%H:%M', time.localtime(e['deadline']))}"
                 if e else " (not launched by this harness)")
        print(f"  {i.id} {i.name} {i.type_name} {i.region} {i.status} {i.ip or '-'}{extra}")
    total = sum(ledger.cost(e) for e in ledger.entries())
    print(f"ledger: {len(ledger.entries())} launches, about ${total:.2f} total")


def cmd_down(a):
    p = get_provider(a.provider)
    ids = [i.id for i in p.list() if i.status != TERMINATED] if a.all else a.ids
    if not ids:
        print("nothing to terminate")
        return
    if confirm(f"Terminate {ids}?", a.yes):
        for iid in ids:
            inst = p.get(iid)
            terminate(p, iid, inst.ip if inst else None)


def cmd_ssh(a):
    p = get_provider(a.provider)
    inst = p.get(a.id)
    if not inst or not inst.ip:
        raise SystemExit("instance not found or has no IP")
    os.execvp("ssh", Remote(inst.ip, p.ssh_user).ssh_cmd(tty=True))


def cmd_watchdog(a):
    p = get_provider(a.provider)
    log(f"watchdog for {a.id}, deadline {time.strftime('%F %H:%M', time.localtime(a.deadline))}")
    while True:
        try:
            inst = p.get(a.id)
        except Exception as ex:
            log(f"api error: {ex}")
            inst = "?"
        if inst is None or (inst != "?" and inst.status == TERMINATED):
            ledger.record_terminated(a.id)
            log("instance gone; exiting")
            return
        if time.time() >= a.deadline:
            log("deadline reached; terminating")
            try:
                terminate(p, a.id, inst.ip if inst != "?" else None)
                return
            except Exception as ex:
                log(f"terminate failed ({ex}); retrying in 60 s")
        time.sleep(max(10, min(60, a.deadline - time.time())))


def main():
    ap = argparse.ArgumentParser(prog="python -m cloud", description=__doc__)
    ap.add_argument("--provider", default="lambda")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("types", help="instance types with capacity now (--all for every type)")
    s.add_argument("--all", action="store_true")
    s.set_defaults(fn=cmd_types)
    s = sub.add_parser("ls", help="running instances and ledger cost")
    s.set_defaults(fn=cmd_ls)
    s = sub.add_parser("run", help="launch (or attach), sync, run a plan, fetch results, terminate")
    s.add_argument("plan")
    s.add_argument("--dry-run", action="store_true", help="choose the instance and print the job script only")
    s.add_argument("--yes", action="store_true", help="launch without asking")
    s.add_argument("--keep", action="store_true", help="leave the instance running afterwards")
    s.add_argument("--instance", help="use this running instance instead of launching one")
    s.add_argument("--wait-capacity", type=float, default=0, metavar="MIN",
                   help="keep checking for capacity for up to MIN minutes")
    s.add_argument("--poll-sec", type=float, default=120, help="seconds between capacity checks (default 120)")
    s.set_defaults(fn=cmd_run)
    s = sub.add_parser("down", help="terminate instances")
    s.add_argument("ids", nargs="*")
    s.add_argument("--all", action="store_true")
    s.add_argument("--yes", action="store_true")
    s.set_defaults(fn=cmd_down)
    s = sub.add_parser("ssh", help="open a shell on an instance")
    s.add_argument("id")
    s.set_defaults(fn=cmd_ssh)
    s = sub.add_parser("watchdog", help=argparse.SUPPRESS)
    s.add_argument("--id", required=True)
    s.add_argument("--deadline", type=float, required=True)
    s.set_defaults(fn=cmd_watchdog)
    a = ap.parse_args()
    STATE.mkdir(parents=True, exist_ok=True)
    a.fn(a)
