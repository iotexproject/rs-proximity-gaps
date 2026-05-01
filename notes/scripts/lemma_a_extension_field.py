#!/usr/bin/env python3 -u
"""B1 — Extension-field FRI/uniform ratio test.

c322's Note 0134 reports FRI/uniform ratio ~ 1.40 +/- 0.10 (4 sigma above 1)
on base-field F_17. The deployment table targets EXTENSION fields
(KoalaBear-ext6, BabyBear-ext4, Mersenne31-ext2). If the structural
amplification is base-field-specific, extensions might give ratio ~ 1
and rescue Lemma A on extension-field rows.

This script implements F_q = F_p[X]/(irred) for small (p, k) and runs
the same FRI-curve abstraction (zero-padded round-1 syndrome) used by
lemma_a_deployment_scale.py. Compares:

  (n=8, c=3): F_17 (baseline, k=1) vs F_49 (k=2) vs F_81 (k=4)

If extension fields give ratio ~ 1 (= no amplification), then
extension-field rows of paper3 deployment table can keep an R1 claim
under a regime-restricted Lemma A. If extensions also give ratio > 1,
Lemma A is dead at deployment regardless of base/ext.
"""

import os
import sys
import random
import time
from itertools import product, combinations
from math import comb


# ---------------------------------------------------------------------------
# F_q arithmetic via F_p[X]/(irred)
# ---------------------------------------------------------------------------

class FieldFq:
    """F_p^k as F_p[X]/(irred). Elements are tuples of length k.

    irred is a list [a_0, ..., a_k] with a_k = 1 (monic), representing the
    polynomial sum a_i X^i.
    """

    def __init__(self, p, k, irred):
        assert irred[k] == 1
        assert len(irred) == k + 1
        self.p = p
        self.k = k
        self.irred = irred
        self.q = p ** k

    def zero(self):
        return tuple([0] * self.k)

    def one(self):
        return tuple([1] + [0] * (self.k - 1)) if self.k > 0 else ()

    def from_int(self, n):
        return tuple([n % self.p] + [0] * (self.k - 1))

    def add(self, a, b):
        return tuple((a[i] + b[i]) % self.p for i in range(self.k))

    def sub(self, a, b):
        return tuple((a[i] - b[i]) % self.p for i in range(self.k))

    def neg(self, a):
        return tuple((-a[i]) % self.p for i in range(self.k))

    def mul(self, a, b):
        if self.k == 1:
            return ((a[0] * b[0]) % self.p,)
        prod = [0] * (2 * self.k - 1)
        for i in range(self.k):
            ai = a[i]
            if ai == 0:
                continue
            for j in range(self.k):
                prod[i + j] = (prod[i + j] + ai * b[j]) % self.p
        # Reduce X^d for d >= k via X^k ≡ -sum_{i<k} irred[i] X^i.
        for d in range(2 * self.k - 2, self.k - 1, -1):
            c = prod[d]
            if c == 0:
                continue
            for i in range(self.k):
                prod[d - self.k + i] = (
                    prod[d - self.k + i] - c * self.irred[i]
                ) % self.p
            prod[d] = 0
        return tuple(prod[: self.k])

    def pow(self, a, n):
        if n < 0:
            return self.pow(self.inv(a), -n)
        result = self.one()
        base = a
        while n > 0:
            if n & 1:
                result = self.mul(result, base)
            base = self.mul(base, base)
            n >>= 1
        return result

    def inv(self, a):
        # Fermat: a^(q-2) for a != 0
        return self.pow(a, self.q - 2)

    def is_zero(self, a):
        return all(c == 0 for c in a)

    def eq(self, a, b):
        return all(a[i] == b[i] for i in range(self.k))

    def random(self, rng):
        return tuple(rng.randrange(self.p) for _ in range(self.k))

    def all_elements(self):
        for tup in product(range(self.p), repeat=self.k):
            yield tup


