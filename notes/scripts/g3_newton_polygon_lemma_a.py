"""g3_newton_polygon_lemma_a.py — Newton polygon analysis for Lemma A.

For each h, extract G_h(s) coefficients from Singular LEX GB of the chain
ideal, then for each prime p compute v_p of all coefficients to find a
prime witnessing irreducibility via Newton polygon.

Lemma A target: G_h(s) is irreducible over Q. Strategy: find p_h such
that the Newton polygon of G_h at p_h is a SINGLE segment, forcing a
deg(G_h)-cycle in the Galois group → transitive → irreducible.

Single-segment condition: v_p(constant) > 0 and v_p(other) = 0.
Then segment has slope -v_p(const)/D and length D. For "5-cycle" type
forcing, we need slope-denominator coprime to 1 and segment length = D.
"""
from __future__ import annotations
import argparse
import re
import subprocess
from math import gcd
from typing import List, Tuple

import sympy as sp


def gen_singular_extract_g(h: int) -> str:
    """Build Singular script that prints g_h(t) = f(t)/t coefficients in t."""
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

    last_var = f"x{h - 1}"
    ring_vars = ",".join(f"x{i}" for i in range(1, h))
    lines = [f"ring R = 0,({ring_vars}),lp;"]
    for i, eq in enumerate(chain):
        lines.append(f"poly c{i} = {sp.sstr(sp.expand(eq))};")
    lines.append("ideal I = " + ", ".join(f"c{i}" for i in range(len(chain))) + ";")
    lines.append("ideal G = std(I);")
    lines.append("poly fpol = G[1];")
    lines.append('"deg f:"; deg(fpol);')
    lines.append(f"poly gpol = fpol/{last_var};")
    lines.append('"deg g:"; deg(gpol);')
    lines.append('"=== g_h polynomial (in last_var) ===";')
    lines.append('"GPOL_BEGIN";')
    lines.append("string gpol_str = string(gpol);")
    lines.append("gpol_str;")
    lines.append('"GPOL_END";')
    lines.append("$;")
    return "\n".join(lines)


def parse_g_coeffs(out: str, h: int) -> Tuple[int, dict]:
    """Parse Singular output: get deg_g and gpol string, parse via sympy."""
    deg_g = None
    gpol_str = None
    lines = out.splitlines()
    in_gpol = False
    gpol_lines: List[str] = []
    for i, line in enumerate(lines):
        if line.strip() == 'deg g:' and i + 1 < len(lines):
            try:
                deg_g = int(lines[i + 1].strip())
            except ValueError:
                pass
        if line.strip() == "GPOL_BEGIN":
            in_gpol = True
            continue
        if line.strip() == "GPOL_END":
            in_gpol = False
            continue
        if in_gpol:
            gpol_lines.append(line.strip())
    gpol_str = "".join(gpol_lines).strip()
    if not gpol_str:
        return deg_g, {}
    last_var = sp.Symbol(f"x{h - 1}")
    other_vars = [sp.Symbol(f"x{j}") for j in range(1, h - 1)]
    locals_map = {f"x{j}": sp.Symbol(f"x{j}") for j in range(1, h)}
    gpol = sp.sympify(gpol_str, locals=locals_map)
    poly = sp.Poly(gpol, last_var)
    coefs_t: dict = {}
    for (deg_tuple, c) in poly.terms():
        d = deg_tuple[0]
        # c may still depend on other_vars — that would mean GB didn't fully
        # triangulate. Sanity-check.
        if other_vars and any(s in c.free_symbols for s in other_vars):
            coefs_t[d] = c
        else:
            coefs_t[d] = sp.Integer(int(c))
    return deg_g, coefs_t


