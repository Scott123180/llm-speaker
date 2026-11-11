"""SSH/rsync transport (provider-agnostic). Uses the system ssh client, so the user's
own keys, agent and ~/.ssh/config apply. Host keys for short-lived instances go to a
separate known_hosts (data/cloud/known_hosts): cloud IPs get reused, and entries for
dead instances must not poison ~/.ssh/known_hosts.
"""
from __future__ import annotations

import shlex
import subprocess
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATE = REPO / "data" / "cloud"
REMOTE_DIR = "llm-speaker"  # relative to the remote user's home


class Remote:
    def __init__(self, host: str, user: str, identity: str | None = None):
        self.host, self.user, self.identity = host, user, identity
        STATE.mkdir(parents=True, exist_ok=True)
        self.opts = ["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new",
                     "-o", f"UserKnownHostsFile={STATE / 'known_hosts'}", "-o", "ConnectTimeout=15",
                     "-o", "ServerAliveInterval=30", "-o", "ServerAliveCountMax=6"]
        if identity:
            self.opts += ["-i", str(Path(identity).expanduser())]

    @property
    def target(self):
        return f"{self.user}@{self.host}"

    def ssh_cmd(self, command: str | None = None, tty=False):
        return ["ssh", *(["-t"] if tty else []), *self.opts, self.target, *([command] if command else [])]

    def run(self, command: str, check=True, capture=True, timeout=None) -> subprocess.CompletedProcess:
        return subprocess.run(self.ssh_cmd(command), check=check, text=True, timeout=timeout,
                              capture_output=capture)

    def wait_ready(self, timeout=900):
        """Wait until SSH accepts our key (boot + cloud-init can take a few minutes)."""
        t0 = time.time()
        while time.time() - t0 < timeout:
            r = subprocess.run(self.ssh_cmd("true"), capture_output=True, text=True)
            if r.returncode == 0:
                return
            time.sleep(10)
        raise TimeoutError(f"ssh to {self.target} not ready after {timeout}s")

    def _rsh(self):
        return "ssh " + " ".join(shlex.quote(o) for o in self.opts)

    def push_files(self, rel_paths: list[str]):
        """Copy repo-relative files (keeping their paths) into ~/llm-speaker."""
        data = "\0".join(rel_paths).encode()
        subprocess.run(["rsync", "-az", "--from0", f"--files-from=-", "-e", self._rsh(), "./",
                        f"{self.target}:{REMOTE_DIR}/"], input=data, check=True, cwd=REPO)

    def push_dirs(self, rel_dirs: list[str]):
        dirs = [d for d in rel_dirs if (REPO / d).exists()]
        if dirs:
            subprocess.run(["rsync", "-azR", "-e", self._rsh(), *dirs, f"{self.target}:{REMOTE_DIR}/"],
                           check=True, cwd=REPO)

    def pull(self, remote_rel: str, local: Path, check=False):
        """Copy ~/llm-speaker/{remote_rel}/ into local/ (merging; never deletes local files)."""
        local.mkdir(parents=True, exist_ok=True)
        return subprocess.run(["rsync", "-az", "-e", self._rsh(), f"{self.target}:{REMOTE_DIR}/{remote_rel}/",
                               f"{local}/"], check=check, capture_output=True, text=True)


def forget_host(ip: str):
    kh = STATE / "known_hosts"
    if kh.exists() and ip:
        subprocess.run(["ssh-keygen", "-R", ip, "-f", str(kh)], capture_output=True)
