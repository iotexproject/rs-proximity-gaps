#!/usr/bin/env bash
# Driver for extreme adversarial D probe across multiple (p, n_0, k_0, R) configs.
# Records to phase2_extreme_probe.output.txt

set -e
cd "$(dirname "$0")"

OUT=phase2_extreme_probe.output.txt
echo "# Extreme adversarial probe — $(date)" > $OUT
echo "" >> $OUT

# Config list: (p, n0, k0, R)
# Pick primes with n0-th roots of unity. Keep n_R = n0/2^R modest for char-sum budget.
# Total: ~6-8 configs, each ~40 inputs × 100 α × 5 c × 50-200 t.

CONFIGS=(
  "97 16 8 2 100 5"      # n_R=4, very fast
  "97 16 4 2 100 5"      # n_R=4, smaller k_R
  "193 16 8 2 100 5"     # n_R=4, bigger p
  "193 16 4 1 100 5"     # n_R=8, R=1
  "193 32 16 2 100 5"    # n_R=8, R=2 — main config
  "193 32 8 2 100 5"     # n_R=8, k_R=2
  "769 32 16 2 100 5"    # n_R=8, larger p (full t-sweep)
  "257 32 16 2 100 5"    # n_R=8, p=257 (256-th root)
  "257 64 32 2 100 5"    # n_R=16, R=2 — DEPLOYMENT-SCALE
  "257 64 16 2 100 5"    # n_R=16, sparser code
  "769 64 32 3 100 5"    # n_R=8, R=3
  "257 64 16 3 50 3"     # n_R=8, R=3, smaller budget
)

for cfg in "${CONFIGS[@]}"; do
  echo "" >> $OUT
  echo "===========================================================" >> $OUT
  echo "## Config: p=${cfg// /,}" >> $OUT
  echo "===========================================================" >> $OUT
  python3 phase2_extreme_probe.py $cfg >> $OUT 2>&1
  echo "## Done: $cfg ($(date))" >> $OUT
done

echo "" >> $OUT
echo "# All configs done — $(date)" >> $OUT
