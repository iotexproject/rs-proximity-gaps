"""g3_h4_p73_construct.py — directly construct E(t) at h=4, p=73, rho=26
with alpha_c = (17, 16, -1) from the y^5 elimination, and check if it
divides (1 - t^{256}) in F_73[t].

If yes: counterexample to Stage 2 (the y^5 system alone is not the full constraint, and Note 0234's empirical claim is suspect).

If no: the y^5 system is incomplete — y^6, y^7 add genuine constraints
       that exclude this Q̄-style solution.
"""
import sympy as sp

p = 73
h = 4
rho = 26
n = 8 * h  # = 32

# Stage 1 on-h-lattice E coefs (from codex E-form).
# P^(0)(y) = y^4 + rho*y^3 - (rho^3/2)*y - eps, with eps = rho^4/4.
# So E[0] = -eps, E[h]=-rho^3/2, E[2h]=0, E[3h]=rho, E[4h]=1.
rho_p = rho % p
inv2 = pow(2, p-2, p)
inv4 = pow(4, p-2, p)

eps = (rho_p**4 * inv4) % p
print(f"eps = rho^4/4 = {eps} mod {p}")

E_full_deg = 4*h
E = [0] * (E_full_deg + 1)
E[0] = (-eps) % p
E[h] = (-pow(rho_p, 3, p) * inv2) % p
E[2*h] = 0
E[3*h] = rho_p
E[4*h] = 1
print(f"On-h-lattice E coefs: E[0]={E[0]}, E[{h}]={E[h]}, E[{2*h}]={E[2*h]}, E[{3*h}]={E[3*h]}, E[{4*h}]={E[4*h]}")

# Hypothesis: E[a]=0, E[h+a]=0 for a in [1, h-1].
# These are already 0 in our list.

# Off-block:
# alpha_c := E[2h+c], beta_c := E[3h+c]
# Universal y^4 reduction: beta_c = (3*rho/2)*alpha_c - Q_alpha(c)/(2*rho)
# where Q_alpha(c) = sum_{a+b=c, 1<=a,b<=c-1} alpha_a * alpha_{c-a}.
# With alpha = (alpha_1, alpha_2, alpha_3) and Q_alpha(c):
#   Q_alpha(1) = 0  (no a+b=1 with a,b >= 1)
#   Q_alpha(2) = alpha_1 * alpha_1 = alpha_1^2
#   Q_alpha(3) = alpha_1*alpha_2 + alpha_2*alpha_1 = 2*alpha_1*alpha_2

alpha_vals = [0, 17, 16, -1]  # alpha_c for c=0..3 (c=0 unused)
alpha_vals = [v % p for v in alpha_vals]
alpha_1, alpha_2, alpha_3 = alpha_vals[1], alpha_vals[2], alpha_vals[3]

Q_alpha = {1: 0, 2: pow(alpha_1, 2, p), 3: (2 * alpha_1 * alpha_2) % p}

inv_rho = pow(rho_p, p-2, p)
inv_2rho = (inv2 * inv_rho) % p

three_rho_half = (3 * rho_p * inv2) % p

beta = [0] * h
for c in range(1, h):
    a_c = alpha_vals[c]
    Qc = Q_alpha[c]
    beta_c = (three_rho_half * a_c - Qc * inv_2rho) % p
    beta[c] = beta_c
    E[2*h + c] = a_c
    E[3*h + c] = beta_c

print(f"\nalpha = ({alpha_1}, {alpha_2}, {alpha_3})")
print(f"beta  = ({beta[1]}, {beta[2]}, {beta[3]})")

print(f"\nFull E coefs (degree {len(E)-1}):")
for d, ed in enumerate(E):
    if ed != 0 or d in {0, h, 2*h, 3*h, 4*h}:
        print(f"  E[{d}] = {ed}")

# Now construct E as sympy polynomial in F_p[t]
t = sp.Symbol("t")
E_poly = sum(coef * t**d for d, coef in enumerate(E))

# Check divisibility: does E divide (1 - t^{8h}) = (1 - t^32) in F_p[t]?
target = sp.Poly(1 - t**(8*h), t, modulus=p)
E_sympoly = sp.Poly(E_poly, t, modulus=p)

print(f"\nE_poly degree: {E_sympoly.degree()}")
print(f"Target (1 - t^{8*h}) degree: {target.degree()}")

q, r = sp.div(target, E_sympoly, t, modulus=p)
print(f"\nDivision: deg(quotient) = {sp.Poly(q, t, modulus=p).degree() if q != 0 else -1}")
print(f"Remainder = {r}")

if r == 0:
    print("\n*** E DIVIDES (1 - t^{8h}) in F_73[t] ***")
    print("This is a NON-TRIVIAL Stage 2 solution — counterexample to char-uniform claim.")
else:
    print("\nE does NOT divide (1 - t^{8h}).")
    print("Means y^6, y^7 equations are violated; my elimination was incomplete.")
    print("Stage 2 char-uniform may still hold.")
