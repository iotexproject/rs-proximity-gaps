"""Brute force B at (n=16, k=4, q=17) for (6, 8) and (4, 8)."""
from itertools import combinations

q, n, k = 17, 16, 4
J = n // 2
# Find primitive n-th root in F_q*
omega = None
for g in range(2, q):
    if pow(g, n, q) == 1 and pow(g, n // 2, q) != 1:
        omega = g
        break
print(f"q={q}, ω={omega}")
L_pts = [pow(omega, i, q) for i in range(n)]

def dist_le_J(values):
    """Brute force: ∃ size-J subset S such that L_n \\ S interpolates to deg < k poly."""
    for S in combinations(range(n), J):
        S_set = set(S)
        comp = [(L_pts[i], values[i]) for i in range(n) if i not in S_set]
        x_pts = [comp[j][0] for j in range(k)]
        y_pts = [comp[j][1] for j in range(k)]
        def lagrange(x_query):
            r = 0
            for j in range(k):
                num = y_pts[j]; den = 1
                for i in range(k):
                    if i != j:
                        num = (num * (x_query - x_pts[i])) % q
                        den = (den * (x_pts[j] - x_pts[i])) % q
                r = (r + num * pow(den, q - 2, q)) % q
            return r
        if all(lagrange(comp[j][0]) == comp[j][1] for j in range(k, len(comp))):
            return True
    return False

for (a, b) in [(4, 8), (6, 8)]:
    bad = []
    for rho in range(1, q):
        h = [(rho * pow(z, a, q) + pow(z, b, q)) % q for z in L_pts]
        if dist_le_J(h):
            bad.append(rho)
    print(f"(a={a}, b={b}): |B|={len(bad)}, B={bad}")
    # Verify ρ⁴ values
    fourths = sorted(set(pow(r, 4, q) for r in bad))
    print(f"   ρ⁴ values in B: {fourths}")
