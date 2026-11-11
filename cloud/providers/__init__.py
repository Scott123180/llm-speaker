"""Provider registry. Add new providers here (see base.Provider)."""
from .base import ERROR, PENDING, RUNNING, TERMINATED, Instance, InstanceType, Provider  # noqa: F401


def get_provider(name: str) -> Provider:
    if name == "lambda":
        from .lambda_cloud import LambdaCloud
        return LambdaCloud()
    raise SystemExit(f"unknown provider {name!r} (known: lambda)")
