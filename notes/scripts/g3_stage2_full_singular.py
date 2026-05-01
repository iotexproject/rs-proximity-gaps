"""g3_stage2_full_singular.py — emit Singular .sing scripts for FULL Stage 2 system
(all y-coefficients of residue-c equations) over Q[rho]/(rho^{8h}-16^?).

Specialized for (3k/2, 2k) family: rho^8 = 16. Stage 1 fixes eps = rho^4/4.
Variables: alpha_c, beta_c for c in [1, h-1].
"""
import argparse
import sys
import sympy as sp

sys.path.insert(0, "notes/scripts")
from g3_stage2_full_correct import stage2_system


def emit(h, mode="symbolic", prime=None, output=None):
    """Emit .sing for full Stage 2 at h.

    mode='symbolic': over Q[r]/(r^8 - 16)  (only valid for the (3k/2, 2k) Stage 1 closure pattern)
    mode='numeric': over GF(prime), substitute rho_val (need to find rho with rho^8=16 mod prime).
    """
    eqs, alpha, beta, rho_sym, eps_sym = stage2_system(h)
    eps_val = rho_sym**4 / 4
    eqs_sub = [(c, k, sp.expand(e.subs(eps_sym, eps_val))) for c, k, e in eqs]

    out = []
    out.append("short=0;")
    out.append("printlevel=0;")
    out.append("option(redSB);")
    out.append("option(redTail);")
    var_list = ", ".join(f"a{c}" for c in range(1, h)) + ", " + ", ".join(f"b{c}" for c in range(1, h))
    if mode == "symbolic":
        out.append(f"ring R = (0,r), ({var_list}), dp;")
        out.append("minpoly = r^8 - 16;")
    else:
        # NOTE: r^8 - 16 splits over F_p when p ≡ 1 mod 8, so
        # Singular won't accept it as minpoly. For numeric runs, the
        # caller should substitute a concrete rho_val and use plain GF(p).
        out.append(f"ring R = ({prime},r), ({var_list}), dp;")
        out.append("minpoly = r^8 - 16;")

    # Convert each equation to Singular syntax (replace rho with r, alphas with aN, betas with bN, multiply through to clear /2,/4)
    eq_strs = []
    for c, k, e in eqs_sub:
        # Clear denominators by multiplying by appropriate constant
        e_clean = sp.together(e)
        num, den = sp.fraction(e_clean)
        # multiply by den (a constant) — may need to be smarter about non-trivial dens
        e_int = sp.expand(num)
        s = str(e_int).replace("rho", "r").replace("**", "^")
        for c_idx in range(1, h):
            s = s.replace(f"a{c_idx}", f"_TMP_A{c_idx}").replace(f"b{c_idx}", f"_TMP_B{c_idx}")
        for c_idx in range(1, h):
            s = s.replace(f"_TMP_A{c_idx}", f"a{c_idx}").replace(f"_TMP_B{c_idx}", f"b{c_idx}")
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
        out.append(f'print("b{c} reduces to:");')
        out.append(f"print(reduce(b{c}, G));")
    out.append("quit;")

    text = "\n".join(out)
    if output:
        with open(output, "w") as f:
            f.write(text)
        print(f"Wrote {output}")
    else:
        print(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, default=4)
    parser.add_argument("--mode", default="symbolic", choices=["symbolic", "numeric"])
    parser.add_argument("--prime", type=int, default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    emit(args.h, args.mode, args.prime, args.output)


if __name__ == "__main__":
    main()
