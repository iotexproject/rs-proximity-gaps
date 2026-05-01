"""
intersection_structure.py — Deep structure of r_i polynomials.

Key findings to explore:
1. r₁ = σ_w · h₁ — what is h₁? Is it related to dr₀/dσ₁?
2. What about r₂, r₃, ...? Do they also have σ_w factors?
3. The identity: (r₀-1) + r₁ζ + r₂ζ² + ... + r_{w-1}ζ^{w-1} = 0
   for any root ζ of Λ with ζ^n = 1.
   At r₀=1: r₁ζ + r₂ζ² + ... = 0, so r₁ = -(r₂ζ + ... + r_{w-1}ζ^{w-2}).
   This is w-2 degree in ζ → at most w-2 roots ζ satisfy this.
4. Relation between r₁ and ∂r₀/∂σ₁ (formal derivative).
"""

from math import gcd

# ---- Z-polynomial arithmetic (bivariate σ₁, σ_w) ----
def zpoly_zero(): return {}
def zpoly_const(c):
    if c == 0: return {}
    return {(0,0): c}
def zpoly_var(idx):
    key = [0, 0]; key[idx] = 1
    return {tuple(key): 1}
def zpoly_add(f, g):
    r = dict(f)
    for k, v in g.items():
        r[k] = r.get(k, 0) + v
        if r[k] == 0: del r[k]
    return r
def zpoly_sub(f, g):
    r = dict(f)
    for k, v in g.items():
        r[k] = r.get(k, 0) - v
        if r[k] == 0: del r[k]
    return r
def zpoly_mul(f, g):
    r = {}
    for (a1,b1),c1 in f.items():
        for (a2,b2),c2 in g.items():
            key = (a1+a2, b1+b2)
            r[key] = r.get(key,0) + c1*c2
            if r[key] == 0: del r[key]
    return r
def zpoly_scale(f, c):
    if c == 0: return {}
    return {k: v*c for k,v in f.items() if v*c != 0}
def zpoly_degree(f):
    if not f: return -1
    return max(a+b for a,b in f.keys())

def compute_all_ri_bivariate_Z(n, w):
    eps = (-1)**(w+1)
    sigma1 = zpoly_var(0)
    sigmaw = zpoly_var(1)
    c_polys = [zpoly_zero() for _ in range(w)]
    c_polys[0] = zpoly_scale(sigmaw, eps)
    c_polys[w-1] = sigma1
    state = [zpoly_zero() for _ in range(w)]
    state[0] = zpoly_const(1)
    for step in range(n):
        top = state[w-1]
        new_state = [None]*w
        new_state[0] = zpoly_mul(top, c_polys[0])
        for j in range(1, w):
            new_state[j] = zpoly_add(state[j-1], zpoly_mul(top, c_polys[j]))
        state = new_state
    return state

def zpoly_div_sw(f):
    """Divide polynomial by σ_w. Returns (quotient, success)."""
    q = {}
    for (a, b), c in f.items():
        if b == 0:
            return None, False  # not divisible
        q[(a, b-1)] = c
    return q, True

def zpoly_deriv_s1(f):
    """∂f/∂σ₁ over Z."""
    r = {}
    for (a, b), c in f.items():
        if a > 0:
            key = (a-1, b)
            r[key] = r.get(key, 0) + a * c
            if r[key] == 0: del r[key]
    return r

def zpoly_deriv_sw(f):
    """∂f/∂σ_w over Z."""
    r = {}
    for (a, b), c in f.items():
        if b > 0:
            key = (a, b-1)
            r[key] = r.get(key, 0) + b * c
            if r[key] == 0: del r[key]
    return r

def print_zpoly(f, name="f"):
    if not f:
        print(f"  {name} = 0")
        return
    items = sorted(f.items(), key=lambda x: (-sum(x[0]), x[0]))
    parts = []
    for (a,b), c in items:
        vp = []
        if a > 0: vp.append(f"s1^{a}" if a > 1 else "s1")
        if b > 0: vp.append(f"sw^{b}" if b > 1 else "sw")
        vs = "*".join(vp) if vp else "1"
        if c == 1 and vp: parts.append(f"+{vs}")
        elif c == -1 and vp: parts.append(f"-{vs}")
        elif c > 0: parts.append(f"+{c}*{vs}")
        else: parts.append(f"{c}*{vs}")
    s = " ".join(parts)
    if s.startswith("+"): s = s[1:]
    print(f"  {name} = {s}")

print("="*70)
print("STRUCTURAL ANALYSIS OF r_i POLYNOMIALS")
print("="*70)