def t_coeffs_to_s_coeffs(coefs_t: dict, h: int) -> dict:
    """g(t) = G(s) where s = t^h. Coefficients in t at powers k·h."""
    coefs_s = {}
    for power_t, c in coefs_t.items():
        if isinstance(c, sp.Basic) and c == 0:
            continue
        if power_t % h != 0:
            # Should be zero by Z/h-symmetry
            if c != 0:
                print(f"  WARN: nonzero coef at non-multiple t^{power_t} = {c}")
            continue
        coefs_s[power_t // h] = c
    return coefs_s


def newton_polygon_at_p(coefs_s: dict, p: int) -> List[Tuple[int, int]]:
    """Return list of (degree, v_p(coef)) sorted by degree."""
    pts = []
    for d, c in coefs_s.items():
        if c == 0:
            continue
        v = 0
        cc = abs(int(c))
        while cc % p == 0:
            cc //= p
            v += 1
        pts.append((d, v))
    return sorted(pts)


def find_witness_prime(coefs_s: dict, prime_pool: List[int]) -> List[Tuple[int, int]]:
    """Find primes where v_p(constant) > 0 and v_p(others) = 0."""
    if 0 not in coefs_s or coefs_s[0] == 0:
        return []
    const = abs(int(coefs_s[0]))
    witnesses = []
    for p in prime_pool:
        if const % p != 0:
            continue
        # constant divisible by p — check others NOT divisible
        ok = True
        for d, c in coefs_s.items():
            if d == 0:
                continue
            if int(c) % p == 0:
                ok = False
                break
        if not ok:
            continue
        v_const = 0
        cc = const
        while cc % p == 0:
            cc //= p
            v_const += 1
        witnesses.append((p, v_const))
    return witnesses


def factor_mod_p(coefs_s: dict, D: int, p: int):
    """Factor G_h(s) modulo p. Return list of (degree, multiplicity)."""
    from sympy.polys.galoistools import gf_factor
    from sympy.polys.domains import ZZ
    coefs_high_to_low = [int(coefs_s.get(d, 0)) for d in range(D, -1, -1)]
    a_n = coefs_high_to_low[0] % p
    if a_n == 0:
        return None
    inv = pow(a_n, p - 2, p)
    coefs_monic = [(c * inv) % p for c in coefs_high_to_low]
    lc, factors = gf_factor(coefs_monic, p, ZZ)
    return [(len(f) - 1, m) for f, m in factors]


def find_irreducibility_witness(coefs_s: dict, D: int,
                                prime_pool: List[int],
                                max_witnesses: int = 5) -> List[int]:
    """Find primes p where G_h mod p is irreducible (single deg-D factor)."""
    found = []
    for p in prime_pool:
        result = factor_mod_p(coefs_s, D, p)
        if result is None:
            continue
        if len(result) == 1 and result[0][0] == D and result[0][1] == 1:
            found.append(p)
            if len(found) >= max_witnesses:
                break
    return found


def cycle_pattern_distribution(coefs_s: dict, D: int,
                               prime_pool: List[int]) -> dict:
    """For each prime, find cycle pattern (factorization). Aggregate."""
    counts: dict = {}
    for p in prime_pool:
        result = factor_mod_p(coefs_s, D, p)
        if result is None:
            continue
        squarefree = all(m == 1 for _, m in result)
        if not squarefree:
            continue
        degs = tuple(sorted(d for d, _ in result))
        counts[degs] = counts.get(degs, 0) + 1
    return counts


def analyze_h(h: int, timeout: int = 1200) -> None:
    print(f"\n========== h = {h} ==========")
    script = gen_singular_extract_g(h)
    try:
        r = subprocess.run(["Singular", "-q"], input=script.encode(),
                           capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT after {timeout}s")
        return
    out = r.stdout.decode()
    deg_g, coefs_t = parse_g_coeffs(out, h)
    print(f"  deg g_h(t) = {deg_g}")
    if deg_g is None:
        print("  Failed to parse deg_g")
        print(out[-2000:])
        return
    coefs_s = t_coeffs_to_s_coeffs(coefs_t, h)
    D = max(coefs_s.keys()) if coefs_s else None
    print(f"  deg G_h(s) = D = {D}")
    print(f"  G_h(s) coefficients (highest to lowest):")
    for d in sorted(coefs_s.keys(), reverse=True):
        c = coefs_s[d]
        # Try to factor for human-readable form
        try:
            factored = sp.factorint(abs(int(c)))
            sign = "-" if int(c) < 0 else ""
            fstr = " · ".join([f"{p}^{e}" if e > 1 else str(p)
                               for p, e in sorted(factored.items())])
            print(f"    s^{d}: {c}    [{sign}{fstr}]")
        except Exception:
            print(f"    s^{d}: {c}")

    # Newton polygon witness search
    prime_pool = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                  53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107,
                  109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167,
                  173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
                  233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283,
                  293, 307, 311, 313, 317]
    witnesses_np = find_witness_prime(coefs_s, prime_pool)
    if witnesses_np:
        print(f"  Newton polygon witness primes (single-segment shape):")
        for p, v in witnesses_np[:5]:
            slope_num, slope_denom = v, D
            g = gcd(slope_num, slope_denom)
            slope_red = (slope_num // g, slope_denom // g)
            print(f"    p = {p}: v_p(const) = {v}, "
                  f"slope = -{v}/{D} = -{slope_red[0]}/{slope_red[1]}")

    # Mod-p irreducibility witnesses (the REAL Lemma A approach)
    witnesses_irred = find_irreducibility_witness(coefs_s, D, prime_pool)
    if witnesses_irred:
        print(f"  ✓ MOD-P IRREDUCIBILITY WITNESSES (Lemma A confirmed):")
        for p in witnesses_irred:
            print(f"    p = {p}: G_h mod p is irreducible (single deg-{D} factor)")
    else:
        print(f"  ✗ NO mod-p irreducibility witness found in primes ≤ {prime_pool[-1]}")

    # Cycle pattern distribution (Chebotarev-style fingerprint of Galois group)
    cycle_dist = cycle_pattern_distribution(coefs_s, D, prime_pool)
    print(f"  Cycle pattern distribution (Frobenius classes, squarefree only):")
    for pattern, count in sorted(cycle_dist.items(), key=lambda kv: -kv[1])[:10]:
        print(f"    {pattern}: {count} primes")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h-list", default="4,5,6,7")
    parser.add_argument("--timeout", type=int, default=1200)
    args = parser.parse_args()
    for h_str in args.h_list.split(","):
        h = int(h_str)
        analyze_h(h, timeout=args.timeout)


if __name__ == "__main__":
    main()
