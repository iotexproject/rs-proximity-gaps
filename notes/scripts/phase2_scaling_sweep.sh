#!/bin/bash
# Phase 2 scaling sweep: vary n_R, observe |dev| / √n_R constant.
set -e
cd "$(dirname "$0")"
OUT=phase2_scaling.output.txt
> $OUT

echo "=== Sweep A: n_R scaling (R=2 fixed) ===" | tee -a $OUT
for params in "97 16 8 2 5 100 50" "97 32 16 2 5 100 50" "193 64 32 2 3 100 30" "193 128 64 2 2 50 20"; do
  echo "--- params: $params ---" | tee -a $OUT
  python3 phase2_charsum_sweep.py $params random agree 2>&1 | tee -a $OUT
  echo "" | tee -a $OUT
done

echo "=== Sweep B: R scaling (n_R ≈ 16) ===" | tee -a $OUT
for params in "193 64 32 2 5 200 50" "257 128 64 3 3 200 30"; do
  echo "--- params: $params ---" | tee -a $OUT
  python3 phase2_charsum_sweep.py $params random agree 2>&1 | tee -a $OUT
  echo "" | tee -a $OUT
done

echo "=== Sweep C: direct character sum (small n) ===" | tee -a $OUT
for params in "29 8 4 2 5 30" "29 16 8 2 5 30" "29 32 16 2 3 20"; do
  echo "--- params: $params ---" | tee -a $OUT
  python3 phase2_charsum_sweep.py $params 1 random charsum 2>&1 | tee -a $OUT
  echo "" | tee -a $OUT
done

echo "=== Sweep D: monomial inputs (CS-style) ===" | tee -a $OUT
for params in "97 16 8 2 5 100 50 monomial" "193 64 32 2 3 100 30 monomial"; do
  echo "--- params: $params ---" | tee -a $OUT
  python3 phase2_charsum_sweep.py $params agree 2>&1 | tee -a $OUT
  echo "" | tee -a $OUT
done

echo "=== Sweep E: CS-lift adversarial inputs ===" | tee -a $OUT
for params in "97 16 8 2 1 100 50 cs_lift" "193 64 32 2 1 100 30 cs_lift"; do
  echo "--- params: $params ---" | tee -a $OUT
  python3 phase2_charsum_sweep.py $params agree 2>&1 | tee -a $OUT
  echo "" | tee -a $OUT
done

echo "=== DONE ===" | tee -a $OUT
