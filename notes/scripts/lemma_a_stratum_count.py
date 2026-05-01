#!/usr/bin/env python3 -u
"""Lemma A — direct S-resonance count for the leading stratum |S|=w+1.

OPEN_PROBLEMS.md / Paper 3 §8.2 conjecture: for a generic affine line
ℓ(α) = (u_1 + α v_1, u_2 + α v_2) in F_q^{2D},

    #{α ∈ F_q : ℓ(α) ∈ V_bad}  ≤  n^{O(c)}.

Reduction (this script): bound the leading-stratum sum

    R_lead(ℓ) := #{S ⊂ [n], |S| = w+1 : ∃ α with ℓ(α) ∈ V_S × V_S}.

Each V_S × V_S is a codim-2(c-1) linear subspace; for a generic line not
parallel to V_S × V_S, line ∩ V_S × V_S is at most one α, so

    #{α-hits in leading stratum}  =  Σ_S 1[line ∩ V_S × V_S ≠ ∅]  =  R_lead.

Sub-leading strata contribute strictly less (Paper 3 §5.3 codim
accounting), so R_lead drives the total within a poly(c, T) factor.

Per S, line crosses V_S × V_S iff the 2(c-1) linear constraints
"⟨X^k p_S, u_i + α v_i⟩ = 0 for k ∈ {0,...,c-2}, i ∈ {1,2}" admit a
common α. Equivalently:

    A_S := (⟨X^k p_S, u_1⟩)_k,  B_S := (⟨X^k p_S, v_1⟩)_k,
    C_S := (⟨X^k p_S, u_2⟩)_k,  D_S := (⟨X^k p_S, v_2⟩)_k

(four vectors in F_q^{c-1}) must satisfy:
  (i)  A_S + α B_S = 0 for some α  ⇔  rank([A_S | B_S]) ≤ 1
  (ii) C_S + α D_S = 0 at the same α
This is 2c - 3 algebraic equations on the line ↔ V_S^⊥ alignment.

p_S(X) := ∏_{v∈S}(X - L_v); V_S^⊥ basis is {p_S, X·p_S, ..., X^{c-2}·p_S}.

Output: empirical R_lead(n, c) for several (n, c, p) with q ≫ T,
fit the exponent via log-log regression to test R_lead ~ C · n^{c-1}.
"""

import os
import sys
import random
import time
from itertools import combinations
from math import comb, log

random.seed(2026)


