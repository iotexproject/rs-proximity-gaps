"""g3_stage2_singular_gen.py — generate Singular script for Stage 2 GB at given h.

Outputs a .sing file that, when fed to Singular, computes the grevlex GB
of the residue-c equations modulo (rho_val, eps_val) in F_p, then checks
that each p-variable reduces to 0.

Singular is much faster than sympy for large h — this is the path to
h=32 (deployment scale (n=256, k=64)).
"""
import sys

import sympy as sp

sys.path.insert(0, "notes/scripts")
from g3_stage2_general_h import (
    compute_R_offblock,
    residue_polys,
    residue_equations,
)


def emit_singular(h, prime, rho_val, eps_val):
    """Build the Stage 2 system, evaluate at (rho_val, eps_val) in F_prime,
    and emit a Singular script."""
    rho_sym, eps_sym = sp.symbols("rho eps")
    p_low_syms = sp.symbols(f"pL1:{h}")
    p_high_syms = sp.symbols(f"pH1:{h}")
    p_low = {a: p_low_syms[a - 1] for a in range(1, h)}
    p_high = {a: p_high_syms[a - 1] for a in range(1, h)}

    _, _, P_full, R_full = compute_R_offblock(
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

    # Substitute (rho, eps)
    subs = {rho_sym: sp.Integer(rho_val), eps_sym: sp.Integer(eps_val)}
    eqs_sub = [sp.expand(e.subs(subs)) for e in all_eqs]
    eqs_sub = [e for e in eqs_sub if e != 0]

    p_vars = list(p_low_syms) + list(p_high_syms)
    p_var_names = [str(s) for s in p_vars]

    # Build Singular script.
    lines = []
    lines.append("short=0;")
    lines.append("printlevel=0;")
    lines.append("option(redSB);")
    lines.append("option(redTail);")
    var_decl = ", ".join(p_var_names)
    lines.append(f"ring R = {prime}, ({var_decl}), dp;")  # dp = grevlex
    eq_strs = []
    for i, eq in enumerate(eqs_sub):
        # Replace ** with ^ for Singular.
        s = str(eq).replace("**", "^")
        eq_strs.append(f"  {s}")
    lines.append("ideal I = ")
    lines.append(",\n".join(eq_strs) + ";")
    lines.append("ideal G = groebner(I);")
    lines.append('print("GB size:");')
    lines.append("print(size(G));")
    # Reduction check
    for v in p_var_names:
        lines.append(f'print("{v} reduces to:");')
        lines.append(f"print(reduce({v}, G));")
    lines.append("quit;")
    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, required=True)
    parser.add_argument("--prime", type=int, default=17)
    parser.add_argument("--rho", type=int, default=3)
    parser.add_argument("--eps", type=int, default=16)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()

    script = emit_singular(args.h, args.prime, args.rho, args.eps)
    if args.out:
        with open(args.out, "w") as f:
            f.write(script)
        print(f"Wrote {args.out} ({len(script)} bytes)")
    else:
        print(script)


if __name__ == "__main__":
    main()
