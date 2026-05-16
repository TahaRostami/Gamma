#!/usr/bin/env bash
set -euo pipefail

# Defaults
N="${N:-13}"
GAMMA="${GAMMA:-6}"
CUBE_VARS="${CUBE_VARS:-5}"
WRITE_DIR="${WRITE_DIR:-qdom_formula}"
QDOM_RUN="${QDOM_RUN:-./qdom_run.sh}"

usage() {
  cat <<EOF
Usage:
  $0 [--n N] [--gamma G] [--cube-vars K] [--write-dir DIR]

Environment overrides:
  QDOM_RUN=./qdom_run.sh
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --n) N="$2"; shift 2 ;;
    --gamma) GAMMA="$2"; shift 2 ;;
    --cube-vars) CUBE_VARS="$2"; shift 2 ;;
    --write-dir) WRITE_DIR="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

CUBE_FILE="${WRITE_DIR}/cubes_n_${N}_gamma_${GAMMA}_cube_vars_${CUBE_VARS}.txt"

START_TIME="$(date +%s)"

echo "Generating formula and cubes..." >&2

"$QDOM_RUN" generate \
  --n "$N" \
  --gamma "$GAMMA" \
  --cube-vars "$CUBE_VARS" \
  --write-dir "$WRITE_DIR"

[[ -f "$CUBE_FILE" ]] || {
  echo "Cube file not found after generation: $CUBE_FILE" >&2
  exit 1
}

NUM_CUBES="$(wc -l < "$CUBE_FILE")"

echo "Generated cube file: $CUBE_FILE" >&2
echo "Number of cubes: $NUM_CUBES" >&2
echo "Starting sequential solve_and_verify..." >&2

for ((cube_id = 0; cube_id < NUM_CUBES; cube_id++)); do
  echo >&2
  echo "============================================================" >&2
  echo "Cube $cube_id / $((NUM_CUBES - 1))" >&2
  echo "============================================================" >&2

  CUBE_START="$(date +%s)"

  "$QDOM_RUN" solve_and_verify \
    --n "$N" \
    --gamma "$GAMMA" \
    --cube-vars "$CUBE_VARS" \
    --write-dir "$WRITE_DIR" \
    --cube-id "$cube_id"

  CUBE_END="$(date +%s)"
  CUBE_SECONDS=$((CUBE_END - CUBE_START))

  echo "Cube $cube_id finished in ${CUBE_SECONDS}s" >&2
done

END_TIME="$(date +%s)"
TOTAL_SECONDS=$((END_TIME - START_TIME))

echo >&2
echo "============================================================" >&2
echo "All cubes finished." >&2
echo "Total time: ${TOTAL_SECONDS}s" >&2
echo "============================================================" >&2
