"""g3_stage2_fast.py — fast Stage 2 system builder over F_p.

Key idea: substitute concrete (rho_val, eps_val = rho_val^4/4) mod p FIRST,
then build E, R, U_c as multivariate polynomials in (alpha_c, beta_c) only,
with all coefficients reduced mod p. This avoids sympy's symbolic blow-up
on rho.

Polynomial representation: dict {monomial_tuple : coef_mod_p}, where
monomial_tuple has 2*(h-1) entries [a1_exp, ..., a_{h-1}_exp, b1_exp, ..., b_{h-1}_exp].

This builder targets KoalaBear / BabyBear / M31 / Goldilocks deployment fields.
"""
import sys
import argparse
from collections import defaultdict


def mul_poly(A, B, p, nvar):
    """Multiply two dict-poly mod p."""
    out = defaultdict(int)
    for ma, ca in A.items():
        if ca == 0:
            continue
        for mb, cb in B.items():
            if cb == 0:
                continue
            mc = tuple(ma[i] + mb[i] for i in range(nvar))
            out[mc] = (out[mc] + ca * cb) % p
    return {m: c for m, c in out.items() if c != 0}


def add_poly(A, B, p):
    out = defaultdict(int, A)
    for m, c in B.items():
        out[m] = (out[m] + c) % p
    return {m: c for m, c in out.items() if c != 0}


def neg_poly(A, p):
    return {m: (p - c) % p for m, c in A.items() if c != 0}


def scale_poly(A, k, p):
    if k == 0:
        return {}
    return {m: (c * k) % p for m, c in A.items() if (c * k) % p != 0}


def poly_const(c, nvar, p):
    c = c % p
    if c == 0:
        return {}
    return {tuple([0]*nvar): c}


def poly_var(idx, nvar, p):
    """Return polynomial = single variable at position idx."""
    m = tuple(1 if i == idx else 0 for i in range(nvar))
    return {m: 1}


def build_stage2(h, p, rho_val):
    """Return list of (c, k, poly_dict) for U_c at y^k = 0.

    Variables: alpha_1, ..., alpha_{h-1}, beta_1, ..., beta_{h-1}.
    nvar = 2*(h-1).
    """
    nvar = 2 * (h - 1)

    # Compute eps = rho^4 / 4 mod p
    inv4 = pow(4, p-2, p)
    eps_val = (pow(rho_val, 4, p) * inv4) % p

    # Compute -rho^3 / 2 = E_h
    inv2 = pow(2, p-2, p)
    Eh_val = (-pow(rho_val, 3, p) * inv2) % p
    E0_val = (-eps_val) % p

    # Build E as list of dict-polys, indexed 0..4h
    E = [None] * (4*h + 1)
    for d in range(4*h + 1):
        E[d] = {}
    E[0] = poly_const(E0_val, nvar, p)
    E[h] = poly_const(Eh_val, nvar, p)
    E[2*h] = {}  # zero
    E[3*h] = poly_const(rho_val, nvar, p)
    E[4*h] = poly_const(1, nvar, p)
    # Hypothesis already-zero for E[1..h-1] and E[h+1..2h-1]
    for c in range(1, h):
        E[2*h + c] = poly_var(c-1, nvar, p)        # alpha_c at index c-1
        E[3*h + c] = poly_var((h-1) + (c-1), nvar, p)  # beta_c at index (h-1)+(c-1)

    # Recursion: R[4h] = 1; for d=1..4h, R[4h-d] = -E[4h-d] - sum_{ell=1..d-1} E[4h-ell] * R[4h-d+ell]
    R = [None] * (4*h + 1)
    R[4*h] = poly_const(1, nvar, p)
    for d in range(1, 4*h + 1):
        idx = 4*h - d
        rhs = neg_poly(E[idx], p)
        for ell in range(1, d):
            rhs = add_poly(rhs, neg_poly(mul_poly(E[4*h - ell], R[4*h - d + ell], p, nvar), p), p)
        R[idx] = rhs

    # Build P^(a) and R^(b) polynomials in y.
    # P^(a)[j] = E[a + j*h] for j in [0, 4]; same for R^(b).
    # Each is a list (length 5) of dict-polys.
    Pa = []
    Rb = []
    for a in range(h):
        pa = [{} for _ in range(5)]
        rb = [{} for _ in range(5)]
        for j in range(5):
            d = a + j*h
            if d <= 4*h:
                pa[j] = E[d]
                rb[j] = R[d]
        Pa.append(pa)
        Rb.append(rb)

    # For each c in [1, h-1]:
    # S_c(y) = sum_{a+b=c, a,b in [0,h-1]} P^(a)(y) R^(b)(y)
    # T_c(y) = sum_{a+b=c+h, a,b in [0,h-1]} P^(a)(y) R^(b)(y)
    # U_c(y) = S_c(y) + y * T_c(y), polynomial in y of degree up to 4 + 4 + 1 = 9.
    eqs = []
    for c in range(1, h):
        # Compute S_c(y) and T_c(y) as lists of dict-polys, indexed by y-power 0..8.
        Sc = [{} for _ in range(9)]
        Tc = [{} for _ in range(9)]
        # S_c
        for a in range(h):
            b = c - a
            if 0 <= b < h:
                # Multiply P^(a)(y) by R^(b)(y), accumulate into Sc.
                for j1 in range(5):
                    if not Pa[a][j1]:
                        continue
                    for j2 in range(5):
                        if not Rb[b][j2]:
                            continue
                        prod = mul_poly(Pa[a][j1], Rb[b][j2], p, nvar)
                        Sc[j1+j2] = add_poly(Sc[j1+j2], prod, p)
        # T_c
        for a in range(h):
            b = c + h - a
            if 0 <= b < h:
                for j1 in range(5):
                    if not Pa[a][j1]:
                        continue
                    for j2 in range(5):
                        if not Rb[b][j2]:
                            continue
                        prod = mul_poly(Pa[a][j1], Rb[b][j2], p, nvar)
                        Tc[j1+j2] = add_poly(Tc[j1+j2], prod, p)
        # U_c[k] = S_c[k] + T_c[k-1]
        for k in range(10):
            uk = {}
            if k <= 8:
                uk = add_poly(uk, Sc[k], p)
            if k-1 >= 0 and k-1 <= 8:
                uk = add_poly(uk, Tc[k-1], p)
            if uk:
                eqs.append((c, k, uk))
    return eqs, nvar


