"""g3_lemma_b_qc_vs_gh.py — Lemma B: G_h ∤ Q_c in F[s] for c ∈ {h-2, h-1}.

For each h, restrict E_c (c=h-1, h-2) to V(chain) parametrized by t=x_{h-1}.
Result is t^{2h-c} · Q_c(t^h). Read off Q_c(s) and test G_h | Q_c.

Lemma B says: NO. Equivalently, gcd(Q_c, G_h) = 1 in F[s] (using G_h irreducible).
"""
from __future__ import annotations
import argparse
import re
import subprocess
from typing import List, Tuple

import sympy as sp


def gen_singular_qc_extract(h: int) -> str:
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
    # E_c = 14 V_c - 3 [z^c] U^2 where U = X - W
    U_sq = {c: Vc[c] - 2 * XW[c] + WW[c] for c in range(0, h)}
    endpts = {}
    for c in [h - 2, h - 1]:
        endpts[c] = sp.expand(14 * Vc[c] - 3 * U_sq[c])

    last_var = f"x{h - 1}"
    ring_vars = ",".join(f"x{i}" for i in range(1, h))
    lines = [f"ring R = 0,({ring_vars}),lp;"]
    for i, eq in enumerate(chain):
        lines.append(f"poly c{i} = {sp.sstr(sp.expand(eq))};")
    for c in [h - 2, h - 1]:
        lines.append(f"poly e{c} = {sp.sstr(endpts[c])};")
    lines.append("ideal I = " + ", ".join(f"c{i}" for i in range(len(chain))) + ";")
    lines.append("ideal G = std(I);")
    lines.append("poly fpol = G[1];")
    lines.append('"deg f:"; deg(fpol);')
    lines.append('"FPOL_BEGIN";')
    lines.append("string fpol_str = string(fpol);")
    lines.append("fpol_str;")
    lines.append('"FPOL_END";')
    for c in [h - 2, h - 1]:
        lines.append(f"poly r{c} = reduce(e{c}, G);")
        lines.append(f'"deg r{c}:"; deg(r{c});')
        lines.append(f'"R{c}_BEGIN";')
        lines.append(f"string r{c}_str = string(r{c});")
        lines.append(f"r{c}_str;")
        lines.append(f'"R{c}_END";')
    lines.append("$;")
    return "\n".join(lines)


def parse_block(out: str, marker_begin: str, marker_end: str) -> str:
    in_blk = False
    parts: List[str] = []
    for line in out.splitlines():
        s = line.strip()
        if s == marker_begin:
            in_blk = True
            continue
        if s == marker_end:
            in_blk = False
            continue
        if in_blk:
            parts.append(s)
    return "".join(parts).strip()


def parse_deg(out: str, label: str) -> int:
    lines = out.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == f"{label}:" and i + 1 < len(lines):
            try:
                return int(lines[i + 1].strip())
            except ValueError:
                continue
    return -1


def to_univariate(poly_str: str, h: int) -> sp.Expr:
    last_var = sp.Symbol(f"x{h - 1}")
    locals_map = {f"x{j}": sp.Symbol(f"x{j}") for j in range(1, h)}
    expr = sp.sympify(poly_str, locals=locals_map)
    other_vars = [sp.Symbol(f"x{j}") for j in range(1, h - 1)]
    if any(v in expr.free_symbols for v in other_vars):
        return expr  # GB didn't fully triangulate (signal of problem)
    return sp.Poly(expr, last_var)


