"""g3_bad_rho_polynomial_degree.py — explicitly construct bad-ρ polynomial.

For 2-mono pencil ρ z^a + z^{a-r} on L_n with above-J (a, a-r ≥ k):
- Enumerate all (T, z₀) extras pairs
- Compute candidate ρ = -E_{a-r}/E_a per pair
- Aggregate into multiset of ρ values
- Test if all bad ρ lie in single L_n^r-orbit (Conjecture E)

Then construct the polynomial P(ρ) ∈ F_q[ρ] vanishing on all bad ρ.
Compute its factorization and degree.

Goal: empirically check that deg(P) ≤ n/gcd(r, n) (orbit size).
"""
import sys, os
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from fri_2round_attack import setup_chain
from mds_decoder import precompute_diff_inv, batched_extras


def find_subgroup(q, n):
    g = None
    for cand in range(2, q):
        ok = True
        for d in range(1, n):
            if pow(cand, (q - 1) * d // n, q) == 1: ok = False; break
        if ok: g = cand; break
    if g is None: g = 3
    w = pow(g, (q - 1) // n, q)
    return [pow(w, i, q) for i in range(n)]


def lagrange_extra(T, z0, c, q):
    """Compute E_c(T, z0) = z0^c - Σ_{t ∈ T} t^c · ℓ_t(z0)."""
    e = pow(z0, c, q)
    for t in T:
        # Lagrange basis ℓ_t(z0)
        num = 1; den = 1
        for tp in T:
            if tp == t: continue
            num = num * (z0 - tp) % q
            den = den * (t - tp) % q
        ell_t = num * pow(den, q-2, q) % q
        e = (e - pow(t, c, q) * ell_t) % q
    return e


def find_bad_rho_polynomial(L, k, q, a, r, w_J):
    """Enumerate all (T, z0) and find candidate ρ values. Return bad ρ set."""
    n = len(L)
    b = a - r  # second monomial position

    # For dist ≤ w_J (agreement ≥ n - w_J), need T size ≥ n - w_J
    T_size = n - w_J
    print(f"n = {n}, k = {k}, a = {a}, b = {b}, r = {r}, T_size needed = {T_size}")

    # Enumerate T-subsets of L of size T_size, check if some ρ makes pencil agree on T
    # For each T: pick info_set I ⊂ T of size k+1, interpolate p, check residual
    # at remaining T \ I points

    if T_size > n:
        print(f"T_size {T_size} > n {n}, no agreement possible")
        return set()

    bad_rho = set()
    bad_alpha = set()

    # For each (T_size)-subset of L:
    cnt = 0
    for T in combinations(range(n), T_size):
        T_vals = [L[i] for i in T]
        # Pick first k+1 indices as I; rest are constraints
        I_idx = T_vals[:k+1]
        constraint_idx = T_vals[k+1:]

        # Each constraint gives 1 equation: ρ · E_a(I, c) + E_b(I, c) = 0
        # where E_c(I, x0) = x0^c - Σ_{i ∈ I} i^c · ℓ_i(x0)
        # Solve for ρ. If multiple constraints, must be consistent.

        constraint_eqs = []
        for c in constraint_idx:
            E_a = lagrange_extra(I_idx, c, a, q)
            E_b = lagrange_extra(I_idx, c, b, q)
            constraint_eqs.append((E_a, E_b))

        # Find ρ consistent with all eqs
        # ρ = -E_b/E_a (when E_a ≠ 0)
        rho_candidates = set()
        for E_a, E_b in constraint_eqs:
            if E_a == 0 and E_b != 0:
                continue  # inconsistent
            elif E_a == 0 and E_b == 0:
                continue  # trivial (any ρ works for this single eq)
            else:
                rho = (-E_b * pow(E_a, q-2, q)) % q
                rho_candidates.add(rho)

        if len(rho_candidates) == 1:
            rho = rho_candidates.pop()
            bad_rho.add(rho)
        elif len(rho_candidates) == 0:
            # All E_a = 0 case (degenerate); could be many bad ρ
            # Actually means all constraints trivial → any ρ works for this T
            # This is the "all-α bad" case. Add a flag.
            cnt += 1

        if len(bad_rho) > 200: break  # cap

    print(f"# bad ρ found: {len(bad_rho)}")
    if cnt > 0:
        print(f"# T's with all-zero E_a (any ρ works): {cnt}")
    return bad_rho


def check_orbit_structure(bad_rho, q, omega_n, r):
    """Check if bad_rho is union of orbits under ρ ↦ ω^r · ρ action."""
    if not bad_rho:
        print("Empty bad set.")
        return
    omega_r = pow(omega_n, r, q)
    n = len(bad_rho)  # incorrect, but won't be used

    # Group bad_rho into orbits
    bad_set = set(bad_rho)
    orbits = []
    while bad_set:
        rho = next(iter(bad_set))
        orbit = []
        cur = rho
        while cur not in orbit:
            orbit.append(cur)
            cur = (cur * omega_r) % q
        for o in orbit:
            bad_set.discard(o)
        orbits.append(orbit)
    print(f"# orbits found: {len(orbits)}")
    for i, orb in enumerate(orbits):
        print(f"  Orbit {i}: size {len(orb)}: {sorted(orb)[:10]}...")
    return orbits


def main():
    # Test cases (toy and small extensions)
    cases = [
        (97, 8, 2, 4, 1),     # (32, 8) toy, n_2 = 8, a=4, r=1
        (97, 8, 2, 4, 2),     # n=8, a=4, r=2 → orbit 4
        (193, 16, 4, 8, 4),   # (64, 16), n_2 = 16, a=8, r=4 → orbit 4
        (193, 16, 4, 9, 5),   # n=16, r=5 → orbit 16/gcd(5,16) = 16
    ]
    for q, n, k, a, r in cases:
        print(f"\n=== q={q}, n={n}, k={k}, a={a}, r={r} ===")
        L = find_subgroup(q, n)
        omega_n = L[1]
        w_J = n - int(round(np.sqrt(k * n)))
        orbit_size = n // int(np.gcd(r, n))
        print(f"L_{n}, w_J = {w_J}, orbit_size predicted = {orbit_size}")

        bad_rho = find_bad_rho_polynomial(L, k, q, a, r, w_J)
        orbits = check_orbit_structure(bad_rho, q, omega_n, r)
        if orbits:
            m = len(orbits)
            print(f"Conjecture E (m ≤ 1): {'PASS' if m <= 1 else 'FAIL'} (m = {m})")


if __name__ == "__main__":
    main()
