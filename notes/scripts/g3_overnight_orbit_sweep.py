"""g3_overnight_orbit_sweep.py — overnight autonomous sweep.

Goals:
1. Verify Conjecture C265 (orbit-length restriction) at h ∈ {9, 10, 12}.
2. Identify minimum endpoint set per h.
3. Save progressive results so the user can see progress.

Safety:
- One Singular subprocess at a time (no parallelism).
- Conservative timeouts (default 1800s = 30 min per Singular call).
- Save partial results after each h.
- Use mod-p (p=11 for h coprime to 11; p=13 fallback) for tractability.
"""
from __future__ import annotations
import argparse
import datetime
import os
import re
import subprocess
import sys
import sympy as sp


def gen_chain(h):
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
    U_sq = {c: Vc[c] - 2 * XW[c] + WW[c] for c in range(0, h)}
    endpoints = {c: sp.expand(14 * Vc[c] - 3 * U_sq[c]) for c in range(2, h)}
    return chain, endpoints


def run_singular(script, timeout):
    try:
        r = subprocess.run(["Singular", "-q"], input=script.encode(),
                           capture_output=True, timeout=timeout)
        return r.stdout.decode()
    except subprocess.TimeoutExpired:
        return "TIMEOUT"


def kbase_zh_hilbert(h, char, timeout):
    chain, _ = gen_chain(h)
    ring_vars = ",".join(f"x{i}" for i in range(1, h))
    lines = [f"ring R = {char},({ring_vars}),lp;"]
    for i, eq in enumerate(chain):
        lines.append(f"poly c{i} = {sp.sstr(sp.expand(eq))};")
    lines.append("ideal I = " + ", ".join(f"c{i}" for i in range(len(chain))) + ";")
    lines.append("ideal G = std(I);")
    lines.append('"vdim:"; vdim(G);')
    lines.append("ideal B = kbase(G);")
    lines.append('"BASIS_BEGIN";')
    lines.append("int i;")
    lines.append("for (i = 1; i <= size(B); i = i + 1) {")
    lines.append('  "BASIS " + string(i) + ": " + string(B[i]);')
    lines.append("}")
    lines.append('"BASIS_END";')
    lines.append("$;")
    out = run_singular("\n".join(lines), timeout=timeout)
    if out == "TIMEOUT":
        return None, None
    vdim = None
    basis = []
    for i, line in enumerate(out.splitlines()):
        if line.strip() == "vdim:" and i + 1 < len(out.splitlines()):
            try:
                vdim = int(out.splitlines()[i + 1].strip())
            except ValueError:
                pass
        m = re.match(r'^BASIS \d+: (.+)$', line.strip())
        if m:
            basis.append(m.group(1))
    if vdim is None:
        return None, None
    counts = [0] * h
    for mono_str in basis:
        try:
            expr = sp.sympify(mono_str, locals={f"x{j}": sp.Symbol(f"x{j}") for j in range(1, h)})
        except Exception:
            return vdim, None
        if expr == 1:
            d = 0
        else:
            d = 0
            pd = expr.as_powers_dict() if hasattr(expr, 'as_powers_dict') else {expr: 1}
            for var, exp in pd.items():
                if isinstance(var, sp.Symbol):
                    name = str(var)
                    wt = int(name[1:])
                    d += wt * int(exp)
        counts[d % h] += 1
    return vdim, counts


