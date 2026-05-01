"""g3_stage2_alpha_only.py — Build Stage 2 system at h with universal y^4 reduction
applied (β_c eliminated), so unknowns are JUST α_c for c ∈ [1, h-1].

This is the smallest possible system. Variables: h-1 unknowns. Equations: typically
3(h-1) (y^5, y^6, y^7 of each residue, after eliminating β via y^4 relation).
"""
import argparse
import sys
import sympy as sp

sys.path.insert(0, "notes/scripts")
from g3_stage2_full_correct import stage2_system


def alpha_only_system(h):
    eqs, alpha, beta, rho_sym, eps_sym = stage2_system(h)
    eps_val = rho_sym**4 / 4

    # Universal y^4 reduction: β_c = (3ρ/2)α_c - Q_α(c)/(2ρ) where
    # Q_α(c) = sum_{a+b=c, 1<=a,b<=c-1} α_a α_{c-a}.
    inv2 = sp.Rational(1, 2)
    inv2rho = inv2 / rho_sym
    three_rho_half = sp.Rational(3) * rho_sym / 2

    Q_alpha = {}
    for c in range(1, h):
        s = sp.Integer(0)
        for a in range(1, c):
            b = c - a
            if 1 <= b < c:
                s += alpha[a-1] * alpha[b-1]
        Q_alpha[c] = sp.expand(s)

    beta_subs = {beta[c-1]: sp.expand(three_rho_half * alpha[c-1] - Q_alpha[c] * inv2rho)
                 for c in range(1, h)}

    eqs_sub = []
    for c, k, e in eqs:
        e1 = e.subs(eps_sym, eps_val)
        e1 = sp.expand(e1.subs(beta_subs))
        # Drop equations that are now identically zero (e.g., y^4 identity itself)
        if e1 != 0:
            eqs_sub.append((c, k, e1))
    return eqs_sub, alpha, rho_sym


def emit_singular(h, mode="symbolic", prime=None, output=None):
    eqs_sub, alpha, rho_sym = alpha_only_system(h)
    var_list = ", ".join(f"a{c}" for c in range(1, h))
    out = []
    out.append("short=0;")
    out.append("printlevel=0;")
    out.append("option(redSB);")
    out.append("option(redTail);")
    if mode == "symbolic":
        out.append(f"ring R = (0,r), ({var_list}), dp;")
        out.append("minpoly = r^8 - 16;")

    eq_strs = []
    for c, k, e in eqs_sub:
        # Clear denominators via collecting numerator
        e_num, e_den = sp.fraction(sp.together(e))
        e_clean = sp.expand(e_num)
        s = str(e_clean).replace("rho", "r").replace("**", "^")
        eq_strs.append(s)

    out.append("ideal I =")
    out.append(",\n".join("  " + s for s in eq_strs) + ";")
    out.append("ideal G = groebner(I);")
    out.append('print("GB size:");')
    out.append("print(size(G));")
    out.append('print("GB:");')
    out.append("print(G);")
    for c in range(1, h):
        out.append(f'print("a{c} reduces to:");')
        out.append(f"print(reduce(a{c}, G));")
    out.append("quit;")

    text = "\n".join(out)
    if output:
        with open(output, "w") as f:
            f.write(text)
        print(f"Wrote {output} ({len(eqs_sub)} eqs in {len(alpha)} unknowns)")
    else:
        print(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, default=4)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    emit_singular(args.h, output=args.output)


if __name__ == "__main__":
    main()
