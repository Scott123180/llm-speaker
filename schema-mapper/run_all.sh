#!/bin/sh
set -eu

# Run all mapping steps in order. Execute from anywhere.
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

python3 01_csv_talk_mapper.py
python3 01b_duration_field_normalizer.py
python3 02_audio_information_updater.py
python3 03_transcript_merger.py
python3 04_minify_json.py
python3 05_build_index.py
python3 06_minify_index.py

echo "All steps completed."
