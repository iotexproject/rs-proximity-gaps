"""g3_alpha_line_orbit_intersection.py — test refined Conjecture E.

Refined Conjecture E (Note 0194): for any 3-pos sparse Reverse Pattern f̂,
the α-line in F_q² intersects bad-ratio orbits in at most 1 orbit.

Procedure:
1. Compute the bad ratio orbits for pure 2-mono pencil γ z^a + β z^b on L_n.
2. For each Reverse Pattern f̂ at (32, 8), compute (c, d_1, d_2) = arising
   pencil coefs.
3. Compute α-line: (c + α d_2, α d_1) for α ∈ F_q.
4. Count which orbits the α-line intersects.

Test on many Reverse supports at toy (32, 8). If all give ≤ 1 orbit: refined
Conjecture E holds at toy.
"""
import sys, os, random
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))

import numpy as np
from itertools import combinations
from fri_2round_attack import setup_chain, even_odd_parts


def evaluate_dft(fhat, L, p):
    n = len(L); f = [0]*n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j]: v = (v + fhat[j]*pow(x, j, p)) % p
        f[i] = v
    return f


def find_dft_supp(arr, L_subgroup, p):
    n = len(L_subgroup); n_inv = pow(n, p-2, p)
    supp = []
    for k in range(n):
        v = 0
        for i, z in enumerate(L_subgroup):
            v = (v + int(arr[i]) * pow(int(z), -k, p)) % p
        v = v * n_inv % p
        if v != 0:
            supp.append((k, v))
    return supp


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


def compute_bad_ratios_pure(L_n, k, a, b, q, w_J, sample_T):
    """Find bad (γ:β) ratios for pure pencil γ z^a + β z^b on L_n.

    Use sampled T-subsets. Each T determines candidate ratios via extras.
    """
    n = len(L_n); r = a - b
    bad_ratios = set()

    # Sample T's of size n - w_J = agreement
    T_size = n - w_J
    if T_size > n:
        return bad_ratios

    # Enumerate T-subsets
    for T in combinations(range(n), T_size):
        T_vals = [L_n[i] for i in T]
        I = T_vals[:k+1]
        rest = T_vals[k+1:]

        # For each extra point z0 ∈ rest: ρ · E_a(I, z0) + E_b(I, z0) = 0
        rho_candidates = []
        for z0 in rest:
            # Compute E_c(I, z0) = z0^c - Σ_{t ∈ I} t^c · ℓ_t(z0)
            E_a = pow(z0, a, q)
            E_b = pow(z0, b, q)
            for t in I:
                num = 1; den = 1
                for tp in I:
                    if tp == t: continue
                    num = num * (z0 - tp) % q
                    den = den * (t - tp) % q
                ell = num * pow(den, q-2, q) % q
                E_a = (E_a - pow(t, a, q) * ell) % q
                E_b = (E_b - pow(t, b, q) * ell) % q

            if E_a == 0:
                continue
            # Allow ρ as ratio γ/β (here β=1 implicit)
            # Actually ρ z^a + z^b = 0 form: ρ = -E_b/E_a means h(z) where γ = ρ, β = 1
            rho = (-E_b * pow(E_a, q-2, q)) % q
            rho_candidates.append(rho)

        if len(set(rho_candidates)) == 1 and rho_candidates:
            bad_ratios.add(rho_candidates[0])

    return bad_ratios


def compute_orbits(bad_ratios, q, omega_n, r):
    """Partition bad_ratios into orbits under ρ ↦ ω^r · ρ."""
    omega_r = pow(omega_n, r, q)
    bad_set = set(bad_ratios)
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
        orbits.append(set(orbit))
    return orbits


def compute_alpha_line_ratios(c, d1, d2, q):
    """Compute (γ, β) ratio γ/β for each α ∈ F_q* on the α-line.

    γ = c + α d2, β = α d1. ratio = γ/β when β ≠ 0.
    """
    ratios = {}
    for alpha in range(1, q):  # α=0 gives β=0, separate
        gamma = (c + alpha * d2) % q
        beta = (alpha * d1) % q
        if beta == 0:
            continue
        rho = (gamma * pow(beta, q-2, q)) % q
        ratios[alpha] = rho
    return ratios


