"""Provider-agnostic harness for running ASR bake-off jobs on rented GPU servers.

  uv run python -m cloud types                       # what's available now, and prices
  uv run python -m cloud run cloud/plans/smoke.toml  # launch, sync, run, fetch results, terminate
  uv run python -m cloud ls / down ID / ssh ID       # manage instances

See cloud/README.md.
"""
