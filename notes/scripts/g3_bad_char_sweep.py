"""g3_bad_char_sweep.py — find primes where chain+endpoints CLOSURE fails.

For each h and each prime p in pool, compute LEX GB of (chain + 2 endpoints)
over F_p and check vdim = 1 (i.e. (x_1, ..., x_{h-1}) is the only solution).

If vdim > 1: p is in N_B(h). Otherwise OK.
"""
from __future__ import annotations
import argparse
import re
import subprocess
from typing import List, Tuple

import sympy as sp


def gen_singular_closure_test(h: int, p: int) -> str:
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
    endpts = []
    for c in [h - 2, h - 1]:
        endpts.append(sp.expand(14 * Vc[c] - 3 * U_sq[c]))

    ring_vars = ",".join(f"x{i}" for i in range(1, h))
    lines = [f"ring R = {p},({ring_vars}),lp;"]
    for i, eq in enumerate(chain):
        lines.append(f"poly c{i} = {sp.sstr(sp.expand(eq))};")
    for i, eq in enumerate(endpts):
        lines.append(f"poly e{i} = {sp.sstr(eq)};")
    lines.append("ideal IC = " + ", ".join(f"c{i}" for i in range(len(chain))) +
                 "," + ", ".join(f"e{i}" for i in range(len(endpts))) + ";")
    lines.append("ideal GC = std(IC);")
    lines.append('"vdim:"; vdim(GC);')
    lines.append("$;")
    return "\n".join(lines)


def run(h: int, p: int, timeout: int = 60) -> int:
    script = gen_singular_closure_test(h, p)
    try:
        r = subprocess.run(["Singular", "-q"], input=script.encode(),
                           capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return -2
    out = r.stdout.decode()
    lines = out.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "vdim:" and i + 1 < len(lines):
            try:
                v = int(lines[i + 1].strip())
                return v
            except ValueError:
                return -1
    return -1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, default=5)
    parser.add_argument("--prime-max", type=int, default=200)
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    # Generate primes ≤ prime_max
    primes = list(sp.sieve.primerange(2, args.prime_max + 1))
    bad_primes = []
    print(f"Sweeping closure at h={args.h} over primes up to {args.prime_max}:")
    for p in primes:
        v = run(args.h, p, timeout=args.timeout)
        if v == 1:
            tag = "OK"
        elif v == -1:
            tag = "PARSE-FAIL"
        elif v == -2:
            tag = "TIMEOUT"
        elif v == 0:
            tag = "EMPTY (-1 or no solns)"
        else:
            tag = f"vdim={v} BAD"
            bad_primes.append((p, v))
        print(f"  p = {p:3d}: vdim = {v:3d}  [{tag}]")
    print(f"\n  BAD primes (vdim > 1): {bad_primes}")
    print(f"  N_B(h={args.h}) ∩ [2, {args.prime_max}] = {[p for p, _ in bad_primes]}")


if __name__ == "__main__":
    main()
