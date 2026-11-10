#!/usr/bin/env bash
# Run the full ASR bake-off on the gold set and regenerate the report.
# Safe to re-run: each runner skips clips it has already transcribed.
#
#   bash eval/run_bakeoff.sh                 # everything
#   SYSTEMS="whisper parakeet" bash eval/run_bakeoff.sh
#
# Prereqs: uv; gold set prepared (eval/goldset.py select/download/cut);
# contexts built (transcriber/build_context.py); VAD regions (eval/goldset.py vad).
set -uo pipefail
cd "$(dirname "$0")/.."
export HF_HUB_DISABLE_XET=1
SYSTEMS=${SYSTEMS:-"whisper parakeet qwen"}
LOG=data/logs; mkdir -p "$LOG"

fetch() {  # project-dir repo-id  (huggingface_hub transfers stalled here; curl is reliable)
  python3 asr/fetch_model.py "$2" >>"$LOG/downloads.log" 2>&1 || echo "download failed: $2 (see $LOG/downloads.log)"
}

for s in $SYSTEMS; do
  case $s in
    whisper)
      fetch . Systran/faster-whisper-large-v3   # turbo comes from the HF cache
      for m in large-v3-turbo large-v3; do
        uv run python asr/run_whisper.py --model $m           >>"$LOG/whisper.log" 2>&1
        uv run python asr/run_whisper.py --model $m --context >>"$LOG/whisper.log" 2>&1
      done ;;
    parakeet)
      fetch asr/envs/nemo nvidia/parakeet-tdt-0.6b-v3
      R="uv run --project asr/envs/nemo python asr/run_parakeet.py"
      $R              >>"$LOG/parakeet.log" 2>&1
      $R --boost 0.5  >>"$LOG/parakeet.log" 2>&1
      $R --boost 1.0  >>"$LOG/parakeet.log" 2>&1
      $R --boost 0.3 --hard-only >>"$LOG/parakeet.log" 2>&1 ;;
    qwen)
      fetch asr/envs/qwen Qwen/Qwen3-ASR-1.7B
      R="uv run --project asr/envs/qwen python asr/run_qwen.py"
      $R           >>"$LOG/qwen.log" 2>&1
      $R --context >>"$LOG/qwen.log" 2>&1
      $R --vad         >>"$LOG/qwen.log" 2>&1   # gated like faster-whisper
      $R --vad --terms >>"$LOG/qwen.log" 2>&1 ;;
  esac
  grep -hE '^\[' "$LOG"/*.log | tail -n 3
done
uv run python eval/report.py
