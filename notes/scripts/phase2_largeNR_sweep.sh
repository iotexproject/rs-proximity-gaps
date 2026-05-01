#!/bin/bash
# Phase 2 LARGE n_R sweep: confirm √n_R scaling at n_R = 32, 64, 128.
# Uses p with sufficient roots of unity (p ≡ 1 mod n_0).
set -e
cd "$(dirname "$0")"
OUT=phase2_largeNR.output.txt
> $OUT

echo "=== Sweep F: large n_R scaling ===" | tee -a $OUT
# (p, n0, k0, R, num_inputs, num_alphas, num_codewords)
# p must have n0-th root: p ≡ 1 mod n0.
# 257 = 1 + 256 → ω_256 exists, all subgroups up to 256 OK.
# 769 = 1 + 768 → ω_256 exists (768 = 256·3), all up to 256 OK.
# 1153 = 1 + 1152 (1152 = 128·9) → ω_128 exists.

for params in \
  "257 128 64 2 3 100 30" \
  "257 256 128 2 2 50 20" \
  "769 256 128 2 2 50 20" \
  "257 128 64 1 3 100 30" \
  "257 256 128 1 2 50 20"; do
  echo "--- params: $params ---" | tee -a $OUT
  python3 phase2_charsum_sweep.py $params random agree 2>&1 | tee -a $OUT
  echo "" | tee -a $OUT
done

echo "=== Sweep G: direct character sum |S(t,α,c)| ===" | tee -a $OUT
# Small primes for full t-range
for params in "17 16 8 2 2 20" "97 16 8 2 2 20" "97 32 16 2 2 10" "193 64 32 2 1 5"; do
  echo "--- params: $params ---" | tee -a $OUT
  python3 phase2_charsum_sweep.py $params 1 random charsum 2>&1 | tee -a $OUT
  echo "" | tee -a $OUT
done

echo "=== DONE ===" | tee -a $OUT
