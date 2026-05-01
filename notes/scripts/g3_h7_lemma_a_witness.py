"""Sweep primes to find G_7 mod p irreducibility witness."""
import re
import subprocess
import sympy as sp
from sympy.polys.galoistools import gf_factor
from sympy.polys.domains import ZZ

h = 7
z = sp.Symbol("z")
x = [sp.Symbol(f"x{i}") for i in range(1, h)]
X = sum(x[i - 1] * z ** i for i in range(1, h))
X2 = sp.expand(X * X)
Wc = {c: X2.coeff(z, h + c) for c in range(0, h)}
Vc = {c: X2.coeff(z, c) for c in range(0, 2 * h)}
XW = {c: sum(x[a - 1] * Wc[c - a] for a in range(1, c + 1)
             if 1 <= c - a < h) for c in range(0, h)}
WW = {c: sum(Wc[a] * Wc[c - a] for a in range(1, c)
             if 1 <= c - a < h) for c in range(0, h)}
chain = [(x[c - 1] - Wc[c]) + 3 * Vc[c] + 2 * XW[c] - WW[c]
         for c in range(1, h)]
ring_vars = ",".join(f"x{i}" for i in range(1, h))


def extract_g_at_p(p, timeout=600):
    lines = [f"ring R = {p},({ring_vars}),lp;"]
    for i, eq in enumerate(chain):
        lines.append(f"poly c{i} = {sp.sstr(sp.expand(eq))};")
    lines.append("ideal I = " + ", ".join(f"c{i}" for i in range(len(chain))) + ";")
    lines.append("ideal G = std(I);")
    lines.append('"deg f:"; deg(G[1]);')
    lines.append('"FPOL_BEGIN";')
    lines.append("string fpol_str = string(G[1]);")
    lines.append("fpol_str;")
    lines.append('"FPOL_END";')
    lines.append("$;")
    script = "\n".join(lines)
    try:
        r = subprocess.run(["Singular", "-q"], input=script.encode(),
                           capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    out = r.stdout.decode()
    in_blk = False
    parts = []
    for line in out.splitlines():
        s_line = line.strip()
        if s_line == "FPOL_BEGIN":
            in_blk = True
            continue
        if s_line == "FPOL_END":
            in_blk = False
            continue
        if in_blk:
            parts.append(s_line)
    return "".join(parts).strip()


def g_to_Gs(fpol_str, p, h):
    t = sp.Symbol(f"x{h - 1}")
    expr = sp.sympify(fpol_str)
    p_t = sp.Poly(expr, t)
    monoms = sorted(p_t.monoms())
    powers_t = [m[0] for m in monoms]
    coefs = [int(p_t.coeff_monomial(m)) % p for m in monoms]
    assert powers_t[0] == 1
    s_poly_dict = {}
    for pw, c in zip(powers_t, coefs):
        if (pw - 1) % h != 0:
            return None
        s_poly_dict[(pw - 1) // h] = c
    return s_poly_dict


def test_irred_modp(s_poly_dict, p):
    D = max(s_poly_dict.keys())
    coefs = [s_poly_dict.get(d, 0) for d in range(D, -1, -1)]
    a_n = coefs[0] % p
    if a_n == 0:
        return D, "leading drops"
    inv = pow(a_n, p - 2, p)
    monic = [(c * inv) % p for c in coefs]
    lc, factors = gf_factor(monic, p, ZZ)
    deg_pattern = sorted(d for d, _ in [(len(f) - 1, m) for f, m in factors])
    if len(factors) == 1 and factors[0][1] == 1 and len(factors[0][0]) - 1 == D:
        return D, "IRREDUCIBLE"
    return D, deg_pattern


# Sweep primes
print(f"Sweeping G_{h} mod p irreducibility witness...")
for p in [17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]:
    fpol = extract_g_at_p(p, timeout=600)
    if fpol is None:
        print(f"  p = {p}: TIMEOUT")
        continue
    s_dict = g_to_Gs(fpol, p, h)
    if s_dict is None:
        print(f"  p = {p}: G_h(s) extraction FAIL (Z/h-symmetry violated)")
        continue
    D, result = test_irred_modp(s_dict, p)
    print(f"  p = {p}: deg G_{h} = {D}, factor pattern: {result}")
    if result == "IRREDUCIBLE":
        print(f"\n  ✓✓✓ Lemma A confirmed at h = {h} via p = {p}")
        break
