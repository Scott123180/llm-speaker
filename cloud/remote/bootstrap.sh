#!/usr/bin/env bash
# Runs on a fresh instance (Ubuntu + NVIDIA driver; any provider). Idempotent.
# Installs ffmpeg and uv, reports the GPU, and syncs the main env (faster-whisper, eval).
set -euo pipefail
cd "$HOME/llm-speaker"

if ! command -v ffmpeg >/dev/null; then
  sudo DEBIAN_FRONTEND=noninteractive apt-get -o DPkg::Lock::Timeout=600 update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get -o DPkg::Lock::Timeout=600 install -y -qq ffmpeg rsync
fi
if ! command -v uv >/dev/null && [ ! -x "$HOME/.local/bin/uv" ]; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"

echo "== host"; uname -m; nproc; free -g | head -n 2; df -h "$HOME" | tail -n 1
echo "== gpu"; nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv || echo "no NVIDIA GPU"
echo "== cuda toolkit"; (command -v nvcc && nvcc --version | tail -n 1) || ls -d /usr/local/cuda* 2>/dev/null || echo "no nvcc"

uv sync --frozen
mkdir -p data/logs data/models
echo "bootstrap ok"
