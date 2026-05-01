"""g3_stage2_singular_native.py — emit a self-contained Singular script
that constructs Stage 2 and runs GB natively. Singular's C-level poly
arithmetic is dramatically faster than dict-of-monomials in Python at
larger h.

Strategy:
- Declare ring with vars (a1,...,a_{h-1}, b1,...,b_{h-1}, t).
- Build E = sum_d E_d * t^d as a single polynomial.
- Compute R via series-recursion using Singular procedure.
- Extract U_c residue equations.
- Run groebner.

Note: Singular has a 'short=0' display flag. Use 'execute' for dynamic strings.
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_stage2_fast import find_rho


def emit(h, p, rho_val):
    inv2 = pow(2, p-2, p)
    inv4 = pow(4, p-2, p)
    eps_val = (pow(rho_val, 4, p) * inv4) % p
    Eh_val = (-pow(rho_val, 3, p) * inv2) % p
    E0_val = (-eps_val) % p

    var_names = [f"a{c}" for c in range(1, h)] + [f"b{c}" for c in range(1, h)]
    nvar = 2 * (h - 1)

    lines = []
    lines.append("short=0;")
    lines.append("printlevel=0;")
    lines.append("option(redSB);")
    lines.append(f"ring AmbR = {p}, ({', '.join(var_names + ['t'])}), (lp(1), dp({nvar}));")
    # Note: we use a block order — t lex-leading so we can read coefficients of t^k easily.

    # Build E
    E_terms = []
    E_terms.append(f"({E0_val})")
    E_terms.append(f"({Eh_val})*t^{h}")
    E_terms.append(f"({rho_val})*t^{3*h}")
    E_terms.append(f"t^{4*h}")
    for c in range(1, h):
        E_terms.append(f"a{c}*t^{2*h+c}")
        E_terms.append(f"b{c}*t^{3*h+c}")
    lines.append(f"poly E = {' + '.join(E_terms)};")

    # Compute R via series. We want E*R = 1 - t^{8h} truncated.
    # Use top-down: R[4h] = 1, then R[4h-d] = -E[4h-d] - sum_{ell=1..d-1} E[4h-ell]*R[4h-d+ell].
    # In Singular, we can compute coeff(P, t^d) via "poly cd = lead(coef(P, t^d))" or division by t-shift.
    #
    # Cleaner: pre-compute R[d] for d = 4h, 4h-1, ..., 0 as Singular polys (no t).
    # Each R[d] is a polynomial in (a1,...,b_{h-1}).
    # Build R as a sum of R[d]*t^d at the end.
    #
    # For coefficient extraction: in this ring, since vars are (a..b..t) with block order,
    # any polynomial P = sum_d (poly_in_ab) * t^d. Coefficient at t^d is `coef(P, t^d)`.

    # Approach: use procedure to compute coefficients. We'll define R[d] via
    # `poly Rd = ...` and accumulate Rfull = sum Rd * t^d.

    # Declare R[*] as individual polys (Singular doesn't support poly arrays)
    lines.append(f"poly Rd{4*h} = 1;")

    # E coefficients: E_coef[d+1] = coefficient at t^d in E. For our specific E, only d in
    # {0, h, 3h, 4h, 2h+c, 3h+c} are non-zero. Rather than extract via Singular,
    # we know them — emit them directly.
    E_coef_vals = [None] * (4*h + 1)  # 0-indexed
    E_coef_vals[0] = f"({E0_val})"
    E_coef_vals[h] = f"({Eh_val})"
    E_coef_vals[3*h] = f"({rho_val})"
    E_coef_vals[4*h] = "1"
    for c in range(1, h):
        E_coef_vals[2*h + c] = f"a{c}"
        E_coef_vals[3*h + c] = f"b{c}"
    # default zero
    for d in range(4*h + 1):
        if E_coef_vals[d] is None:
            E_coef_vals[d] = "0"

    # Emit R[d] via for-loop
    # for d in [1, 4h]: R[4h-d] = -E[4h-d] - sum_{ell=1..d-1} E[4h-ell] * R[4h-d+ell]
    for d in range(1, 4*h + 1):
        idx = 4*h - d  # we want R[idx]
        rhs_parts = [f"-({E_coef_vals[idx]})"]
        for ell in range(1, d):
            e_term = E_coef_vals[4*h - ell]
            if e_term == "0":
                continue
            rhs_parts.append(f"-({e_term})*Rd{4*h - d + ell}")
        lines.append(f"poly Rd{idx} = {' '.join(rhs_parts)};")

    # Build U_c for c in [1, h-1]: U_c(y) = S_c(y) + y T_c(y)
    # where P^(a)(y) = sum_j E[a + j*h] * y^j
    # R^(b)(y) = sum_j R[a + j*h] * y^j
    # S_c = sum_{a+b=c} P^(a) R^(b), T_c similarly
    #
    # We extract coefficients of y, but y is not an actual variable. Just iterate
    # over all (j1, j2, a1, a2) tuples manually, accumulating Sc[k], Tc[k].
    # Then [y^k] U_c = Sc[k] + Tc[k-1].
    # Each Sc[k] / Tc[k] is a poly in a, b.

    # Determine max y-degree: 4 + 4 = 8, plus 1 from y T_c → 9.
    # Each Sc[k] = sum over (a, b, j1, j2) with j1+j2=k, a+b=c, a,b in [0,h-1], j1,j2 in [0..4].
    # We have E[a+j1*h] and R[b+j2*h] — array indices into our 1-based Rarr (and E_coef_vals).

    # Initialize Sc, Tc
    for c in range(1, h):
        for k in range(9):
            lines.append(f"poly Sc{c}_y{k} = 0;")
            lines.append(f"poly Tc{c}_y{k} = 0;")

    # Accumulate
    for c in range(1, h):
        for a in range(h):
            for b in range(h):
                if a + b == c:
                    # contributes to S_c
                    for j1 in range(5):
                        for j2 in range(5):
                            d1 = a + j1*h
                            d2 = b + j2*h
                            if d1 > 4*h or d2 > 4*h:
                                continue
                            e1 = E_coef_vals[d1]
                            if e1 == "0":
                                continue
                            # R is in Rarr[d2+1]
                            lines.append(f"Sc{c}_y{j1+j2} = Sc{c}_y{j1+j2} + ({e1})*Rd{d2};")
                if a + b == c + h:
                    # contributes to T_c
                    for j1 in range(5):
                        for j2 in range(5):
                            d1 = a + j1*h
                            d2 = b + j2*h
                            if d1 > 4*h or d2 > 4*h:
                                continue
                            e1 = E_coef_vals[d1]
                            if e1 == "0":
                                continue
                            lines.append(f"Tc{c}_y{j1+j2} = Tc{c}_y{j1+j2} + ({e1})*Rd{d2};")

    # Build U_c[k] = Sc[k] + Tc[k-1] for k in [0, 9]
    eq_names = []
    for c in range(1, h):
        for k in range(10):
            parts = []
            if 0 <= k <= 8:
                parts.append(f"Sc{c}_y{k}")
            if 0 <= k-1 <= 8:
                parts.append(f"Tc{c}_y{k-1}")
            if not parts:
                continue
            eq_name = f"U{c}_{k}"
            lines.append(f"poly {eq_name} = {' + '.join(parts)};")
            eq_names.append(eq_name)

    # Build ideal — keep only non-zero equations
    # We can just include all and let Singular dedupe; or check via "if (eq != 0)" — too verbose.
    # Just include them all.
    lines.append("// Now eliminate t — we want only relations in (a, b).")
    lines.append("ring SmallR = " + str(p) + ", (" + ", ".join(var_names) + "), dp;")
    lines.append("setring SmallR;")
    # Map from AmbR; but we built equations in AmbR. Use imap or fetch.
    lines.append("// Imap each equation")
    for ename in eq_names:
        lines.append(f"poly {ename} = imap(AmbR, {ename});")

    lines.append(f"ideal I = {', '.join(eq_names)};")
    lines.append("ideal G = groebner(I);")
    lines.append('print("GB size:");')
    lines.append("print(size(G));")
    lines.append('print("GB:");')
    lines.append("print(G);")
    lines.append("quit;")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, required=True)
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--rho", type=int, default=None)
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()
    rho_val = args.rho
    if rho_val is None:
        rhos = find_rho(args.p)
        rho_val = sorted(rhos)[0]
    s = emit(args.h, args.p, rho_val)
    with open(args.out, "w") as f:
        f.write(s)
    print(f"Wrote {len(s.splitlines())} lines to {args.out}")
    print(f"rho = {rho_val}")


if __name__ == "__main__":
    main()
