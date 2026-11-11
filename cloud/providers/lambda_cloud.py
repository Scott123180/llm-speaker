"""Lambda Cloud (https://cloud.lambda.ai/api/v1, OpenAPI 1.10). Auth: LAMBDA_CLOUD_API_KEY.

Rate limits: about 1 request/s, and 1 launch per 12 s. Billing runs until an
instance is *terminated* (shutting the OS down does not stop it).
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request

from .base import ERROR, PENDING, RUNNING, TERMINATED, Instance, InstanceType, Provider

API = "https://cloud.lambda.ai/api/v1"
STATUS = {"booting": PENDING, "active": RUNNING, "unhealthy": ERROR,
          "terminating": TERMINATED, "terminated": TERMINATED, "preempted": TERMINATED}


class LambdaCloud(Provider):
    name = "lambda"
    ssh_user = "ubuntu"
    default_image = "lambda-stack-24-04"

    def __init__(self, api_key: str | None = None):
        self.key = api_key or os.environ.get("LAMBDA_CLOUD_API_KEY")
        if not self.key:
            raise SystemExit("LAMBDA_CLOUD_API_KEY is not set in this environment")
        self._last = 0.0
        self._types: dict[str, InstanceType] | None = None

    def _call(self, method, path, body=None):
        wait = 1.05 - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(API + path, method=method,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Authorization": f"Bearer {self.key}",
                                              "Content-Type": "application/json",
                                              # the API's edge rejects Python-urllib's default agent (403)
                                              "User-Agent": "llm-speaker-cloud/0.1"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                self._last = time.time()
                return json.load(r).get("data")
        except urllib.error.HTTPError as e:
            self._last = time.time()
            try:
                err = json.load(e).get("error", {})
            except Exception:
                err = {}
            raise RuntimeError(f"Lambda API {method} {path}: HTTP {e.code} {err.get('code', '')} "
                               f"{err.get('message', '')} {err.get('suggestion', '')}".strip()) from None

    def instance_types(self):
        out = []
        for v in self._call("GET", "/instance-types").values():
            it, specs = v["instance_type"], v["instance_type"]["specs"]
            m = re.search(r"(\d+)\s*GB", it.get("gpu_description") or "")
            out.append(InstanceType(
                name=it["name"], description=it["description"], gpus=specs.get("gpus", 0),
                gpu_mem_gb=float(m.group(1)) if m and specs.get("gpus") else 0.0,
                vcpus=specs["vcpus"], ram_gb=specs["memory_gib"], disk_gb=specs["storage_gib"],
                price_per_hour=it["price_cents_per_hour"] / 100, arch=it.get("architecture", "x86_64"),
                regions=[r["name"] for r in v["regions_with_capacity_available"]]))
        self._types = {t.name: t for t in out}
        return sorted(out, key=lambda t: t.price_per_hour)

    def ssh_keys(self):
        return [(k["name"], k["public_key"]) for k in self._call("GET", "/ssh-keys")]

    def launch(self, type_name, region, ssh_key, name, image=None):
        body = {"region_name": region, "instance_type_name": type_name, "ssh_key_names": [ssh_key],
                "name": name[:64], "image": {"family": image or self.default_image}}
        wait = 12.5 - (time.time() - self._last)  # launch endpoint: 1 per 12 s
        if wait > 0:
            time.sleep(wait)
        return self._call("POST", "/instance-operations/launch", body)["instance_ids"][0]

    def _inst(self, d):
        it = d.get("instance_type") or {}
        return Instance(id=d["id"], name=d.get("name") or "", status=STATUS.get(d.get("status"), ERROR),
                        ip=d.get("ip"), type_name=it.get("name", "?"), region=(d.get("region") or {}).get("name", "?"),
                        price_per_hour=(it.get("price_cents_per_hour") or 0) / 100 or None)

    def get(self, instance_id):
        try:
            return self._inst(self._call("GET", f"/instances/{instance_id}"))
        except RuntimeError as e:
            if "404" in str(e) or "not-found" in str(e):
                return None
            raise

    def list(self):
        return [self._inst(d) for d in self._call("GET", "/instances")]

    def terminate(self, instance_ids):
        if instance_ids:
            self._call("POST", "/instance-operations/terminate", {"instance_ids": list(instance_ids)})
