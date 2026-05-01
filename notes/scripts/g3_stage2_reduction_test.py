"""g3_stage2_reduction_test.py — test the h → h/2 structural reduction
hypothesis (Note 0243).

For h = 2h', substitute α_{2c} = β_{2c} = 0 in Stage 2 system at h.
Get a reduced system in {α_{2c+1}, β_{2c+1}}_{c=0..h'-1}, i.e., h' "odd"
unknowns each.

Hypothesis: this reduced system is equivalent (modulo a twist) to Stage 2
at h'.

Test:
1. Build full Stage 2 at h via g3_stage2_fast.
2. Substitute even-c unknowns → 0.
3. Run GB of the reduced system; check if max ideal in odd-c unknowns.
4. If yes — induction step works → h closure follows from h' closure.
"""
import argparse
import sys
import os
import subprocess
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_stage2_fast import build_stage2, find_rho


def reduce_even(eqs, h, p):
    """Substitute α_{2c} = β_{2c} = 0 for c with 2c < h (i.e., even c-indices).
    Variable index layout: a1, ..., a_{h-1}, b1, ..., b_{h-1}.
    Index i_α = c-1 for α_c (c=1..h-1); index i_β = (h-1) + (c-1) for β_c.
    Even c values for substitution: c=2,4,...,floor((h-1)/2)*2.
    """
    nvar = 2 * (h - 1)
    even_indices = set()
    for c in range(2, h, 2):  # c=2,4,...
        even_indices.add(c - 1)              # α_c
        even_indices.add((h-1) + (c - 1))    # β_c
    reduced = []
    for c, k, poly in eqs:
        new_poly = {}
        for monom, coef in poly.items():
            kill = False
            for ei in even_indices:
                if monom[ei] > 0:
                    kill = True
                    break
            if not kill:
                new_poly[monom] = coef
        if new_poly:
            reduced.append((c, k, new_poly))
    return reduced, even_indices


def emit_singular_reduced(eqs, h, p, output, drop_indices):
    """Emit Singular ideal using only the surviving variables."""
    surviving = []
    name_map = {}
    for c in range(1, h):
        idx = c - 1
        if idx not in drop_indices:
            name_map[idx] = f"a{c}"
            surviving.append(f"a{c}")
        idx = (h-1) + (c - 1)
        if idx not in drop_indices:
            name_map[idx] = f"b{c}"
            surviving.append(f"b{c}")

    if not surviving:
        print("WARN: all variables dropped — empty ring")
        return 0

    out = ["short=0;", "printlevel=0;", "option(redSB);"]
    out.append(f"ring R = {p}, ({', '.join(surviving)}), dp;")

    eqs_str = []
    for c, k, poly in eqs:
        terms = []
        for monom, coef in poly.items():
            tparts = [str(coef)]
            for i, ex in enumerate(monom):
                if ex > 0:
                    tparts.append(f"{name_map[i]}" + (f"^{ex}" if ex > 1 else ""))
            terms.append("*".join(tparts))
        eqs_str.append(" + ".join(terms) if terms else "0")

    out.append("ideal I =")
    out.append(",\n".join("  " + s for s in eqs_str) + ";")
    out.append("ideal G = groebner(I);")
    out.append('print("GB size:");')
    out.append("print(size(G));")
    out.append('print("GB:");')
    out.append("print(G);")
    out.append("quit;")

    with open(output, "w") as f:
        f.write("\n".join(out))
    return len(eqs_str)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, required=True, help="parent h (must be even)")
    parser.add_argument("--p", type=int, default=193, help="prime field")
    parser.add_argument("--rho", type=int, default=None)
    args = parser.parse_args()

    if args.h % 2 != 0:
        print("h must be even"); return

    p = args.p
    rho_val = args.rho
    if rho_val is None:
        rhos = find_rho(p)
        rho_val = sorted(rhos)[0]
    print(f"p={p}, rho={rho_val}, h={args.h}")

    print(f"Building Stage 2 at h={args.h}...")
    t0 = time.time()
    eqs, nvar = build_stage2(args.h, p, rho_val)
    print(f"  built in {time.time()-t0:.2f}s; {len(eqs)} eqs, {nvar} vars")

    reduced, dropped = reduce_even(eqs, args.h, p)
    n_remain = nvar - len(dropped)
    print(f"\nReduced (α_even=β_even=0): {len(reduced)} eqs, {n_remain} surviving vars")
    print(f"  dropped indices: {sorted(dropped)} (count {len(dropped)})")

    out = f"/tmp/reduced_h{args.h}_p{p}.sing"
    n_eq = emit_singular_reduced(reduced, args.h, p, out, dropped)
    print(f"  wrote {n_eq} eqs to {out}")
    print(f"\nRunning Singular ...")
    res = subprocess.run(["Singular", "-q", out], capture_output=True, text=True, timeout=300)
    print(res.stdout + res.stderr)


if __name__ == "__main__":
    main()
