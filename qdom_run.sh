#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-}"

# Defaults
N="${N:-13}"
GAMMA="${GAMMA:-6}"
CUBE_VARS="${CUBE_VARS:-5}"
WRITE_DIR="${WRITE_DIR:-qdom_formula}"
PYTHON="${PYTHON:-python}"
QDOM="${QDOM:-Qdom.py}"
CUBE_ID="${CUBE_ID:-0}"

CADICAL_EXHAUST="${CADICAL_EXHAUST:-./cadical-exhaust}"
DRAT_TRIM="${DRAT_TRIM:-./drat-trim-t}"
SOL_DIR="${SOL_DIR:-solutions}"

usage() {
  cat <<EOF
Usage:
  $0 generate         [--n N] [--gamma G] [--cube-vars K] [--write-dir DIR]
  $0 solve            [--n N] [--gamma G] [--cube-vars K] [--write-dir DIR] [--cube-id ID]
  $0 solve_and_verify [--n N] [--gamma G] [--cube-vars K] [--write-dir DIR] [--cube-id ID]

Environment overrides:
  PYTHON=python3
  QDOM=Qdom.py
  CADICAL_EXHAUST=./cadical-exhaust
  DRAT_TRIM=./drat-trim-t
  SOL_DIR=solutions
EOF
}

shift || true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --n) N="$2"; shift 2 ;;
    --gamma) GAMMA="$2"; shift 2 ;;
    --cube-vars) CUBE_VARS="$2"; shift 2 ;;
    --write-dir) WRITE_DIR="$2"; shift 2 ;;
    --cube-id) CUBE_ID="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 1 ;;
  esac
done

CNF_FILE="${WRITE_DIR}/${N}_${GAMMA}_HILBERTCURVE_mtotalizer_sym_square_cubing.cnf"
CUBE_FILE="${WRITE_DIR}/cubes_n_${N}_gamma_${GAMMA}_cube_vars_${CUBE_VARS}.txt"

case "$MODE" in
  generate)
    mkdir -p "$WRITE_DIR"

    "$PYTHON" "$QDOM" \
      --sym_break \
      --write_cnf \
      --write_dir "$WRITE_DIR/" \
      --make_cubes \
      --cube_file "$CUBE_FILE" \
      --n "$N" \
      --gamma "$GAMMA" \
      --cube_vars "$CUBE_VARS"
    ;;

  solve|solve_and_verify)
    [[ -f "$CNF_FILE" ]] || { echo "CNF not found: $CNF_FILE" >&2; exit 1; }
    [[ -f "$CUBE_FILE" ]] || { echo "Cube file not found: $CUBE_FILE" >&2; exit 1; }

    CUBE_LINE="$(sed -n "$((CUBE_ID + 1))p" "$CUBE_FILE")"

    [[ -n "$CUBE_LINE" ]] || {
      echo "Cube ID $CUBE_ID not found in $CUBE_FILE" >&2
      exit 1
    }

    read -ra TOKENS <<< "$CUBE_LINE"

    LITS=()
    for tok in "${TOKENS[@]}"; do
      [[ "$tok" == "a" ]] && continue
      [[ "$tok" == "0" ]] && continue
      LITS+=("$tok")
    done

    TMP_CNF="$(mktemp --suffix=".cnf")"
    TMP_PROOF=""

    cleanup() {
      rm -f "$TMP_CNF"
      [[ -n "$TMP_PROOF" ]] && rm -f "$TMP_PROOF"
    }
    trap cleanup EXIT

    HEADER_DONE=0

    while IFS= read -r line; do
      if [[ "$HEADER_DONE" -eq 0 && "$line" =~ ^p[[:space:]]+cnf[[:space:]]+([0-9]+)[[:space:]]+([0-9]+) ]]; then
        VARS="${BASH_REMATCH[1]}"
        CLAUSES="${BASH_REMATCH[2]}"
        NEW_CLAUSES=$((CLAUSES + ${#LITS[@]}))
        echo "p cnf $VARS $NEW_CLAUSES" >> "$TMP_CNF"
        HEADER_DONE=1
      else
        echo "$line" >> "$TMP_CNF"
      fi
    done < "$CNF_FILE"

    for lit in "${LITS[@]}"; do
      echo "$lit 0" >> "$TMP_CNF"
    done

    mkdir -p "$SOL_DIR"

    SOL_FILE="${SOL_DIR}/solutions_${N}_${GAMMA}_${CUBE_ID}.txt"
    ORDER=$((N * N))

    echo "Solving cube_id=$CUBE_ID with ${#LITS[@]} assumptions as unit clauses" >&2
    echo "Writing solutions to: $SOL_FILE" >&2

    if [[ "$MODE" == "solve_and_verify" ]]; then
      TMP_PROOF="$(mktemp --suffix=".drat")"

      echo "Writing temporary proof to: $TMP_PROOF" >&2

      set +e
      "$CADICAL_EXHAUST" "$TMP_CNF" "$TMP_PROOF" \
        --order "$ORDER" \
        --only-neg \
        --solfile "$SOL_FILE"
      CADICAL_STATUS=$?
      set -e

      echo "cadical-exhaust exit code: $CADICAL_STATUS" >&2

      if [[ "$CADICAL_STATUS" -ne 20 ]]; then
        echo "Expected UNSAT exit code 20 before proof verification, got $CADICAL_STATUS" >&2
        exit "$CADICAL_STATUS"
      fi

      echo "Verifying proof with drat-trim-t..." >&2

      set +e
      "$DRAT_TRIM" "$TMP_CNF" "$TMP_PROOF"
      DRAT_STATUS=$?
      set -e

      echo "drat-trim-t exit code: $DRAT_STATUS" >&2

      if [[ "$DRAT_STATUS" -ne 0 ]]; then
        echo "Proof verification failed." >&2
        exit "$DRAT_STATUS"
      fi

      echo "Proof verification succeeded." >&2

    else
      "$CADICAL_EXHAUST" "$TMP_CNF" \
        --order "$ORDER" \
        --only-neg \
        --solfile "$SOL_FILE"
    fi
    ;;

  *)
    usage
    exit 1
    ;;
esac