def solve_orbits(h, hilb):
    """Solve k_d (d | h) from Z/h-Hilbert R_c = sum_{d|h, h/d|c} k_d."""
    divisors = [d for d in range(1, h+1) if h % d == 0]
    A = [[1 if c % (h // d) == 0 else 0 for d in divisors] for c in range(h)]
    syms = sp.symbols(f"k:{len(divisors)}")
    sols = sp.linsolve((sp.Matrix(A), sp.Matrix(hilb)), syms)
    if len(sols) == 0:
        return None
    sol = list(sols)[0]
    return dict(zip(divisors, sol))


def vdim_with_endpoints(h, endpoint_indices, char, timeout):
    chain, endpoints = gen_chain(h)
    ring_vars = ",".join(f"x{i}" for i in range(1, h))
    lines = [f"ring R = {char},({ring_vars}),lp;"]
    for i, eq in enumerate(chain):
        lines.append(f"poly c{i} = {sp.sstr(sp.expand(eq))};")
    for i, idx in enumerate(endpoint_indices):
        lines.append(f"poly e{i} = {sp.sstr(endpoints[idx])};")
    parts = [f"c{i}" for i in range(len(chain))] + [f"e{i}" for i in range(len(endpoint_indices))]
    lines.append("ideal IC = " + ", ".join(parts) + ";")
    lines.append("ideal GC = std(IC);")
    lines.append('"vdim:"; vdim(GC);')
    lines.append("$;")
    out = run_singular("\n".join(lines), timeout=timeout)
    if out == "TIMEOUT":
        return None
    for i, line in enumerate(out.splitlines()):
        if line.strip() == "vdim:" and i + 1 < len(out.splitlines()):
            try:
                return int(out.splitlines()[i + 1].strip())
            except ValueError:
                return -1
    return -1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h-list", default="9,10,12,14,15")
    parser.add_argument("--char", type=int, default=11)
    parser.add_argument("--timeout-kbase", type=int, default=2700)  # 45 min
    parser.add_argument("--timeout-vdim", type=int, default=1800)   # 30 min
    parser.add_argument("--out", default="notes/scripts/g3_overnight_orbit_sweep.output.md")
    args = parser.parse_args()

    out_lines = [
        f"# g3_overnight_orbit_sweep — output log",
        f"",
        f"Started: {datetime.datetime.now().isoformat()}",
        f"Configuration: char = {args.char}, kbase timeout = {args.timeout_kbase}s, vdim timeout = {args.timeout_vdim}s",
        f"H list: {args.h_list}",
        f"",
    ]
    with open(args.out, "w") as f:
        f.write("\n".join(out_lines))

    def append(line):
        with open(args.out, "a") as f:
            f.write(line + "\n")
        print(line)
        sys.stdout.flush()

    h_list = [int(x) for x in args.h_list.split(",")]
    for h in h_list:
        append(f"\n## h = {h}\n")
        append(f"Started h={h} at {datetime.datetime.now().isoformat()}")

        # Step 1: Z/h-Hilbert via kbase
        char = args.char
        # If char divides any small structural prime (like 14 = 2·7 or denominators), pick another
        if char == 7:
            char = 11
        append(f"### Step 1: Z/h-Hilbert at char {char}")
        vdim, hilb = kbase_zh_hilbert(h, char, timeout=args.timeout_kbase)
        if vdim is None:
            append(f"  TIMEOUT at h={h} kbase. Skipping orbit analysis.")
            continue
        append(f"  vdim = {vdim}")
        append(f"  Z/h-Hilbert R_d for d ∈ Z/{h}:")
        for d in range(h):
            append(f"    R_{d}: {hilb[d]}")
        # Solve orbit decomposition
        orbits = solve_orbits(h, hilb)
        if orbits is None:
            append(f"  Cannot solve orbit decomposition (system underdetermined or infeasible)")
        else:
            append(f"  Orbit decomposition (k_d for d | h):")
            for d, k in orbits.items():
                append(f"    k_{d} = {k}  (length-{d} orbits)")

        # Step 2: Endpoint sufficiency tests
        append(f"\n### Step 2: Endpoint tests at char {char}")
        # Standard pair
        v_pair = vdim_with_endpoints(h, [h-2, h-1], char, timeout=args.timeout_vdim)
        append(f"  chain + {{E_{h-2}, E_{h-1}}}: vdim = {v_pair}")
        # E_{h-1} alone
        v_top = vdim_with_endpoints(h, [h-1], char, timeout=args.timeout_vdim)
        append(f"  chain + {{E_{h-1}}}: vdim = {v_top}")
        # E_{h-2} alone
        v_top_minus_1 = vdim_with_endpoints(h, [h-2], char, timeout=args.timeout_vdim)
        append(f"  chain + {{E_{h-2}}}: vdim = {v_top_minus_1}")

        # Step 3: If pair fails, try extended set
        if v_pair is not None and v_pair > 1:
            append(f"\n### Step 3: Standard pair FAILED. Identifying obstructing orbit lengths...")
            if orbits:
                # Find d with k_d > 0 and h/d > 2 (obstruction beyond standard pair)
                bad_lengths = []
                for d, k in orbits.items():
                    if k > 0 and d > 1 and (h // d) > 2:
                        bad_lengths.append((d, h // d, k))
                append(f"  Obstructing orbit lengths (d, h/d, count): {bad_lengths}")
                # Identify minimum c values to add: c with (h/d) | c
                needed_c_sets = []
                for d, hd, k in bad_lengths:
                    # E_c with hd | c, c ≤ h-1
                    options = [c for c in range(2, h) if c % hd == 0]
                    needed_c_sets.append((d, hd, options))
                append(f"  Required endpoint c values per orbit length: {needed_c_sets}")
                # Try adding the smallest required E_c
                added_c = sorted({opts[0] for _, _, opts in needed_c_sets if opts})
                if added_c:
                    full_set = sorted(set([h-2, h-1] + added_c))
                    append(f"  Trying extended endpoint set: {full_set}")
                    v_ext = vdim_with_endpoints(h, full_set, char, timeout=args.timeout_vdim)
                    append(f"  chain + extended: vdim = {v_ext}")

        append(f"\nFinished h={h} at {datetime.datetime.now().isoformat()}")

    append(f"\n--- ALL DONE at {datetime.datetime.now().isoformat()} ---")


if __name__ == "__main__":
    main()
