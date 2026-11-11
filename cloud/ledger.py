"""Local record of every instance the harness launched (data/cloud/ledger.json):
used for cost reporting and for finding instances that were never terminated."""
from __future__ import annotations

import fcntl
import json
import time
from contextlib import contextmanager

from .ssh import STATE

LEDGER = STATE / "ledger.json"


@contextmanager
def _locked():
    STATE.mkdir(parents=True, exist_ok=True)
    with open(STATE / ".ledger.lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        data = json.loads(LEDGER.read_text()) if LEDGER.exists() else []
        yield data
        LEDGER.write_text(json.dumps(data, indent=1))


def record_launch(provider, instance_id, type_name, region, price, plan, deadline):
    with _locked() as d:
        d.append({"provider": provider, "id": instance_id, "type": type_name, "region": region,
                  "price_per_hour": price, "plan": plan, "launched": time.time(), "deadline": deadline,
                  "terminated": None})


def record_terminated(instance_id, when=None):
    with _locked() as d:
        for e in d:
            if e["id"] == instance_id and not e["terminated"]:
                e["terminated"] = when or time.time()


def entries():
    return json.loads(LEDGER.read_text()) if LEDGER.exists() else []


def cost(e, now=None):
    end = e["terminated"] or now or time.time()
    return (end - e["launched"]) / 3600 * (e["price_per_hour"] or 0)