for w in [3, 4, 5]:
    for n in range(w+2, min(w+14, 22), 2):
        print(f"\n{'='*60}")
        print(f"n={n}, w={w}")
        print(f"{'='*60}")

        r_all = compute_all_ri_bivariate_Z(n, w)
        r0m1 = zpoly_sub(r_all[0], zpoly_const(1))

        # Check σ_w divisibility of each r_i
        for i in range(w):
            q, ok = zpoly_div_sw(r_all[i])
            label = f"r_{i}" if i > 0 else "r₀"
            if ok:
                print(f"  {label}: σ_w | r_{i} ✓  (h_{i} = r_{i}/σ_w has deg {zpoly_degree(q)})")
            else:
                has_const = any(b == 0 for (a,b) in r_all[i].keys())
                print(f"  {label}: σ_w ∤ r_{i}  (has σ_w-free terms: {has_const})")

        # Check relation r₁ vs ∂r₀/∂σ₁
        dr0_ds1 = zpoly_deriv_s1(r_all[0])
        print(f"\n  ∂r₀/∂σ₁:")
        print_zpoly(dr0_ds1, "∂r₀/∂σ₁")
        print_zpoly(r_all[1], "r₁")

        # Check if r₁ = c · ∂r₀/∂σ₁ for some constant
        if r_all[1] and dr0_ds1:
            # Compare term by term
            ratios = []
            for key in r_all[1]:
                if key in dr0_ds1 and dr0_ds1[key] != 0:
                    ratios.append((key, r_all[1][key], dr0_ds1[key], r_all[1][key] / dr0_ds1[key]))
            if ratios:
                r_vals = [r[3] for r in ratios]
                if len(set(r_vals)) == 1:
                    print(f"  r₁ = {r_vals[0]} · ∂r₀/∂σ₁  *** PROPORTIONAL ***")
                else:
                    print(f"  r₁ / (∂r₀/∂σ₁) ratios: {[(k, f'{r:.4f}') for k,_,_,r in ratios]}")

        # Check relation r₁ vs ∂r₀/∂σ_w
        dr0_dsw = zpoly_deriv_sw(r_all[0])

        # Check weighted Euler relation: Σ j·σ_j · ∂r₀/∂σ_j = n·r₀
        # In bivariate: 1·σ₁·∂r₀/∂σ₁ + w·σ_w·∂r₀/∂σ_w = n·r₀
        # So: σ₁·∂r₀/∂σ₁ + w·σ_w·∂r₀/∂σ_w = n·r₀
        euler_lhs = zpoly_add(
            zpoly_mul(zpoly_var(0), dr0_ds1),
            zpoly_scale(zpoly_mul(zpoly_var(1), dr0_dsw), w)
        )
        euler_rhs = zpoly_scale(r_all[0], n)
        euler_diff = zpoly_sub(euler_lhs, euler_rhs)
        if not euler_diff:
            print(f"\n  Euler relation: σ₁·∂r₀/∂σ₁ + {w}·σ_w·∂r₀/∂σ_w = {n}·r₀  ✓ VERIFIED")
        else:
            print(f"\n  Euler relation FAILED, diff has {len(euler_diff)} terms")

        # Now check: is r₁ related to ∂r₀/∂σ₁ or ∂r₀/∂σ_w via the recurrence?
        # The companion matrix identity:
        # x^n = r₀ + r₁·x + ... + r_{w-1}·x^{w-1} mod Λ(x)
        # Differentiating w.r.t. σ₁: ∂r₀/∂σ₁ + (∂r₁/∂σ₁)x + ... = ∂/∂σ₁[x^n mod Λ]
        # The RHS involves: -∂Λ/∂σ₁ = x^{w-1}, so there's a correction term.

        # Actually the key relation comes from:
        # d/dσ₁ [x^n mod Λ(x)] = [d/dσ₁ of (remainder)] + [correction from changing Λ]
        # The correction is: Q(x) · ∂Λ/∂σ₁ where Q(x) = (x^n - R(x))/Λ(x)
        # ∂Λ/∂σ₁ = -x^{w-1}
        # So: d/dσ₁[R(x)] = -Q(x)·x^{w-1} mod Λ(x)

        # R(x) = r₀ + r₁x + ... + r_{w-1}x^{w-1}
        # d/dσ₁[R(x)] = (∂r₀/∂σ₁) + (∂r₁/∂σ₁)x + ...
        # And -Q(x)·x^{w-1} mod Λ(x) involves the quotient Q.

        # Check gcd of r₀-1 and r₁
        # Over Z, can check if they share a common factor by looking at resultant structure
        # But for now, check if h₁ = r₁/σ_w and r₀-1 share a factor

        h1, ok1 = zpoly_div_sw(r_all[1])
        if ok1 and h1:
            # Check: is h₁ proportional to (r₀-1)/σ_w at some specialization?
            # r₀-1 has a constant term -1, so σ_w ∤ (r₀-1).
            # Check: gcd(r₀-1, h₁) via evaluation at specific points
            pass

print("\n" + "="*70)
print("FACTORIZATION PATTERN: r_i = σ_w^{a_i} · h_i")
print("="*70)

for w in [3, 4, 5]:
    for n in range(w+2, min(w+10, 20), 2):
        r_all = compute_all_ri_bivariate_Z(n, w)
        factors = []
        for i in range(w):
            f = r_all[i]
            sw_power = 0
            while True:
                q, ok = zpoly_div_sw(f)
                if not ok:
                    break
                f = q
                sw_power += 1
            factors.append(sw_power)
        print(f"  n={n}, w={w}: r_i divisible by σ_w^a: a = {factors}")
        # Also check weighted degrees of h_i = r_i / σ_w^{a_i}
        wt_degs = []
        for i in range(w):
            f = r_all[i]
            for _ in range(factors[i]):
                f, _ = zpoly_div_sw(f)
            if f:
                wt = max(a + w*b for (a,b) in f.keys())
            else:
                wt = -1
            wt_degs.append(wt)
        print(f"         weighted degrees of h_i: {wt_degs}")

print("\n" + "="*70)
print("DERIVATIVE RELATION: r₁ vs (1/n)·∂r₀/∂σ₁")
print("="*70)

for w in [3]:
    for n in range(w+2, w+16, 2):
        r_all = compute_all_ri_bivariate_Z(n, w)
        dr0 = zpoly_deriv_s1(r_all[0])
        r1 = r_all[1]

        # For each term in r₁, compute ratio with corresponding term in ∂r₀/∂σ₁
        if r1 and dr0:
            ratios = {}
            for key in r1:
                if key in dr0 and dr0[key] != 0:
                    ratios[key] = (r1[key], dr0[key])

            print(f"\n  n={n}, w={w}:")
            for key, (r1c, drc) in sorted(ratios.items()):
                print(f"    {key}: r₁={r1c}, ∂r₀/∂σ₁={drc}, ratio={r1c/drc:.6f}")
