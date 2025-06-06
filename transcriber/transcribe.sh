#!/bin/bash

#INPUT_DIR="/home/biosdaddy/git/llm-speaker/transcriber/talks"
INPUT_DIR="/media/biosdaddy/WD Red/archives/myotai/audio"
OUTPUT_DIR="./transcriptions"
MODEL="turbo"  # or "medium", "large", etc.
FORMAT="all"
VERBOSE="False"

FILES=("$INPUT_DIR"/*.mp3)
TOTAL=${#FILES[@]}

START_TIME=$(date +%s)

for i in "${!FILES[@]}"; do
    FILE="${FILES[$i]}"
    INDEX=$((i + 1))

    # Timestamp so far
    NOW=$(date +%s)
    ELAPSED=$((NOW - START_TIME))
    ELAPSED_FORMATTED=$(printf '%02dh:%02dm:%02ds\n' $((ELAPSED/3600)) $((ELAPSED%3600/60)) $((ELAPSED%60)))

    echo "🔄 [$INDEX / $TOTAL] Transcribing: $FILE"
    echo "⏱️  Elapsed time: $ELAPSED_FORMATTED"

    whisper "$FILE" --model "$MODEL" --output_format "$FORMAT" --language en --verbose "$VERBOSE" --output_dir "$OUTPUT_DIR"

    echo ""
done

END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))
printf "✅ Done! Total time: %02dh:%02dm:%02ds\n" $((TOTAL_TIME/3600)) $((TOTAL_TIME%3600/60)) $((TOTAL_TIME%60))