def emit_singular(eqs, nvar, h, p, output, use_modstd=False):
    var_names = [f"a{c}" for c in range(1, h)] + [f"b{c}" for c in range(1, h)]
    out = []
    out.append("short=0;")
    out.append("printlevel=0;")
    out.append("option(redSB);")
    if use_modstd:
        out.append('LIB "modstd.lib";')
    out.append(f"ring R = {p}, ({', '.join(var_names)}), dp;")

    eqs_str = []
    for (c, k, poly) in eqs:
        terms = []
        for monom, coef in poly.items():
            tparts = [str(coef)]
            for i, ex in enumerate(monom):
                if ex > 0:
                    tparts.append(f"{var_names[i]}" + (f"^{ex}" if ex > 1 else ""))
            terms.append("*".join(tparts))
        eqs_str.append(" + ".join(terms) if terms else "0")

    out.append("ideal I =")
    out.append(",\n".join("  " + s for s in eqs_str) + ";")
    if use_modstd:
        out.append("ideal G = modStd(I);")
    else:
        out.append("ideal G = groebner(I);")
    out.append('print("GB size:");')
    out.append("print(size(G));")
    out.append('print("GB:");')
    out.append("print(G);")
    out.append("quit;")

    with open(output, "w") as f:
        f.write("\n".join(out))
    return len(eqs_str)


def tonelli_shanks(n, p):
    n %= p
    if pow(n, (p-1) // 2, p) != 1:
        raise ValueError(f"{n} not a QR mod {p}")
    Q, S = p - 1, 0
    while Q % 2 == 0:
        Q //= 2
        S += 1
    z = 2
    while pow(z, (p-1) // 2, p) != p - 1:
        z += 1
    M, c, t, R = S, pow(z, Q, p), pow(n, Q, p), pow(n, (Q+1)//2, p)
    while True:
        if t == 1:
            return R
        i, temp = 0, t
        while temp != 1:
            temp = (temp * temp) % p
            i += 1
        b = pow(c, 1 << (M - i - 1), p)
        M = i
        c = (b * b) % p
        t = (t * c) % p
        R = (R * b) % p


def find_rho(p):
    """Find rho with rho^8 = 16 mod p (assumes p ≡ 1 mod 8)."""
    from sympy.ntheory import factorint
    p_minus_1 = p - 1
    pf = list(factorint(p_minus_1).keys())
    g = None
    for cand in range(2, p):
        if all(pow(cand, p_minus_1 // f, p) != 1 for f in pf):
            g = cand
            break
    sqrt2 = tonelli_shanks(2, p)
    zeta_8 = pow(g, p_minus_1 // 8, p)
    rhos = []
    for k in range(8):
        rv = (sqrt2 * pow(zeta_8, k, p)) % p
        if pow(rv, 8, p) == 16 % p:
            rhos.append(rv)
    return sorted(rhos)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, required=True)
    parser.add_argument("--p", type=int, required=True, help="prime field characteristic")
    parser.add_argument("--rho", type=int, default=None, help="rho value (auto-find if omitted)")
    parser.add_argument("--out", type=str, default=None, help="Singular output file")
    parser.add_argument("--modstd", action="store_true")
    parser.add_argument("--label", type=str, default="field")
    args = parser.parse_args()

    p = args.p
    if (p - 1) % 8 != 0:
        print(f"WARN: p ≡ {p % 8} mod 8 (need ≡ 1 for r^8=16 in F_p; rho lives in extension)")
    rho_val = args.rho
    if rho_val is None:
        rhos = find_rho(p)
        if not rhos:
            print(f"FAIL: no rho with rho^8 = 16 mod {p}")
            return
        rho_val = rhos[0]
        print(f"Auto-found rho candidates: {rhos}")
    print(f"Using rho = {rho_val} (rho^8 mod p = {pow(rho_val, 8, p)}, target 16)")

    print(f"Building Stage 2 system at h={args.h} over F_{{{p}}}...")
    import time
    t0 = time.time()
    eqs, nvar = build_stage2(args.h, p, rho_val)
    t1 = time.time()
    print(f"  build time: {t1-t0:.2f}s; {len(eqs)} equations in {nvar} variables")

    out = args.out or f"/tmp/{args.label}_h{args.h}.sing"
    n_eqs = emit_singular(eqs, nvar, args.h, p, out, use_modstd=args.modstd)
    print(f"  wrote {n_eqs} equations to {out}")


if __name__ == "__main__":
    main()
