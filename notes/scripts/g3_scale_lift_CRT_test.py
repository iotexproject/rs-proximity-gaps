"""Test Theorem 0336.A: deg(CRT(S, a, r)) ≥ k for no-full S.

Setup (Note 0336): For L = ⟨ζ⟩ cyclic of order n = 4k, no-full 2k-subset S,
and (a, r) with 1 ≤ a ≤ 3, 0 ≤ r < k, the CRT polynomial A_0 satisfying:
  A_0 ≡ 0 (mod G_0)
  A_0 ≡ (i^{ac} - 1) x^r (mod G_c) for c = 1, 2, 3
should have degree ≥ k (paper-grade target).

Implementation: work in F_p[x] with modulus throughout via sympy.Poly.
"""
import sys
import random
from sympy import Poly, Symbol, gcdex, rem, quo, Integer, prod, ZZ
from sympy.polys.domains import GF


def find_primitive_root(p, n):
    assert (p - 1) % n == 0
    for g in range(2, p):
        order = pow(g, (p - 1) // n, p)
        is_prim = True
        for d in [m for m in range(1, n) if n % m == 0 and m < n]:
            if pow(order, d, p) == 1:
                is_prim = False
                break
        if is_prim and pow(order, n, p) == 1:
            return order
    return None


def crt_test(p, n, k, S):
    """Compute CRT(S, a, r) for all (a, r), check deg ≥ k for no-full S."""
    omega = find_primitive_root(p, n)
    L = [pow(omega, j, p) for j in range(n)]
    i_root = pow(omega, n // 4, p)

    blocks = [[], [], [], []]
    for x in L:
        xk = pow(x, k, p)
        for b in range(4):
            ib = pow(i_root, b, p)
            if xk == ib:
                blocks[b].append(x)
                break

    s_b = [sum(1 for x in S if x in blocks[b]) for b in range(4)]
    if not all(s < k for s in s_b):
        return "NOT_NO_FULL", s_b

    S_b = [[x for x in S if x in blocks[b]] for b in range(4)]

    x_sym = Symbol("x")
    Fp = GF(p)

    # G_b in F_p[x]
    Gb = []
    for b in range(4):
        gb = Poly(1, x_sym, domain=Fp)
        for xi in S_b[b]:
            gb = gb * Poly(x_sym - xi, x_sym, domain=Fp)
        Gb.append(gb)

    G_prod = Gb[0] * Gb[1] * Gb[2] * Gb[3]

    results = []
    for a in [1, 2, 3]:
        for r in range(k):
            # A_0 = sum over b of (h_b * Gother_b * R_b)
            # where Gother_b = G_prod / G_b
            # h_b = inv(Gother_b mod G_b) in F_p[x]
            # R_0 = 0, R_c = (i^{ac} - 1) x^r

            A0 = Poly(0, x_sym, domain=Fp)
            for b in range(4):
                if b == 0:
                    Rb = Poly(0, x_sym, domain=Fp)
                else:
                    iab = pow(i_root, a * b, p) % p
                    coef = (iab - 1) % p
                    if coef == 0:
                        Rb = Poly(0, x_sym, domain=Fp)
                    else:
                        Rb = Poly(coef * x_sym ** r, x_sym, domain=Fp)
                Gother = quo(G_prod, Gb[b])
                # gcdex(Gother, Gb[b]) over F_p[x]
                g_ext, h_b, _ = Gother.gcdex(Gb[b])
                # h_b * Gother * Rb
                A_b_lift = h_b * Gother * Rb
                A0 = A0 + A_b_lift

            # Reduce mod G_prod
            A0_red = rem(A0, G_prod)

            deg = A0_red.degree() if A0_red != 0 else -1
            results.append({
                "a": a, "r": r, "deg": deg, "deg_ge_k": deg >= k
            })
    return results, s_b


def random_no_full_S(p, n, k, seed=42):
    rng = random.Random(seed)
    omega = find_primitive_root(p, n)
    L = [pow(omega, j, p) for j in range(n)]
    i_root = pow(omega, n // 4, p)
    blocks = [[], [], [], []]
    for x in L:
        xk = pow(x, k, p)
        for b in range(4):
            ib = pow(i_root, b, p)
            if xk == ib:
                blocks[b].append(x)
                break
    while True:
        s = []
        rem_total = 2 * k
        for b in range(4):
            if b < 3:
                lo = max(0, rem_total - (3 - b) * (k - 1))
                hi = min(k - 1, rem_total)
                if lo > hi:
                    s = None
                    break
                s.append(rng.randint(lo, hi))
                rem_total -= s[-1]
            else:
                s.append(rem_total)
                if not (0 <= rem_total <= k - 1):
                    s = None
                    break
        if s is not None and all(0 <= ss < k for ss in s) and sum(s) == 2 * k:
            break
    S = []
    for b in range(4):
        S.extend(rng.sample(blocks[b], s[b]))
    return S, s


if __name__ == "__main__":
    # Test at k = 8 (n = 32, F_97) and k = 16 (n = 64, F_193)
    for p, n, k, n_trials in [(97, 32, 8, 50), (193, 64, 16, 20)]:
        print(f"\n=== Testing at (n, k) = ({n}, {k}) over F_{p}, {n_trials} trials ===")
        all_pass = True
        for trial in range(n_trials):
            S, s = random_no_full_S(p, n, k, seed=trial)
            results, s_b = crt_test(p, n, k, S)
            if results == "NOT_NO_FULL":
                continue
            max_deg = max(r["deg"] for r in results)
            n_below = sum(1 for r in results if r["deg"] < k)
            if n_below > 0:
                all_pass = False
                print(f"  Trial {trial} ({s}): COUNTEREXAMPLE — {n_below} (a,r) with deg<{k}")
                for r in results:
                    if r["deg"] < k:
                        print(f"    a={r['a']}, r={r['r']}, deg={r['deg']}")
            else:
                pass  # silent pass
        if all_pass:
            print(f"  ✓ All {n_trials} trials × 3*{k} (a,r) combinations PASS at (n={n}, k={k})")
        else:
            print(f"  ✗ Some trials FAIL at (n={n}, k={k})")
