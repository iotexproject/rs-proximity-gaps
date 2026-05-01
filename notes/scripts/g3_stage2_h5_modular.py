"""g3_stage2_h5_modular.py — fast modular Stage 2 GB at h=5 using concrete (rho, eps).

In F_17 with rho=3 (rho^8 = 16) and eps = rho^4/4 = -1 (consistent with Stage 1).
This eliminates 2 free symbols and should make GB tractable.
"""
import sys
import time

import sympy as sp

sys.path.insert(0, "notes/scripts")
from g3_stage2_general_h import (
    compute_R_offblock,
    residue_polys,
    residue_equations,
)


def test_h_modular(h, prime, rho_val, eps_val):
    print(f"\n=== h={h}, char={prime}, rho={rho_val}, eps={eps_val} ===")
    rho_sym, eps_sym = sp.symbols("rho eps")
    p_low_syms = sp.symbols(f"pL1:{h}")
    p_high_syms = sp.symbols(f"pH1:{h}")
    p_low = {a: p_low_syms[a - 1] for a in range(1, h)}
    p_high = {a: p_high_syms[a - 1] for a in range(1, h)}

    t0 = time.time()
    _r_low, _r_high, P_full, R_full = compute_R_offblock(
        h, rho_sym, eps_sym, p_low, p_high
    )
    y = sp.Symbol("y")
    Pa, Ra = residue_polys(h, P_full, R_full, y)
    eqs_by_c = residue_equations(h, Pa, Ra, y)

    all_eqs = []
    for c, expr in eqs_by_c.items():
        deg = sp.degree(expr, y) if expr != 0 else -1
        for k in range(deg + 1):
            ck = sp.expand(expr.coeff(y, k))
            if ck != 0:
                all_eqs.append(ck)
    print(f"  System built in {time.time()-t0:.2f}s, {len(all_eqs)} eqs.")

    # Substitute (rho, eps) values
    subs = {rho_sym: rho_val, eps_sym: eps_val}
    eqs_sub = [sp.expand(e.subs(subs)) for e in all_eqs]
    eqs_sub = [e for e in eqs_sub if e != 0]
    print(f"  After subs: {len(eqs_sub)} eqs.")

    p_vars = list(p_low_syms) + list(p_high_syms)

    t1 = time.time()
    try:
        G = sp.groebner(eqs_sub, *p_vars, order="lex", domain=sp.GF(prime))
    except Exception as exc:
        print(f"  GB failed: {exc}")
        return
    print(f"  GB ({len(G)} polys) computed in {time.time()-t1:.2f}s.")

    print("  Reduction of p_vars mod GB:")
    all_zero = True
    for sym in p_vars:
        rem = G.reduce(sym)[1]
        if rem != 0:
            all_zero = False
        print(f"    {sym} → {rem}")
    print(f"  All p_vars → 0: {all_zero}")


def main():
    # In F_17: rho=3 (rho^8 = 16), eps = rho^4/4 = 13*13 mod 17 = 169 mod 17 = -1 = 16
    for h in [5, 6, 7, 8]:
        test_h_modular(h, 17, 3, 16)
    # Alt: F_31 — rho with rho^8 = 16 mod 31?
    # 16 mod 31 = 16. We want rho with rho^8 = 16. Try rho = 2: 2^8 = 256 = 256 - 8*31 = 256-248 = 8. No.
    # rho = 5: 5^8 = 390625. mod 31: 390625 / 31 = 12600.8, 31*12600=390600, 390625-390600=25. No.
    # rho = 9: 9^8 = (9^2)^4 = 81^4. 81 mod 31 = 19. 19^2 = 361 = 361-11*31=20. 20^2 = 400 = 400-12*31=28. So 9^8=28 mod 31. No.
    # Skip F_31.


if __name__ == "__main__":
    main()