def main():
    p = 97
    n0, k0 = 32, 8
    n2, k2 = 8, 2
    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]; L1 = chain[1][0]; L2 = chain[2][0]
    n2 = len(L2); omega_n2 = L2[1]
    w_J_L2 = n2 - int(round(np.sqrt(k2 * n2)))

    # Try multiple Reverse supports — first compute bad ratios for SAME (a, b) pencil
    # Most arising pencils at (32, 8) Reverse have (a, b) = (4, 3) (positions {3, 4} on L_2)
    # since c has 1 pos, d has 2 pos including a.

    # Actually let me just enumerate all 3-pos Reverse and group by (a, b) of the resulting pencil
    rev_pos = [j for j in range(k0, n0) if j % 4 in (2, 3)]
    triples = list(combinations(rev_pos, 3))
    print(f"Total above-J Reverse triples at (32, 8): {len(triples)}")

    # Group by (a, b) pencil structure
    by_ab = {}
    for sup in triples:
        coefs = [10, 92, 63]  # standard test coefs (toy default)
        fhat = [0]*n0
        for j, c in zip(sup, coefs): fhat[j] = c
        f = evaluate_dft(fhat, L0, p)
        f_e, f_o = even_odd_parts(f, L0, p)
        fe_e, fe_o = even_odd_parts(f_e, L1, p)
        fo_e, fo_o = even_odd_parts(f_o, L1, p)
        c_supp = find_dft_supp(fe_o, L2, p)
        d_supp = find_dft_supp(fo_o, L2, p)
        all_pos = sorted(set([j for j, _ in c_supp + d_supp]))
        if len(all_pos) == 2 and all(j >= k2 for j in all_pos):
            ab = (all_pos[1], all_pos[0])  # (a, b)
            if ab not in by_ab: by_ab[ab] = []
            # Extract (c, d1, d2)
            c_val = c_supp[0][1] if c_supp else 0
            c_pos = c_supp[0][0] if c_supp else None
            # d has 2 positions; one matches c position, the other is the other pencil position
            if c_pos == ab[0]:
                d_at_a = next((v for j, v in d_supp if j == ab[0]), 0)
                d_at_b = next((v for j, v in d_supp if j == ab[1]), 0)
                # h(α) = c_val·z^a + α·(d_at_b·z^b + d_at_a·z^a) → c=c_val, d2=d_at_a, d1=d_at_b
                cd = (c_val, d_at_b, d_at_a)
            elif c_pos == ab[1]:
                # c is at b position; d at both
                d_at_b = next((v for j, v in d_supp if j == ab[1]), 0)
                d_at_a = next((v for j, v in d_supp if j == ab[0]), 0)
                # h(α) = c_val·z^b + α·(d_at_a·z^a + d_at_b·z^b)
                # rearrange: (c_val + α d_at_b)·z^b + α d_at_a·z^a
                # standard form: γ z^a + β z^b → γ = α d_at_a, β = c_val + α d_at_b
                # So role of (γ, β) swapped — α-line is γ = α d_at_a, β = c_val + α d_at_b
                cd = (c_val, d_at_a, d_at_b, 'swap')
            else:
                continue
            by_ab[ab].append((sup, cd))

    print(f"# distinct (a, b) pencil structures: {len(by_ab)}")
    for ab, supports in sorted(by_ab.items()):
        print(f"  {ab}: {len(supports)} supports")

    # For most common (a, b), compute orbits
    if not by_ab:
        print("No 2-position pencils found")
        return

    most_common = max(by_ab, key=lambda k: len(by_ab[k]))
    print(f"\nMost common (a, b) = {most_common}, {len(by_ab[most_common])} supports")
    a, b = most_common
    r = a - b
    print(f"r = a - b = {r}, gcd(r, n_2) = {int(np.gcd(r, n2))}")
    print(f"orbit_size predicted = {n2 // int(np.gcd(r, n2))}")

    # Compute pure 2-mono bad ratios for this (a, b)
    print("\nComputing pure 2-mono bad ratios on L_2...")
    bad_pure = compute_bad_ratios_pure(L2, k2, a, b, p, w_J_L2, None)
    orbits_pure = compute_orbits(bad_pure, p, omega_n2, r)
    print(f"Pure 2-mono bad ratios: {len(bad_pure)} ratios in {len(orbits_pure)} orbits")
    for i, orb in enumerate(orbits_pure):
        print(f"  Orbit {i}: {sorted(orb)[:8]}")

    # Now check α-line for each support
    print(f"\nChecking α-line orbits for {len(by_ab[most_common])} arising supports:")
    multi_orbit_supports = []
    for sup, cd in by_ab[most_common]:
        if len(cd) == 4:  # swap case
            c_val, d1, d2, _ = cd
        else:
            c_val, d1, d2 = cd
        ratios = compute_alpha_line_ratios(c_val, d1, d2, p)
        # For each orbit, count how many ratios from α-line are in it
        orbit_hits = [0] * len(orbits_pure)
        for alpha, rho in ratios.items():
            for i, orb in enumerate(orbits_pure):
                if rho in orb:
                    orbit_hits[i] += 1
                    break
        n_orbits_hit = sum(1 for h in orbit_hits if h > 0)
        if n_orbits_hit > 1:
            multi_orbit_supports.append((sup, cd, orbit_hits))
        # Print sample
        if sup in by_ab[most_common][:3]:
            print(f"  sup={sup}: α-line hits orbits with counts {orbit_hits}, total hits = {sum(orbit_hits)}")

    print(f"\n# supports with α-line hitting > 1 orbit: {len(multi_orbit_supports)} of {len(by_ab[most_common])}")
    if multi_orbit_supports:
        print("CONJECTURE E REFINED FAILS for some Reverse supports!")
        for sup, cd, hits in multi_orbit_supports[:5]:
            print(f"  {sup}: orbit hits {hits}")
    else:
        print("✓ Refined Conjecture E HOLDS at toy (32, 8) for this (a, b)")


if __name__ == "__main__":
    main()
