"""g3_coset_rigidity_test.py — verify coset-rigidity / coset-exclusion at deployment scales.

For (n, k) with n = 4k power-of-2 (deployment shape):
- Codex hypothesis: every size-2k one-ratio half-set certificate = union of 2 ⟨ω^{n/4}⟩-cosets.
- Empirical observation (this script): TRUE for sign-paired (b-a = ±n/2),
  weaker (coset-EXCLUSION) for non-sign-paired.

Output: for each (a, b) pencil, summarize coset-rigidity stats:
- # one-ratio witness half-sets
- # of which are exactly 2-coset unions
- coset-exclusion: which mod-4 classes are EMPTY in every witness
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from itertools import combinations
from math import isqrt
from collections import Counter, defaultdict

from g3_conjE_exact_halfset import subgroup, rho_for_halfset


def coset_pair_unions(n, k):
    """Enumerate all unions of 2 distinct mod-(n/k) classes — only valid at n=4k.

    At n=4k: classes are ⟨ω^4⟩-cosets, 4 classes of size n/4 each.
    A 2-coset union has size 2·(n/4) = n/2 = 2k. ✓
    """
    classes_per = n // 4
    classes = [[i for i in range(n) if i % 4 == c] for c in range(4)]
    pairs = []
    for c1, c2 in combinations(range(4), 2):
        idx = sorted(classes[c1] + classes[c2])
        pairs.append((tuple(idx), (c1, c2)))
    return pairs


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--q", type=int, required=True)
    args = ap.parse_args()
    n, k, q = args.n, args.k, args.q

    assert n == 4*k, f"deployment shape requires n=4k; got n={n}, k={k}"
    L = subgroup(q, n)
    t = isqrt(k*n)
    assert t*t == k*n

    coset_unions_set = {idx for idx, _ in coset_pair_unions(n, k)}
    print(f"# 2-coset unions = {len(coset_unions_set)} (= C(4,2)={6})")
    print(f"deployment scale (n={n}, k={k}, q={q}); halfset size = {t}")
    print()

    rows = []
    for a in range(k, n):
        for b in range(k, n):
            if a == b:
                continue
            sign_paired = (b - a) % n == n // 2

            n_one_ratio = 0
            n_coset_aligned = 0
            class_loads = [0, 0, 0, 0]   # total occupancy summed over witnesses
            seen_coset_pairs = set()
            seen_ratios = set()

            for ind in combinations(range(n), t):
                pts = [L[i] for i in ind]
                kind, rho = rho_for_halfset(pts, a, b, k, q)
                if kind != "one" or rho == 0:
                    continue
                n_one_ratio += 1
                seen_ratios.add(rho)
                ind_t = tuple(ind)
                if ind_t in coset_unions_set:
                    n_coset_aligned += 1
                    cs = tuple(sorted(set(i % 4 for i in ind)))
                    seen_coset_pairs.add(cs)
                for i in ind:
                    class_loads[i % 4] += 1

            empty_classes = tuple(c for c in range(4) if class_loads[c] == 0)
            sign_str = "SIGN-PAIRED" if sign_paired else "         "
            ratio_str = f"|bad ρ|={len(seen_ratios)}"
            print(
                f"  (a={a:2d},b={b:2d}) {sign_str} witnesses={n_one_ratio:3d} "
                f"coset-aligned={n_coset_aligned:3d} "
                f"empty-mod4={empty_classes} {ratio_str}"
            )
            rows.append((a, b, sign_paired, n_one_ratio, n_coset_aligned, empty_classes, len(seen_ratios)))

    # Summary stats
    print()
    sp_rows = [r for r in rows if r[2]]
    nsp_rows = [r for r in rows if not r[2]]
    sp_full_aligned = [r for r in sp_rows if r[3] > 0 and r[3] == r[4]]
    print(f"sign-paired pairs: {len(sp_rows)}; fully coset-aligned: {len(sp_full_aligned)}")
    nsp_with_witnesses = [r for r in nsp_rows if r[3] > 0]
    nsp_full_aligned = [r for r in nsp_with_witnesses if r[3] == r[4]]
    nsp_excluded = [r for r in nsp_with_witnesses if len(r[5]) > 0]
    print(f"non-sign-paired pairs with witnesses: {len(nsp_with_witnesses)}; "
          f"fully coset-aligned: {len(nsp_full_aligned)}; "
          f"with empty mod-4 class: {len(nsp_excluded)}")


if __name__ == "__main__":
    main()
