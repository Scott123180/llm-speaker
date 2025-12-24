#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <input.txt> <output.txt>" >&2
  exit 1
fi

in="$1"
out="$2"

if [[ ! -f "$in" ]]; then
  echo "Error: input file not found: $in" >&2
  exit 1
fi

# Unwrap hard-wrapped transcripts:
# - Treat blank lines as paragraph boundaries (preserve them)
# - Replace single newlines within a paragraph with spaces
# - Collapse repeated spaces/tabs inside lines
awk '
  function rtrim(s) { sub(/[ \t\r]+$/, "", s); return s }
  function ltrim(s) { sub(/^[ \t\r]+/, "", s); return s }
  function trim(s)  { return rtrim(ltrim(s)) }

  BEGIN {
    first_line = 1
    in_para = 0
  }

  # Blank line => paragraph break
  /^[[:space:]]*$/ {
    if (in_para) {
      printf "\n\n"
      in_para = 0
      first_line = 1
    }
    next
  }

  {
    line = $0
    gsub(/\r$/, "", line)            # strip CR if file has Windows line endings
    line = trim(line)
    gsub(/[ \t]+/, " ", line)        # collapse internal whitespace runs

    if (!in_para) {
      printf "%s", line
      in_para = 1
      first_line = 0
    } else {
      printf " %s", line
    }
  }

  END {
    if (in_para) printf "\n"
  }
' "$in" > "$out"