# Irreducible polynomial library for the (p, k) we test.
# Format: [a_0, ..., a_k] with a_k = 1 (monic), so poly = sum a_i X^i.
IRRED = {
    (17, 1): [0, 1],          # placeholder, k=1 doesn't reduce
    ( 7, 2): [4, 0, 1],       # X^2 + 4 over F_7  (= X^2 - 3, 3 NQR mod 7)
    ( 5, 2): [2, 0, 1],       # X^2 + 2 over F_5  (2 NQR mod 5)
    ( 3, 2): [1, 0, 1],       # X^2 + 1 over F_3  (-1 NQR mod 3)
    ( 3, 4): [2, 2, 0, 0, 1], # X^4 + 2X^3 + 2 over F_3 (Conway poly for F_81)
    (41, 1): [0, 1],
    (73, 1): [0, 1],
}


def make_field(p, k):
    irred = IRRED[(p, k)]
    return FieldFq(p, k, irred)


def find_primitive(F):
    """Find a generator of F^*."""
    q = F.q
    factors = []
    n = q - 1
    d = 2
    while d * d <= n:
        if n % d == 0:
            factors.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        factors.append(n)

    for cand in F.all_elements():
        if F.is_zero(cand):
            continue
        ok = True
        for r in factors:
            if F.eq(F.pow(cand, (F.q - 1) // r), F.one()):
                ok = False
                break
        if ok:
            return cand
    raise RuntimeError(f"No primitive element found in F_{F.q}")


def subgroup_of_order(F, n):
    """Return n elements of F^* forming a cyclic subgroup of order n."""
    if (F.q - 1) % n != 0:
        return None
    g = find_primitive(F)
    h = F.pow(g, (F.q - 1) // n)
    L = []
    cur = F.one()
    for _ in range(n):
        L.append(cur)
        cur = F.mul(cur, h)
    seen = set(L)
    assert len(seen) == n, f"L generation failed: {len(seen)} != {n}"
    return L


def vandermonde_row(v, D, F):
    return [F.pow(v, j) for j in range(D)]


def kernel_basis(V_E, F, D):
    """Reduced row-echelon kernel basis of |E| x D matrix V_E over F."""
    n_rows = len(V_E)
    A = [list(row) for row in V_E]
    pivots = []
    for j in range(D):
        pr = None
        for i in range(len(pivots), n_rows):
            if not F.is_zero(A[i][j]):
                pr = i
                break
        if pr is None:
            continue
        prr = len(pivots)
        A[prr], A[pr] = A[pr], A[prr]
        inv = F.inv(A[prr][j])
        A[prr] = [F.mul(x, inv) for x in A[prr]]
        for i in range(n_rows):
            if i != prr and not F.is_zero(A[i][j]):
                factor = A[i][j]
                A[i] = [
                    F.sub(x, F.mul(factor, A[prr][k]))
                    for k, x in enumerate(A[i])
                ]
        pivots.append(j)
        if len(pivots) == n_rows:
            break
    free = [j for j in range(D) if j not in pivots]
    basis = []
    for fj in free:
        v = [F.zero()] * D
        v[fj] = F.one()
        for k_idx, pj in enumerate(pivots):
            v[pj] = F.neg(A[k_idx][fj])
        basis.append(v)
    return basis


def precompute_E_kernels(L, F, D, w):
    all_kers = []
    n = len(L)
    for E_idx in combinations(range(n), w):
        V_E = [vandermonde_row(L[v], D, F) for v in E_idx]
        all_kers.append(kernel_basis(V_E, F, D))
    return all_kers


def count_M(s1, s2, F, D, c, w, all_kers):
    """Count distinct gamma in F such that s1 + gamma s2 in V_E for some
    size-w support E."""
    realizers = set()
    for ker in all_kers:
        a_coords = []
        b_coords = []
        for kr in ker:
            ac = F.zero()
            bc = F.zero()
            for ki, s2i in zip(kr, s2):
                ac = F.add(ac, F.mul(ki, s2i))
            for ki, s1i in zip(kr, s1):
                bc = F.add(bc, F.mul(ki, s1i))
            a_coords.append(ac)
            b_coords.append(bc)
        nz = next(
            (j for j in range(len(a_coords)) if not F.is_zero(a_coords[j])),
            None,
        )
        if nz is None:
            continue
        # gamma = -b_nz / a_nz
        g = F.neg(F.mul(b_coords[nz], F.inv(a_coords[nz])))
        # Check proportionality: a_j b_nz == a_nz b_j for all j
        prop = True
        for j in range(len(a_coords)):
            lhs = F.mul(a_coords[j], b_coords[nz])
            rhs = F.mul(a_coords[nz], b_coords[j])
            if not F.eq(lhs, rhs):
                prop = False
                break
        if prop:
            realizers.add(g)
    return len(realizers)


def even_odd_split(coeffs):
    return coeffs[0::2], coeffs[1::2]


def fri_curve_from_f(f_coeffs, F, D):
    fe, fo = even_odd_split(f_coeffs)
    fe_e, fe_o = even_odd_split(fe)
    fo_e, fo_o = even_odd_split(fo)

    def pad(v, length):
        v = list(v[:length])
        while len(v) < length:
            v.append(F.zero())
        return v

    return pad(fe_e, D), pad(fo_e, D), pad(fe_o, D), pad(fo_o, D)


def n_hits_along_line(u_1, v_1, u_2, v_2, F, D, c, w, T, all_kers, all_alphas):
    hits = 0
    for alpha in all_alphas:
        s1 = [F.add(u_1[j], F.mul(alpha, v_1[j])) for j in range(D)]
        s2 = [F.add(u_2[j], F.mul(alpha, v_2[j])) for j in range(D)]
        if count_M(s1, s2, F, D, c, w, all_kers) > T:
            hits += 1
    return hits


def sweep(F, n, c, n_lines, label, seed=2026):
    L = subgroup_of_order(F, n)
    if L is None:
        print(f"Skip {label}: no subgroup of order {n} in F_{F.q}*")
        return None
    k_rs = n // 2
    D = (n + k_rs) // 2
    w = D - c
    T = (2 * D - 1) // c
    if w < 1 or T < 1 or w + 1 > n:
        print(f"Skip {label}: degenerate (w={w}, T={T})")
        return None

    bin_nw1 = comb(n, w + 1)
    pred_per_line = bin_nw1 / (F.q ** (2 * c - 3))

    print(
        f"=== {label}: n={n}, c={c}, q={F.q}={F.p}^{F.k}, "
        f"D={D}, w={w}, T={T} ===",
        flush=True,
    )
    print(
        f"  C(n, w+1) = {bin_nw1}, pred E[N]/line = {pred_per_line:.4e}",
        flush=True,
    )

    t0 = time.time()
    all_kers = precompute_E_kernels(L, F, D, w)
    print(
        f"  precomputed {len(all_kers)} kernels  ({time.time()-t0:.1f}s)",
        flush=True,
    )

    all_alphas = list(F.all_elements())
    rng = random.Random(seed)

    # Uniform line.
    t0 = time.time()
    rand_total = 0
    rand_max = 0
    for line_i in range(n_lines):
        u_1 = [F.random(rng) for _ in range(D)]
        v_1 = [F.random(rng) for _ in range(D)]
        u_2 = [F.random(rng) for _ in range(D)]
        v_2 = [F.random(rng) for _ in range(D)]
        h = n_hits_along_line(u_1, v_1, u_2, v_2, F, D, c, w, T, all_kers, all_alphas)
        rand_total += h
        rand_max = max(rand_max, h)
    rand_avg = rand_total / n_lines
    print(
        f"  uniform: avg={rand_avg:.4f}, max={rand_max:>3}, total={rand_total} "
        f"({n_lines} lines, {time.time()-t0:.1f}s)",
        flush=True,
    )

    # FRI curve.
    rng = random.Random(seed + 1)
    t0 = time.time()
    fri_total = 0
    fri_max = 0
    for line_i in range(n_lines):
        f = [F.random(rng) for _ in range(2 * n)]
        u_1, v_1, u_2, v_2 = fri_curve_from_f(f, F, D)
        h = n_hits_along_line(u_1, v_1, u_2, v_2, F, D, c, w, T, all_kers, all_alphas)
        fri_total += h
        fri_max = max(fri_max, h)
    fri_avg = fri_total / n_lines
    print(
        f"  FRI:     avg={fri_avg:.4f}, max={fri_max:>3}, total={fri_total} "
        f"({n_lines} curves, {time.time()-t0:.1f}s)",
        flush=True,
    )

    if rand_total > 0 and fri_total > 0:
        ratio = fri_avg / rand_avg
        se = ratio * (1.0 / rand_total + 1.0 / fri_total) ** 0.5
        print(
            f"  RATIO FRI/unif = {ratio:.3f} +/- {se:.3f}  "
            f"(unif={rand_total}, FRI={fri_total})",
            flush=True,
        )
    else:
        print(
            f"  RATIO insufficient hits (unif={rand_total}, FRI={fri_total})",
            flush=True,
        )

    return {
        "label": label,
        "n": n,
        "c": c,
        "q": F.q,
        "p": F.p,
        "k": F.k,
        "n_lines": n_lines,
        "rand_total": rand_total,
        "fri_total": fri_total,
        "rand_avg": rand_avg,
        "fri_avg": fri_avg,
        "ratio": (fri_avg / rand_avg) if rand_avg > 0 else None,
    }


def main():
    print("B1 — Extension-field FRI/uniform ratio test")
    print("=" * 78)
    print()

    # Strategy: (n=8, c=2) gives high hit density (pred = 56/q per line,
    # 100x more hits than c=3 at q=17) so a small number of lines is enough
    # to get tight SE.  Compare base F_17 vs ext2 F_49 vs ext4 F_81.
    #
    # If extension fields give ratio ~ 1, the FRI-vs-uniform amplification
    # is base-field-specific and Lemma A might survive on ext-field rows.
    # If ext fields also give ratio > 1, Lemma A is dead at deployment
    # regardless of base/ext.
    configs = []
    # F_17 baseline (already done, retained for reproducibility)
    configs.append(("F_17 (k=1) c=2",  make_field(17, 1), 8, 2, 1500))
    # F_49 ext2 main test
    configs.append(("F_49 (k=2) c=2",  make_field( 7, 2), 8, 2,  500))
    # F_81 ext4 (k=4) — optional, expensive
    configs.append(("F_81 (k=4) c=2",  make_field( 3, 4), 8, 2,  100))

    rows = []
    for label, F, n, c, nl in configs:
        r = sweep(F, n, c, nl, label)
        if r is not None:
            rows.append(r)
        print()

    print("=" * 78)
    print("SUMMARY")
    print("=" * 78)
    print(
        f"{'config':<24} {'n':>3} {'c':>2} {'q':>5} "
        f"{'unif tot':>9} {'FRI tot':>9} {'ratio':>10}"
    )
    print("-" * 78)
    for r in rows:
        if r["ratio"] is None:
            ratio_str = "(unif=0)"
        else:
            se = (
                r["ratio"]
                * (1.0 / r["rand_total"] + 1.0 / r["fri_total"]) ** 0.5
                if r["rand_total"] > 0 and r["fri_total"] > 0
                else 0
            )
            ratio_str = f"{r['ratio']:.2f}±{se:.2f}"
        print(
            f"{r['label']:<24} {r['n']:>3} {r['c']:>2} {r['q']:>5} "
            f"{r['rand_total']:>9} {r['fri_total']:>9} {ratio_str:>10}"
        )

    print()
    print("Interpretation:")
    print(" - Baseline c322 (8, 3, 17): ratio 1.40 +/- 0.10 (4 sigma > 1)")
    print(" - If extension rows give ratio ~ 1, Lemma A might survive on")
    print("   extension-field deployment rows under regime restriction.")
    print(" - If extension rows also give ratio > 1, Lemma A is dead at")
    print("   deployment regardless of extension structure.")


if __name__ == "__main__":
    main()
