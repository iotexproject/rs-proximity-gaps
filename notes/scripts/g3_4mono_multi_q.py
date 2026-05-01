"""g3_4mono_multi_q.py — 4-mono empirical K_4 across multiple primes.

Verify K_4 ≤ 7 (Note 0292) is structural, not a q=97 artifact, by
sweeping at q ∈ {97, 193, 257, 449, 1153} where 8 | q-1.

For each q, run 30-sample ρ-sweep over 35 irreducible 4-mono cases
at (n, k) = (8, 2). Report max |B(α)| per q.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_4mono_numerical import sweep_q


def main():
    n, k = 8, 2
    n_samples = 30
    primes = [97, 193, 257, 449, 1153]

    print(f"=== 4-mono multi-q empirical sweep at (n, k) = ({n}, {k}) ===")
    print(f"Sampling {n_samples} (ρ_1, ρ_2, ρ_3) per case, all 35 irreducible (a, b, c, d)")
    print()

    for q in primes:
        max_bad, max_case = sweep_q(n, k, q, n_samples)
        if max_bad is None:
            print(f"  q = {q:>5}: SKIP (no primitive {n}-th root of unity)")
        else:
            print(f"  q = {q:>5}: max |B(α)| = {max_bad} at {max_case}")

    print()
    print(f"Empirical K_4 trend across primes — values consistent ⟹ structural.")


if __name__ == "__main__":
    main()
