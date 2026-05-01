"""g3_stage2_koalabear.py — verify Stage 2 at deployment scales over KoalaBear.

KoalaBear prime: q = 2^31 - 2^24 + 1 = 2130706433.
q - 1 = 2^24 · 127.

For h ∈ {4, 8, 16, 32}, deployment scale n = 8h ∈ {32, 64, 128, 256}.
Stage 1 requires rho ∈ F_q with rho^8 = 16. Test: 8 | q-1 (yes, 2^24 | q-1).

Run Singular GB (or modStd) for full Stage 2 system at each h.
"""
import sys
import os
import subprocess
import sympy as sp

sys.path.insert(0, "notes/scripts")
from g3_stage2_full_correct import stage2_system

KOALABEAR = 2**31 - 2**24 + 1  # = 2130706433


def find_rho(p):
    """Return list of rho in F_p with rho^8 = 16. Return up to 8 of them."""
    target = 16 % p
    rhos = []
    # Use the algebraic structure: rho^8 = 16 iff rho^8/16 = 1 iff rho is a primitive 8h-th root
    # For brute force at small p: scan. For large p: use generator approach.
    # Find a primitive root g of F_p*.
    from sympy.ntheory import is_primitive_root, factorint
    p_minus_1 = p - 1
    pminus1_factors = list(factorint(p_minus_1).keys())
    g = None
    for cand in range(2, p):
        if all(pow(cand, p_minus_1 // f, p) != 1 for f in pminus1_factors):
            g = cand
            break
    assert g is not None, "no primitive root found"
    # rho = g^k satisfies rho^8 = 16 iff g^{8k} = 16, find log of 16 base g.
    # Brute force baby-step: g^{2^a} sequence
    # For now, simpler: solve g^x = 16 via Pohlig-Hellman or BSGS. But for KoalaBear it's expensive.
    # Alternative: take 16 = 2^4. Then rho^8 = 2^4. Set rho = 2^{1/2} * ζ_8^k.
    # In F_p with p ≡ 1 mod 8: sqrt(2) and ζ_8 exist.
    # sqrt(2) in F_p: pow(2, (p+1)/4, p) if p ≡ 3 mod 4, or use Tonelli-Shanks. p ≡ 1 mod 8 means p = 8k+1, so p ≡ 1 mod 4. Use Tonelli-Shanks.
    sqrt2 = tonelli_shanks(2, p)
    # ζ_8 = primitive 8th root of unity. (g)^{(p-1)/8} works.
    zeta_8 = pow(g, (p-1) // 8, p)
    # rho = sqrt2 * zeta_8^k for k=0..7 gives all 8 values
    for k in range(8):
        rho_val = (sqrt2 * pow(zeta_8, k, p)) % p
        if pow(rho_val, 8, p) == target:
            rhos.append(rho_val)
    return rhos


def tonelli_shanks(n, p):
    """Find sqrt(n) mod p, assuming p ≡ 1 mod 4."""
    n %= p
    if pow(n, (p-1) // 2, p) != 1:
        raise ValueError(f"{n} is not a QR mod {p}")
    # Find Q, S with p - 1 = Q * 2^S
    Q, S = p - 1, 0
    while Q % 2 == 0:
        Q //= 2
        S += 1
    # Find z = non-residue
    z = 2
    while pow(z, (p-1) // 2, p) != p - 1:
        z += 1
    M, c, t, R = S, pow(z, Q, p), pow(n, Q, p), pow(n, (Q+1)//2, p)
    while True:
        if t == 1:
            return R
        i = 0
        temp = t
        while temp != 1:
            temp = (temp * temp) % p
            i += 1
        b = pow(c, 1 << (M - i - 1), p)
        M = i
        c = (b * b) % p
        t = (t * c) % p
        R = (R * b) % p


def emit_singular(h, p, rho_val, output, use_modstd=False):
    eqs, alpha, beta, rho_sym, eps_sym = stage2_system(h)
    eps_val = rho_sym**4 / 4
    a_vars = list(alpha) + list(beta)
    eqs_sub = []
    for c, k, e in eqs:
        e1 = sp.expand(e.subs(eps_sym, eps_val).subs(rho_sym, rho_val))
        poly = sp.Poly(e1, *a_vars)
        new_terms = []
        for monom, coef in poly.terms():
            num, den = sp.fraction(sp.Rational(coef))
            den_inv = pow(int(den) % p, p-2, p) if int(den) % p != 0 else 0
            c_mod = (int(num) * den_inv) % p
            if c_mod != 0:
                term_parts = [str(c_mod)]
                for v, ex in zip(a_vars, monom):
                    if ex > 0:
                        term_parts.append(f"{v.name}" + (f"^{ex}" if ex > 1 else ""))
                new_terms.append("*".join(term_parts))
        eqs_sub.append(" + ".join(new_terms) if new_terms else "0")

    var_list = ", ".join(f"a{c}" for c in range(1, h)) + ", " + ", ".join(f"b{c}" for c in range(1, h))
    out = []
    out.append("short=0;")
    out.append("printlevel=0;")
    out.append("option(redSB);")
    out.append("option(redTail);")
    if use_modstd:
        out.append('LIB "modstd.lib";')
    out.append(f"ring R = {p}, ({var_list}), dp;")
    out.append("ideal I =")
    out.append(",\n".join("  " + s for s in eqs_sub) + ";")
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
    return len(eqs_sub)


def main():
    p = KOALABEAR
    print(f"KoalaBear prime: q = {p}")
    print(f"q - 1 = {p-1} = {sp.factorint(p-1)}")
    print()

    for h in [4, 8, 16, 32]:
        rhos = find_rho(p)
        if not rhos:
            print(f"h={h}: no rho with rho^8=16 mod {p}")
            continue
        rho_val = sorted(rhos)[0]
        sing_file = f"/tmp/koala_h{h}.sing"
        n_eqs = emit_singular(h, p, rho_val, sing_file, use_modstd=False)
        print(f"h={h} (n={8*h}): rho={rho_val}, {n_eqs} equations -> {sing_file}")


if __name__ == "__main__":
    main()
