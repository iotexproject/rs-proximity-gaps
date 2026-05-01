"""Multi-prime Q1 verification: chain alone vs chain + E_{h/2} at h.

For each h ∈ targets and each prime p:
- vdim(chain) = c_p (chain alone)
- vdim(chain + E_{h/2}) = f_p (closed)
- Q1@d=h holds rigorously over F_p iff f_p == 1 AND c_p > 1
  (c_p == 1 means chain alone is degenerate — char-p witness vacuous)

Usage:
    python3 g3_Q1_multi_prime.py [h1 [h2 ...]]
"""
import sys
import sympy as sp
import subprocess
import time


def build(h):
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
    c_half = h // 2
    E_half = 11 * Vc[c_half] + 6 * XW[c_half] - 3 * WW[c_half]
    return chain, E_half, x


def vdim(p, chain, E_half, x, with_endpoint, timeout=900):
    ring_vars = ",".join(str(s) for s in x)
    lines = [f"ring R = {p},({ring_vars}),dp;"]
    for i, eq in enumerate(chain):
        lines.append(f"poly c{i} = {sp.sstr(sp.expand(eq))};")
    polys = [f"c{i}" for i in range(len(chain))]
    if with_endpoint:
        lines.append(f"poly Eh = {sp.sstr(sp.expand(E_half))};")
        polys.append("Eh")
    lines.append("ideal I = " + ", ".join(polys) + ";")
    lines.append("ideal G = std(I);")
    lines.append('"v:"; vdim(G);')
    lines.append("$;")
    try:
        out = subprocess.run(["Singular", "-q"], input="\n".join(lines).encode(),
                             capture_output=True, timeout=timeout).stdout.decode()
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    for line in out.splitlines():
        s = line.strip()
        if s.lstrip("-").isdigit():
            return int(s)
    return None


def run(h, primes=None):
    if primes is None:
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    chain, E_half, x = build(h)
    print(f"\n{'='*60}")
    print(f"h={h} multi-prime Q1 check")
    print(f"{'p':>4} | {'vdim(chain)':>12} | {'vdim(chain+E_{h//2})':>22} | Q1@d={h}")
    print("-" * 65)
    for p in primes:
        t0 = time.time()
        v_c = vdim(p, chain, E_half, x, False)
        v_f = vdim(p, chain, E_half, x, True)
        elapsed = time.time() - t0
        if v_c == 1:
            status = "✗ chain degenerate (vacuous)"
        elif v_f == 1:
            status = "✓ rigorous"
        else:
            status = f"✗ E_{h//2} fails (vdim>1)"
        print(f"  {p} | {str(v_c):>12} | {str(v_f):>22} | {status} ({elapsed:.0f}s)")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for h in [int(a) for a in sys.argv[1:]]:
            run(h)
    else:
        for h in [4, 8]:
            run(h)
