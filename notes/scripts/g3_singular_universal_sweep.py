"""g3_singular_universal_sweep.py — universal sweep at fixed h via Singular.

For each h, compute:
  - chain GB (LEX): vdim, deg f.
  - chain + endpoints GB: vdim (= 1 means closure).
  - factor g_h (non-trivial part of f_h): irreducibility check (Lemma A).

Output: tabulated data for verifying the universal-h proof framework.
"""
from __future__ import annotations
import argparse
import subprocess
import sympy as sp


def gen_singular(h):
    z = sp.Symbol("z")
    x = [sp.Symbol(f"x{i}") for i in range(1, h)]
    X = sum(x[i - 1] * z**i for i in range(1, h))
    X2 = sp.expand(X * X)
    Wc = {c: X2.coeff(z, h + c) for c in range(0, h)}
    Vc = {c: X2.coeff(z, c) for c in range(0, 2 * h)}
    XW = {c: sum(x[a - 1] * Wc[c - a] for a in range(1, c + 1)
                 if 1 <= c - a < h) for c in range(0, h)}
    WW = {c: sum(Wc[a] * Wc[c - a] for a in range(1, c)
                 if 1 <= c - a < h) for c in range(0, h)}
    chain = [(x[c - 1] - Wc[c]) + 3 * Vc[c] + 2 * XW[c] - WW[c] for c in range(1, h)]
    endpts = []
    for c in [h - 2, h - 1]:
        Uc_sq = Vc[c] - 2 * XW[c] + WW[c]
        endpts.append(14 * Vc[c] - 3 * Uc_sq)

    last_var = f"x{h-1}"
    ring_vars = ",".join(f"x{i}" for i in range(1, h))
    lines = [f"ring R = 0,({ring_vars}),lp;"]
    for i, eq in enumerate(chain):
        lines.append(f"poly c{i} = {sp.sstr(sp.expand(eq))};")
    for i, eq in enumerate(endpts):
        lines.append(f"poly e{i} = {sp.sstr(sp.expand(eq))};")
    lines.append("ideal I = " + ", ".join(f"c{i}" for i in range(len(chain))) + ";")
    lines.append("ideal IC = " + ", ".join(f"c{i}" for i in range(len(chain))) +
                 "," + ", ".join(f"e{i}" for i in range(len(endpts))) + ";")
    lines.append("ideal G = std(I);")
    lines.append('"chain GB size:"; size(G);')
    lines.append('"chain vdim:"; vdim(G);')
    lines.append('"deg f:"; deg(G[1]);')
    lines.append("ideal GC = std(IC);")
    lines.append('"chain+endpt vdim:"; vdim(GC);')
    lines.append("poly fpol = G[1];")
    lines.append(f"poly gpol = fpol/{last_var};")
    lines.append('"deg g:"; deg(gpol);')
    lines.append('LIB "primdec.lib";')
    lines.append('"factor count of g:";')
    lines.append("size(factorize(gpol)[1]);")
    lines.append("$;")
    return "\n".join(lines)


def run(h, timeout=600):
    script = gen_singular(h)
    try:
        r = subprocess.run(["Singular", "-q"], input=script.encode(),
                           capture_output=True, timeout=timeout)
        return r.stdout.decode()
    except subprocess.TimeoutExpired:
        return "TIMEOUT"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h-list", default="4,5,6,7,8")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    print(f"{'h':>3} {'|G|':>5} {'vdim':>8} {'degf':>5} {'+endpt vdim':>13} {'degG':>6} {'#factors':>10}")
    for h_str in args.h_list.split(","):
        h = int(h_str)
        out = run(h, timeout=args.timeout)
        if out == "TIMEOUT":
            print(f"{h:>3} TIMEOUT (> {args.timeout}s)")
            continue
        # Parse out the values
        lines = out.strip().split("\n")
        vals = {}
        for i, line in enumerate(lines):
            if line.endswith(":") and i + 1 < len(lines):
                vals[line.rstrip(':')] = lines[i + 1].strip()
        gb_size = vals.get('"chain GB size"', "?")
        chain_vdim = vals.get('"chain vdim"', "?")
        deg_f = vals.get('"deg f"', "?")
        ce_vdim = vals.get('"chain+endpt vdim"', "?")
        deg_g = vals.get('"deg g"', "?")
        n_factors = vals.get('"factor count of g"', "?")
        try:
            deg_g_val = int(deg_g)
            deg_G_val = deg_g_val // h
        except Exception:
            deg_G_val = "?"
        print(f"{h:>3} {gb_size:>5} {chain_vdim:>8} {deg_f:>5} {ce_vdim:>13} {deg_G_val:>6} {n_factors:>10}")


if __name__ == "__main__":
    main()
