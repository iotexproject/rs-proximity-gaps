#!/usr/bin/env bash
# Phase 2 large-n_R extreme probe: test if D > 4 anywhere.
set -e
cd "$(dirname "$0")"

OUT=phase2_extreme_large.output.txt
echo "# Extreme probe — large n_R — $(date)" > $OUT
echo "" >> $OUT

# Need primes p with p-1 divisible by n_0; we want n_R = n_0/2^R large.
# n_R = 32: needs p-1 % 32 == 0
# Choose: p=257 (256-th root), p=193 (96-th root, 32 divides 96), p=769 (full)

CONFIGS=(
  # (p, n_0, k_0, R, num_alphas, num_codewords) → n_R = n_0 / 2^R
  "257 64 32 1 50 3"      # n_R=32
  "769 128 64 2 50 3"     # n_R=32
  "257 128 64 2 50 3"     # n_R=32
  "769 128 32 2 30 3"     # n_R=32, sparser code
  "769 256 128 3 30 3"    # n_R=32, R=3
  "257 128 64 1 30 3"     # n_R=64
  "769 256 128 2 30 3"    # n_R=64
  "769 512 256 3 20 3"    # n_R=64, R=3
  "1153 256 128 1 30 3"   # n_R=128 (1153-1 = 1152 = 128*9)
)

for cfg in "${CONFIGS[@]}"; do
  echo "" >> $OUT
  echo "===========================================================" >> $OUT
  echo "## Config: $cfg" >> $OUT
  echo "===========================================================" >> $OUT
  python3 phase2_extreme_probe.py $cfg >> $OUT 2>&1
  echo "## Done: $cfg ($(date))" >> $OUT
done

echo "" >> $OUT
echo "# All configs done — $(date)" >> $OUT