def t_poly_to_q_in_s(t_poly_str: str, h: int, c_endpoint: int) -> Tuple[sp.Poly, int]:
    """t-polynomial r_c(t) = t^{2h-c} * Q_c(t^h). Return Q_c(s), shift."""
    last_var = sp.Symbol(f"x{h - 1}")
    locals_map = {f"x{j}": sp.Symbol(f"x{j}") for j in range(1, h)}
    expr = sp.sympify(t_poly_str, locals=locals_map)
    other_vars = [sp.Symbol(f"x{j}") for j in range(1, h - 1)]
    if any(v in expr.free_symbols for v in other_vars):
        raise ValueError("Not univariate after reduction; GB not triangular?")
    p_t = sp.Poly(expr, last_var)
    if p_t.is_zero:
        return sp.Poly(0, sp.Symbol("s")), 0
    monoms = sorted(p_t.monoms())
    powers_t = [m[0] for m in monoms]
    coefs = [p_t.coeff_monomial(m) for m in monoms]
    min_pow = powers_t[0]
    # Verify all powers ≡ min_pow (mod h) — Z/h-symmetry
    for pw in powers_t:
        if (pw - min_pow) % h != 0:
            raise ValueError(f"Z/h-symmetry violated: powers {powers_t}")
    s = sp.Symbol("s")
    s_poly = sum(c * s ** ((pw - min_pow) // h) for pw, c in zip(powers_t, coefs))
    return sp.Poly(s_poly, s), min_pow


def gh_from_fpol(fpol_str: str, h: int) -> sp.Poly:
    """f(t) = t · g_h(t). Return g_h as poly in s = t^h."""
    last_var = sp.Symbol(f"x{h - 1}")
    locals_map = {f"x{j}": sp.Symbol(f"x{j}") for j in range(1, h)}
    expr = sp.sympify(fpol_str, locals=locals_map)
    p_t = sp.Poly(expr, last_var)
    monoms = sorted(p_t.monoms())
    powers_t = [m[0] for m in monoms]
    coefs = [p_t.coeff_monomial(m) for m in monoms]
    # Lowest power should be 1 (the t factor); strip it
    assert powers_t[0] == 1, f"Expected lowest power 1, got {powers_t[0]}"
    s = sp.Symbol("s")
    s_poly = sum(c * s ** ((pw - 1) // h) for pw, c in zip(powers_t, coefs))
    return sp.Poly(s_poly, s)


def analyze_h(h: int, timeout: int = 1200) -> None:
    print(f"\n========== Lemma B at h = {h} ==========")
    script = gen_singular_qc_extract(h)
    try:
        r = subprocess.run(["Singular", "-q"], input=script.encode(),
                           capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT after {timeout}s")
        return
    out = r.stdout.decode()
    fpol_str = parse_block(out, "FPOL_BEGIN", "FPOL_END")
    G_h = gh_from_fpol(fpol_str, h)
    print(f"  G_h(s) deg = {G_h.degree()}, leading = {G_h.LC()}")

    s = sp.Symbol("s")
    Q_polys = {}
    for c in [h - 2, h - 1]:
        r_str = parse_block(out, f"R{c}_BEGIN", f"R{c}_END")
        if not r_str or r_str == "0":
            print(f"  E_{c}|(t) = 0 ⟹ E_{c} ∈ I_chain. Lemma B trivially fails for this c.")
            continue
        try:
            Q_c, shift = t_poly_to_q_in_s(r_str, h, c)
            print(f"  E_{c}|(t) → t^{shift} · Q_{c}(s), deg Q_{c} = {Q_c.degree()}")
            # Clear denominators
            den_lcm = sp.lcm([sp.fraction(c)[1] for c in Q_c.all_coeffs()])
            Q_c_int = Q_c * den_lcm
            print(f"    deg Q_{c} = {Q_c.degree()} < deg G_h = {G_h.degree()}: Lemma B holds over Q (irreducible G_h)")
            # Compute resultant — bad primes where gcd(Q_c, G_h) > 1 mod p
            try:
                R = sp.resultant(Q_c_int, G_h, s)
                R_int = sp.Integer(R)
                print(f"    Res(Q_{c}, G_h) = {R_int}")
                print(f"    Res factored: {sp.factorint(abs(R_int)) if R_int != 0 else 'ZERO!'}")
                # Bad denominator (where Q_c reduction fails)
                print(f"    den lcm of Q_{c}: {sp.factorint(int(den_lcm)) if den_lcm != 1 else '{}'}")
            except Exception as e:
                print(f"    Resultant error: {e}")
            Q_polys[c] = (Q_c, Q_c_int, den_lcm)
        except Exception as e:
            print(f"  E_{c}: parse error: {e}")
    # Compute the joint bad set: gcd(Res(Q_{h-1}), Res(Q_{h-2}))
    if len(Q_polys) == 2:
        c1, c2 = h - 1, h - 2
        if c1 in Q_polys and c2 in Q_polys:
            R1 = sp.resultant(Q_polys[c1][1], G_h, s)
            R2 = sp.resultant(Q_polys[c2][1], G_h, s)
            joint = sp.gcd(R1, R2)
            print(f"\n  Joint bad-primes set (gcd of resultants): {joint}")
            if joint != 0:
                print(f"    Factored: {sp.factorint(abs(int(joint)))}")
            # Also include leading coefficient of G_h
            lc_factors = sp.factorint(abs(int(G_h.LC())))
            print(f"  Leading G_h factored: {lc_factors}")
            # Bad set = primes dividing joint OR primes dividing leading
            joint_primes = set(sp.factorint(abs(int(joint))).keys()) if joint != 0 else set()
            lc_primes = set(lc_factors.keys())
            bad_set = joint_primes | lc_primes
            print(f"  N_B(h) ⊆ {sorted(bad_set)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h-list", default="5,6")
    parser.add_argument("--timeout", type=int, default=1200)
    args = parser.parse_args()
    for h_str in args.h_list.split(","):
        h = int(h_str)
        analyze_h(h, timeout=args.timeout)


if __name__ == "__main__":
    main()
