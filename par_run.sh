#!/usr/bin/env bash
set -euo pipefail

# Defaults
N="${N:-13}"
GAMMA="${GAMMA:-6}"
CUBE_VARS="${CUBE_VARS:-5}"
WRITE_DIR="${WRITE_DIR:-qdom_formula}"
QDOM_RUN="${QDOM_RUN:-./qdom_run.sh}"
CORES="${CORES:-1}"

usage() {
  cat <<EOF
Usage:
  $0 [--n N] [--gamma G] [--cube-vars K] [--write-dir DIR] [--cores C]

Environment overrides:
  QDOM_RUN=./qdom_run.sh
  CORES=4
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --n) N="$2"; shift 2 ;;
    --gamma) GAMMA="$2"; shift 2 ;;
    --cube-vars) CUBE_VARS="$2"; shift 2 ;;
    --write-dir) WRITE_DIR="$2"; shift 2 ;;
    --cores) CORES="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

if ! [[ "$CORES" =~ ^[0-9]+$ ]] || [[ "$CORES" -lt 1 ]]; then
  echo "Error: --cores must be a positive integer" >&2
  exit 1
fi

CUBE_FILE="${WRITE_DIR}/cubes_n_${N}_gamma_${GAMMA}_cube_vars_${CUBE_VARS}.txt"

TOTAL_START="$(date +%s)"

echo "Generating formula and cubes..." >&2

GEN_START="$(date +%s)"

"$QDOM_RUN" generate \
  --n "$N" \
  --gamma "$GAMMA" \
  --cube-vars "$CUBE_VARS" \
  --write-dir "$WRITE_DIR"

GEN_END="$(date +%s)"
GEN_SECONDS=$((GEN_END - GEN_START))

[[ -f "$CUBE_FILE" ]] || {
  echo "Cube file not found after generation: $CUBE_FILE" >&2
  exit 1
}

NUM_CUBES="$(wc -l < "$CUBE_FILE")"

echo "Generated cube file: $CUBE_FILE" >&2
echo "Number of cubes: $NUM_CUBES" >&2
echo "Cores: $CORES" >&2
echo "Generation time: ${GEN_SECONDS}s" >&2
echo "Starting parallel solve_and_verify..." >&2

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

run_worker() {
  local worker_id="$1"
  local worker_total=0
  local cube_id
  local cube_start
  local cube_end
  local cube_seconds

  echo "[worker $worker_id] started" >&2

  for ((cube_id = worker_id; cube_id < NUM_CUBES; cube_id += CORES)); do
    echo >&2
    echo "============================================================" >&2
    echo "[worker $worker_id] Cube $cube_id / $((NUM_CUBES - 1))" >&2
    echo "============================================================" >&2

    cube_start="$(date +%s)"

    "$QDOM_RUN" solve_and_verify \
      --n "$N" \
      --gamma "$GAMMA" \
      --cube-vars "$CUBE_VARS" \
      --write-dir "$WRITE_DIR" \
      --cube-id "$cube_id"

    cube_end="$(date +%s)"
    cube_seconds=$((cube_end - cube_start))
    worker_total=$((worker_total + cube_seconds))

    echo "[worker $worker_id] Cube $cube_id finished in ${cube_seconds}s" >&2
  done

  echo "$worker_total" > "$TMP_DIR/worker_${worker_id}.time"
  echo "[worker $worker_id] finished; total worker time: ${worker_total}s" >&2
}

pids=()

SOLVE_START="$(date +%s)"

for ((worker_id = 0; worker_id < CORES; worker_id++)); do
  run_worker "$worker_id" &
  pids+=("$!")
done

FAILED=0

for pid in "${pids[@]}"; do
  if ! wait "$pid"; then
    FAILED=1
  fi
done

SOLVE_END="$(date +%s)"
SOLVE_WALL_SECONDS=$((SOLVE_END - SOLVE_START))

if [[ "$FAILED" -ne 0 ]]; then
  echo "At least one worker failed." >&2
  exit 1
fi

SUM_WORKER_SECONDS=0

echo >&2
echo "============================================================" >&2
echo "Per-worker times" >&2
echo "============================================================" >&2

for ((worker_id = 0; worker_id < CORES; worker_id++)); do
  worker_file="$TMP_DIR/worker_${worker_id}.time"

  if [[ -f "$worker_file" ]]; then
    worker_seconds="$(cat "$worker_file")"
  else
    worker_seconds=0
  fi

  SUM_WORKER_SECONDS=$((SUM_WORKER_SECONDS + worker_seconds))
  echo "Worker $worker_id: ${worker_seconds}s" >&2
done

TOTAL_END="$(date +%s)"
TOTAL_WALL_SECONDS=$((TOTAL_END - TOTAL_START))

echo >&2
echo "============================================================" >&2
echo "All cubes finished." >&2
echo "Generation time: ${GEN_SECONDS}s" >&2
echo "Parallel solve wall time: ${SOLVE_WALL_SECONDS}s" >&2
echo "Sum of worker solve times: ${SUM_WORKER_SECONDS}s" >&2
echo "Estimated sequential total: $((GEN_SECONDS + SUM_WORKER_SECONDS))s" >&2
echo "Actual total wall time: ${TOTAL_WALL_SECONDS}s" >&2
echo "============================================================" >&2