def small_field_subgroup(p: int, n: int):
    if (p - 1) % n != 0:
        return None
    for g in range(2, p):
        ok = True
        d = 1
        while d * d <= p - 1:
            if (p - 1) % d == 0:
                if d < p - 1 and pow(g, d, p) == 1:
                    ok = False
                    break
                e = (p - 1) // d
                if e < p - 1 and pow(g, e, p) == 1:
                    ok = False
                    break
            d += 1
        if not ok:
            continue
        h = pow(g, (p - 1) // n, p)
        L = [pow(h, i, p) for i in range(n)]
        if len(set(L)) == n:
            return L
    return None


def poly_mul(a, b, p):
    """Multiply polynomials given as coefficient lists (low-to-high)."""
    r = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            r[i + j] = (r[i + j] + ai * bj) % p
    return r


def p_S_coeffs(S_idx, L, p, length):
    """Coefficients of p_S(X) = ∏_{v∈S}(X - L_v) as a list of length `length`,
    padded with zeros on the high side."""
    poly = [1]  # constant polynomial 1
    for v in S_idx:
        # multiply by (X - L_v) = [-L_v, 1]
        poly = poly_mul(poly, [(-L[v]) % p, 1], p)
    if len(poly) < length:
        poly = poly + [0] * (length - len(poly))
    return poly[:length]


def shifted_basis_inner(p_S, x, c, D, p):
    """Compute (⟨X^k · p_S, x⟩)_{k=0..c-2}.

    ⟨X^k · p_S, x⟩ = Σ_j (X^k p_S)_j · x_j
                  = Σ_j (p_S)_{j-k} · x_j   (with p_S of degree w+1)
                  = Σ_i (p_S)_i · x_{i+k}.

    p_S has w+2 coefficients (indices 0..w+1). For valid k in [0, c-2],
    the shifted index range is [k, w+1+k] ⊂ [0, D-1] since w+1+k ≤
    w+1+c-2 = D-1.
    """
    outs = []
    w_plus_1 = len(p_S) - 1  # last nonzero index of p_S can be ≤ this; pad guarantees w+1
    # Actually p_S has degree exactly w+1, so length is w+2, but we passed
    # length = D, so trailing entries are 0.
    L_pS = w_plus_1 + 1
    for k in range(c - 1):
        s = 0
        for i in range(L_pS):
            j = i + k
            if j >= D:
                break
            pi = p_S[i]
            if pi == 0:
                continue
            s = (s + pi * x[j]) % p
        outs.append(s)
    return outs


def line_crosses_VS_squared(p_S, u1, v1, u2, v2, c, D, p):
    """Test whether ∃ α ∈ F_p with (u_1+αv_1, u_2+αv_2) ∈ V_S × V_S.

    Returns 1 if line crosses, 0 otherwise.
    """
    A = shifted_basis_inner(p_S, u1, c, D, p)
    B = shifted_basis_inner(p_S, v1, c, D, p)
    C = shifted_basis_inner(p_S, u2, c, D, p)
    Dv = shifted_basis_inner(p_S, v2, c, D, p)

    # (i) A + α B = 0  ⇔  exists α with A_i + α B_i = 0 for all i.
    #     If B ≡ 0: need A ≡ 0.
    #     Else: pick first i with B_i ≠ 0, α = -A_i / B_i, check rest.
    # (ii) C + α D = 0 at same α.

    nz = next((i for i in range(c - 1) if B[i] != 0), None)
    if nz is None:
        # B ≡ 0; line direction's u_1-component projects to 0 in V_S^⊥.
        # Then condition is A ≡ 0 AND (C + α D = 0 for some α).
        if any(a != 0 for a in A):
            return 0
        # A ≡ 0 means u_1 ∈ V_S. Then the cross is satisfied iff also
        # exists α with u_2 + α v_2 ∈ V_S, i.e., C + α D = 0 has solution.
        # rank([C | D]) ≤ 1.
        nz2 = next((i for i in range(c - 1) if Dv[i] != 0), None)
        if nz2 is None:
            return 1 if all(c_ == 0 for c_ in C) else 0
        alpha2 = (-C[nz2] * pow(Dv[nz2], p - 2, p)) % p
        for i in range(c - 1):
            if (C[i] + alpha2 * Dv[i]) % p != 0:
                return 0
        return 1
    alpha = (-A[nz] * pow(B[nz], p - 2, p)) % p
    # Check rest of A + α B
    for i in range(c - 1):
        if i == nz:
            continue
        if (A[i] + alpha * B[i]) % p != 0:
            return 0
    # Check C + α D
    for i in range(c - 1):
        if (C[i] + alpha * Dv[i]) % p != 0:
            return 0
    return 1


def R_lead_for_line(L, n, c, D, w, p, u1, v1, u2, v2):
    """Count #{S, |S|=w+1 : line crosses V_S × V_S}."""
    count = 0
    for S_idx in combinations(range(n), w + 1):
        pS = p_S_coeffs(S_idx, L, p, D)
        count += line_crosses_VS_squared(pS, u1, v1, u2, v2, c, D, p)
    return count


def random_vec(D, p):
    return [random.randrange(p) for _ in range(D)]


def sweep_one(n, c, p, n_lines):
    L = small_field_subgroup(p, n)
    if L is None:
        return None
    k = n // 2
    D = (n + k) // 2
    w = D - c
    T = (2 * D - 1) // c
    if w < 1 or T < 1 or w + 1 > n:
        return None
    counts = []
    t0 = time.time()
    for _ in range(n_lines):
        u1 = random_vec(D, p)
        v1 = random_vec(D, p)
        u2 = random_vec(D, p)
        v2 = random_vec(D, p)
        r = R_lead_for_line(L, n, c, D, w, p, u1, v1, u2, v2)
        counts.append(r)
    dt = time.time() - t0
    n_subsets = comb(n, w + 1)
    avg = sum(counts) / len(counts)
    mx = max(counts)
    print(
        f"(n={n}, c={c}, p={p}, D={D}, w={w}, T={T})  "
        f"#S={n_subsets:>10}  R_lead avg={avg:7.2f}  max={mx:>5}  "
        f"({n_lines} lines, {dt:.1f}s)",
        flush=True,
    )
    return {
        "n": n, "c": c, "p": p, "D": D, "w": w, "T": T,
        "n_subsets": n_subsets,
        "R_avg": avg, "R_max": mx, "counts": counts,
    }


def fit_exponent(rows, c_target):
    """Fit log(R_avg) = a + b log(n) for the c=c_target rows. Returns b."""
    pts = [(r["n"], r["R_avg"]) for r in rows if r["c"] == c_target and r["R_avg"] > 0]
    if len(pts) < 2:
        return None
    xs = [log(n) for n, _ in pts]
    ys = [log(r) for _, r in pts]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    return num / den


def main():
    # Field-size choice: must satisfy q ≫ T so V_bad is a proper subset.
    # We also want a multiplicative subgroup of order n in F_q^*, i.e.,
    # n | (q-1). Below: for each n, we pick the smallest q ≡ 1 (mod n)
    # with q ≥ 257 (to keep |F| comfortably above T).
    print("Lemma A — leading-stratum S-resonance count")
    print("=" * 80)
    print("R_lead(ℓ) := #{S, |S|=w+1 : line ℓ crosses V_S × V_S}")
    print("Conjecture: R_lead = O(n^{c-1}) at fixed c.")
    print()

    cases = [
        # (n, c, p, n_lines)
        # c = 2 sweep
        ( 8, 2, 257, 50),
        (10, 2, 251, 50),
        (12, 2, 241, 50),
        (14, 2, 281, 50),
        (16, 2, 257, 30),
        (20, 2, 241, 20),
        # c = 3 sweep
        ( 8, 3, 257, 50),
        (10, 3, 251, 50),
        (12, 3, 241, 50),
        (14, 3, 281, 30),
        (16, 3, 257, 20),
        # c = 4 sweep
        (10, 4, 251, 50),
        (12, 4, 241, 30),
        (14, 4, 281, 20),
        (16, 4, 257, 10),
    ]
    rows = []
    for n, c, p, nl in cases:
        r = sweep_one(n, c, p, nl)
        if r is not None:
            rows.append(r)

    print()
    print("=" * 80)
    print("SUMMARY: log-log fit of R_lead(n) at fixed c (slope = empirical exponent)")
    print("=" * 80)
    for c in (2, 3, 4):
        b = fit_exponent(rows, c)
        if b is None:
            print(f"  c={c}:  insufficient nonzero data")
        else:
            print(f"  c={c}:  fitted slope b ≈ {b:.3f}   (conjecture: c-1 = {c-1})")
    print()
    print("Interpretation:")
    print("  - Fitted slope close to c-1 supports the leading-stratum O(n^{c-1})")
    print("    bound that drives the n^{O(c)} curve-intersection conjecture.")
    print("  - R_lead ≪ C(n, w+1) confirms uniform-vs-curve measure separation.")


if __name__ == "__main__":
    main()
