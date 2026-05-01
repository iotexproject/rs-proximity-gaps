"""Debug the mismatch in op1a_algorithm.py."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from op1a_algorithm import (
    M_oracle, berlekamp_massey, is_L_rooted, poly_pow_mod, poly_sub, poly_divmod2
)
from op2_curve_measure_prefactor import (
    small_field_subgroup, vandermonde, count_M, precompute_E_kernels, in_V_E
)

p = 41
n = 10
c = 3
D = 7
w = 4
T = 4
s1 = [36, 34, 13, 7, 39, 17, 35]
s2 = [36, 13, 36, 18, 36, 17, 35]

L = small_field_subgroup(p, n)
print(f"L = {L}")
all_kers = precompute_E_kernels(L, p, D, w)
print(f"|kers| = {len(all_kers)}")

# Find which γ and which E gives x_γ ∈ V_E.
from itertools import combinations
n_pts = len(L)
E_list = list(combinations(range(n_pts), w))

print("\n--- Brute-force find: γ, E s.t. x_γ ∈ V_E ---")
hits = []
for gamma in range(1, p):
    x = [(s1[j] + gamma * s2[j]) % p for j in range(D)]
    for idx, E in enumerate(E_list):
        ker = all_kers[idx]
        if in_V_E(x, ker, p):
            hits.append((gamma, E, x))
            print(f"  γ={gamma:3d}: x_γ ∈ V_E with E={E} (L_E = {[L[v] for v in E]})")
print(f"Total hits: {len(hits)}")
print()

# For each γ in hits, check what BM says.
print("--- BM analysis on hit γ's ---")
for (gamma, E, x) in hits:
    Q_char, ell = berlekamp_massey(x, p)
    print(f"  γ={gamma}: x={x}")
    print(f"    BM: characteristic poly Q={Q_char}, deg L={ell}")
    print(f"    L_E (expected roots) = {[L[v] for v in E]}")
    # Check if Q evaluates to 0 at each L_v of E
    for v in E:
        Lv = L[v]
        val = sum((Q_char[i] * pow(Lv, i, p)) % p for i in range(len(Q_char))) % p
        print(f"    Q({Lv}) = {val}")
    # Check L-rooted via X^n mod Q
    if Q_char and len(Q_char) > 1:
        Xn_mod = poly_pow_mod([0, 1], n, Q_char, p)
        diff = poly_sub(Xn_mod, [1], p)
        print(f"    X^n mod Q = {Xn_mod}, X^n mod Q - 1 = {diff}")
        print(f"    is L-rooted? {is_L_rooted(Q_char, L, p)}")
    print()

print("--- Re-run M_oracle and trace failures ---")
M = M_oracle(s1, s2, p, D, w, L)
print(f"M_oracle = {M}")
