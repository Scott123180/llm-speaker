#!/usr/bin/env bash
# Build NVIDIA NeMo-Speech.cpp with the speech-LLM (Nemotron / SALM) runtime.
#   bash cloud/remote/setup_nemo_speech_cpp.sh cuda   # needs the CUDA toolkit (nvcc >= 12.8)
#   bash cloud/remote/setup_nemo_speech_cpp.sh cpu
# Pinned to the commit whose docs the runner (asr/run_nemotron_cpp.py) was written against.
set -euo pipefail
BACKEND=${1:-cuda}
COMMIT=${NEMO_SPEECH_COMMIT:-536b17a41bef62d2a67a40ed3df61df26a4389fe}
cd "$HOME/llm-speaker"
export PATH="$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
mkdir -p data/src && cd data/src
if [ ! -d NeMo-Speech.cpp/.git ]; then
  git clone --filter=blob:none https://github.com/NVIDIA/NeMo-Speech.cpp
fi
cd NeMo-Speech.cpp
git checkout --quiet "$COMMIT"
command -v ninja >/dev/null || uv tool install ninja
if [ "$BACKEND" = cuda ]; then nvcc --version | tail -n 1; fi
# the runner uses `nemo-speech serve`, which only exists with NEMO_SPEECH_BUILD_HTTP=ON
if [ -x "build/$BACKEND-asr/bin/nemo-speech" ] && [ -f "build/$BACKEND-asr/.with-http" ]; then echo "already built"; exit 0; fi
JOBS=$(nproc) bash scripts/build_sentencepiece_static.sh
git submodule update --init --depth 1 llama.cpp third_party/cpp-httplib
bash scripts/configure.sh "$BACKEND-asr" -DNEMO_SPEECH_BUILD_SPEECHLM=ON -DNEMO_SPEECH_BUILD_HTTP=ON
cmake --build --preset "$BACKEND-asr" -j "$(nproc)"
ls -la "build/$BACKEND-asr/bin/nemo-speech"
touch "build/$BACKEND-asr/.with-http"
