# Cloud harness

Runs bake-off jobs on a rented GPU server and brings the results home. The cloud
provider is a plug-in; everything else is generic.

```bash
uv run python -m cloud types                                   # instance types with capacity now, $/h
uv run python -m cloud run cloud/plans/smoke.toml --dry-run    # pick an instance, print the job script
uv run python -m cloud run cloud/plans/smoke.toml              # asks before launching
uv run python -m cloud ls                                      # running instances + money spent
uv run python -m cloud down <id> | --all                       # terminate
uv run python -m cloud ssh <id>                                # shell on an instance
```

`run` does the whole lifecycle:

1. **Choose** the first instance type in the plan's preference list that has capacity,
   costs at most `max_price_per_hour` and has at least `min_gpu_mem_gb` (`--wait-capacity MIN`
   keeps retrying).
2. **Launch** after confirmation (`--yes` skips the prompt). It records the launch in
   `data/cloud/ledger.json` and starts a detached **watchdog** process that terminates the
   instance at `max_hours`, even if the harness or your terminal dies.
3. **Sync** the repo's tracked and untracked-but-not-ignored files, plus the plan's `sync.dirs`
   (gold-set clips, VAD, contexts), with rsync over SSH. Models are not uploaded; the instance
   downloads them from Hugging Face with `asr/fetch_model.py`, which is fast in a datacentre.
4. **Run** a generated bash job script under `nohup`/`setsid`, so an SSH drop doesn't kill it.
   - It runs setup commands, then each job's model fetch, setup and run commands.
   - Every step logs to `~/llm-speaker/.job/<step>.log`.
   - A failed setup step aborts. A failed job step skips the rest of that job only.
5. **Poll** every 30 s and print progress lines. It pulls partial results every 5 minutes.
6. **Pull** `sync.results` (default `data/outputs`) into the same local paths, and the job logs
   into `data/logs/cloud/<plan>-<id>/`.
7. **Terminate**, also on Ctrl-C or errors, unless `--keep`. To re-attach to a kept instance:
   `run PLAN --instance <id>`.

Outputs land in `data/outputs/<system>/` exactly as local runs do, so `eval/report.py`
scores cloud and local systems together.

## Plans

TOML files in `cloud/plans/`. See the docstring in `cloud/plan.py` for every field.

- `smoke.toml`: the cheapest suitable GPU for at most 1 h. Whisper turbo on 4 clips.
  Checks the whole loop for well under $1.
- `a10-bakeoff.toml`: the models that don't fit the home GPU, on a 24 GB A10 (about $1.29/h,
  8 h cap). Runs parakeet-ft-v1 (whole clips), Granite 5.0 2B, VibeVoice-ASR 9B and
  Nemotron-3.5 at 4-bit (IQ4_NL via NeMo-Speech.cpp, built on the instance with CUDA).
  Each runs with and without per-talk terms.

## Providers

`cloud/providers/base.py` defines the interface:
- `instance_types()`
- `ssh_keys()`
- `launch()`
- `get()`
- `list()`
- `terminate()`
- normalized states (`pending`, `running`, `terminated`, `error`)

To add a provider:
1. Implement the interface in `cloud/providers/<name>.py`.
2. Register it in `cloud/providers/__init__.py`.
3. Set `instance.provider` and that provider's type names in a plan.

The instance must run Ubuntu with an NVIDIA driver and accept SSH as `ssh_user`.
`cloud/remote/bootstrap.sh` installs the rest (ffmpeg, uv, the Python envs).

| Provider | Auth | Notes |
|---|---|---|
| `lambda` | `LAMBDA_CLOUD_API_KEY` | Default image `lambda-stack-24-04` (CUDA, Docker). The SSH key is matched to `~/.ssh/*.pub` (or set `instance.ssh_key`). Billing runs until *terminated*. The API allows about 1 request/s and 1 launch per 12 s |

## Safety

- Nothing launches without confirmation or `--yes`. `--dry-run` never launches.
- **Every launch has a hard deadline** (`max_hours`), enforced by the detached watchdog
  (log: `data/logs/cloud/watchdog-<id>.log`).
- The harness terminates in a `finally` block. `ls` shows anything still running and its
  cost so far. `down --all` is the panic button.
- Host keys for short-lived instances go to `data/cloud/known_hosts`, not `~/.ssh/known_hosts`.

## Environment note

`LAMBDA_CLOUD_API_KEY` must be in the environment of the shell that runs the harness.
If it's exported in `~/.bashrc` below the "not running interactively" guard,
non-interactive shells (scripts, cron, agents) won't see it. Move the export above the
guard, or into `~/.profile`.
