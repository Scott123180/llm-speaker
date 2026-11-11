"""Provider interface: the only cloud-specific code. Everything else (sync, jobs,
polling, results, ledger, watchdog) works with any provider that implements this.

To add a provider: subclass Provider, implement the six methods, register it in
providers/__init__.py. Instances must accept SSH as `ssh_user` with a registered key.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

# normalized instance states
PENDING, RUNNING, TERMINATED, ERROR = "pending", "running", "terminated", "error"


@dataclass
class InstanceType:
    name: str                  # provider's id, e.g. gpu_1x_a10
    description: str           # human-readable, e.g. "1x A10 (24 GB PCIe)"
    gpus: int
    gpu_mem_gb: float          # per GPU (0 for CPU-only)
    vcpus: int
    ram_gb: float
    disk_gb: float
    price_per_hour: float      # USD, on-demand
    arch: str = "x86_64"       # x86_64 | arm64
    regions: list[str] = field(default_factory=list)  # regions with capacity right now


@dataclass
class Instance:
    id: str
    name: str
    status: str                # PENDING | RUNNING | TERMINATED | ERROR
    ip: str | None
    type_name: str
    region: str
    price_per_hour: float | None = None


class Provider(ABC):
    name: str = "?"
    ssh_user: str = "ubuntu"

    @abstractmethod
    def instance_types(self) -> list[InstanceType]: ...

    @abstractmethod
    def ssh_keys(self) -> list[tuple[str, str]]:
        """[(key name, public key text)] registered with the provider."""

    @abstractmethod
    def launch(self, type_name: str, region: str, ssh_key: str, name: str, image: str | None = None) -> str:
        """Start one instance; return its id. Must not block until it is running."""

    @abstractmethod
    def get(self, instance_id: str) -> Instance | None: ...

    @abstractmethod
    def list(self) -> list[Instance]: ...

    @abstractmethod
    def terminate(self, instance_ids: list[str]) -> None: ...
