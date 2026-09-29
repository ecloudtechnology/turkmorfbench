#!/usr/bin/env bash
# Butun altin sinamalari kos. Kural motoru degistiyse ONCE burasi kosulur.
set -e
cd "$(dirname "$0")/../kural_motoru"
export PYTHONPATH="$PWD:$PYTHONPATH"
for t in ../sinama/sinama_*.py; do
  echo "--- $(basename "$t")"
  python3 "$t"
done
echo "TUM ALTIN SINAMALAR GECTI"
