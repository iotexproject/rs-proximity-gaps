"""g3_rate_half_base_case.py — K bound for 2-mono pencils at rate-1/2 base case.

paper2 thm:universal-K10 is stated at rate ρ = 1/4 (n_0 = 4 k_0).
ABF §6.3 deployment uses rate ρ = 1/2 (n_0 = 2 k_0).

The Substitution Principle (Note 0284) reduces 2-mono pencils at
(4k, k) to base case (4, 1) (rate 1/4) or (8, 2) (rate 1/4). For
rate 1/2, the corresponding base cases are (4, 2) and (8, 4) — a
SEPARATE enumeration is needed to obtain a K_s bound at rate 1/2.

This script enumerates max |B(α)| over all 2-mono pencils
h_α(z) = ρ z^a + α z^b on L_n (multiplicative subgroup of order n)
at base cases (n, k) ∈ {(4, 2), (8, 4)} above the Johnson bound
δ > 1 - sqrt(k/n) = 1 - sqrt(1/2) ≈ 0.293.

For each above-J 2-mono pencil, brute force computes
   K(a, b) := |{α ∈ F_q^* : Δ(h_α, RS_k) ≤ δ·n}|
over q ∈ {97, 193, 257}, and reports max K (the rate-1/2 K_s bound).
"""
from __future__ import annotations

import argparse
import itertools
from math import gcd, isqrt


def find_omega(q: int, n: int) -> int:
    assert (q - 1) % n == 0
    g_pow = (q - 1) // n
    for g in range(2, q):
        omega = pow(g, g_pow, q)
        if omega == 1:
            continue
        if pow(omega, n, q) == 1 and all(
                pow(omega, n // p, q) != 1 for p in [2, 3, 5, 7] if n % p == 0):
            return omega
    raise RuntimeError("no primitive n-th root")


def evaluate(coeffs, xs, q):
    out = []
    for x in xs:
        v = 0; xp = 1
        for c in coeffs:
            v = (v + c * xp) % q
            xp = (xp * x) % q
        out.append(v)
    return out


def all_RS(q, k, xs):
    return [evaluate(coeffs, xs, q)
            for coeffs in itertools.product(range(q), repeat=k)]


def min_dist(g, rs):
    n = len(g)
    best = n
    for c in rs:
        d = sum(1 for i in range(n) if g[i] != c[i])
        if d < best:
            best = d
            if best == 0: return 0
    return best


def K_bad(a, b, n, k, q, delta_n):
    omega = find_omega(q, n)
    L = [pow(omega, i, q) for i in range(n)]
    rs = all_RS(q, k, L)
    z_a = [pow(x, a, q) for x in L]
    z_b = [pow(x, b, q) for x in L]
    K = 0
    for alpha in range(1, q):  # nonzero α
        h = [(z_a[i] + alpha * z_b[i]) % q for i in range(n)]
        if min_dist(h, rs) <= delta_n:
            K += 1
    return K


def above_J_pairs(n, k):
    """Enumerate (a, b) with 1 ≤ a < b ≤ n - 1, both above k - 1, gcd(a,b,n) = 1."""
    out = []
    for a in range(k, n):
        for b in range(a + 1, n):
            if gcd(gcd(a, b), n) == 1:
                out.append((a, b))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, nargs="+", default=[17, 41])
    args = parser.parse_args()

    print("=== Rate-1/2 base case K-bound enumeration ===")
    print("paper2 thm:universal-K10 at rate 1/4 needs extension to rate 1/2 for ABF §6.3.")
    print("This script computes max K(a,b) for (n,k) ∈ {(4,2), (8,4)} above-J.")
    print()

    for n, k in [(4, 2), (8, 4)]:
        # Strict above-J: distance > J·n = (1 - sqrt(k/n)) · n = n - sqrt(nk).
        # Smallest integer above-J: delta_n = floor(n - sqrt(nk)) + 1.
        # At (4, 2): n - sqrt(8) = 4 - 2.83 = 1.17, so delta_n = 2.
        # At (8, 4): n - sqrt(32) = 8 - 5.66 = 2.34, so delta_n = 3.
        from math import sqrt, floor
        delta_J_n = n - sqrt(n * k)
        delta_n = floor(delta_J_n) + 1
        agree = n - delta_n
        t_J = isqrt(n * k)
        pairs = above_J_pairs(n, k)
        print(f"--- (n, k) = ({n}, {k}), rate {k/n:.3f}, "
              f"J-agreement t* = {t_J}, above-J agree ≤ {agree}, δ·n = {delta_n} ---")
        if not pairs:
            print(f"  No (a, b) above-J with gcd(a,b,n)=1 — base case trivial.", flush=True)
            print(flush=True)
            continue
        print(f"  Above-J coprime (a, b) pairs: {pairs}", flush=True)
        for q in args.q:
            if (q - 1) % n != 0:
                print(f"  q={q}: skip (n ∤ q-1)", flush=True)
                continue
            K_max = 0; argmax = None
            for (a, b) in pairs:
                K = K_bad(a, b, n, k, q, delta_n)
                print(f"  q={q}, (a,b)={(a,b)}: K = {K}", flush=True)
                if K > K_max:
                    K_max = K; argmax = (a, b)
            print(f"  q={q}: max K = {K_max} at (a, b) = {argmax}", flush=True)
        print(flush=True)

    print("=== Interpretation ===")
    print("If max K stays small (≤ 10) at base cases (4, 2) and (8, 4),")
    print("then thm:universal-K10 generalizes to rate 1/2 by the same")
    print("Substitution Principle: any 2-mono pencil at deployment (2k, k)")
    print("reduces to base case (4, 2) or (8, 4) via u = z^d, d = gcd(a,b,n).")
    print("This would close the rate-1/2 ABF §6.3 deployment gap.")


if __name__ == "__main__":
    main()
