"""g3_2mono_rate_half_base.py — Singular GB eliminator for rate-1/2 base cases.

Companion to issue #411 (paper2 K10 rate ρ=1/2 arising K bound).

For each above-J coprime 2-mono pair (a, b) at base case (n, k):
- (n, k) = (4, 2) rate 1/2: only pair (2, 3)
- (n, k) = (8, 4) rate 1/2: pairs (4,5), (4,7), (5,6), (5,7), (6,7)

Generates one .sing file per pair, runs Singular GB elimination of p_0..p_{2k-1}
to produce eliminator Φ(α, ρ). Reports deg_α(Φ) = K bound for that pair.

If max deg_α(Φ) ≤ 10 across all rate-1/2 base case pairs → empirical evidence
that rate 1/2 K bound ≈ K10 (matches rate 1/4). This de-risks #408 analytic
re-derivation.

If deg_α(Φ) > 10 for some pair → rate 1/2 is structurally larger than rate 1/4,
K10 won't extend cleanly to ABF §6.3 deployment.
"""
from __future__ import annotations

import argparse
import itertools
import os
import subprocess
import sys
import time
from math import gcd


def gen_sing(n: int, k: int, a: int, b: int) -> str:
    """Build Singular .sing file content for 2-mono pair (a, b) at base (n, k)."""
    twok = 2 * k
    p_decls = ", ".join(f"p{i}" for i in range(twok))
    p_terms = " + ".join(f"p{i}*z^{i}" for i in range(twok))
    z_decls = "\n".join(
        f"poly z_{i} = reduce(z^{i}, std(sigma));" for i in range(1, n)
    )
    z_list = ", ".join(f"z_{i}" for i in range(1, n))
    div_polys = "\n".join(
        f"poly div{c} = Mn[{c+1}, 1];" for c in range(twok)
    )
    div_ids = ", ".join(f"div{c}" for c in range(twok))
    cert_polys = "\n".join(
        f"poly cert{c} = M[{c+1}, 1];" for c in range(k, twok)
    )
    cert_ids = ", ".join(f"cert{c}" for c in range(k, twok))
    return f"""// 2-mono pair (a, b) = ({a}, {b}) at base (n, k) = ({n}, {k}), rate {k}/{n}.
ring R = 0, (z, {p_decls}, alpha, rho), (dp(1), lp({twok + 2}));
poly sigma = z^{twok} + {p_terms};

{z_decls}
list zs = {z_list};

poly zn = reduce(z^{n} - 1, std(sigma));
matrix Mn = coeffs(zn, z);
{div_polys}

poly h = rho * zs[{a}] + alpha * zs[{b}];
matrix M = coeffs(h, z);
{cert_polys}

ideal I = {cert_ids}, {div_ids};
print("CASE: (a, b) = ({a}, {b}) at (n, k) = ({n}, {k}) rate {k}/{n}");
print("Starting elimination of p_i...");
ideal E = eliminate(I, {'*'.join(f'p{i}' for i in range(twok))});
print("Done. E size:");
print(size(E));
poly phi = E[size(E)];
print("phi:");
print(phi);
intvec deg_a = 0{',0' * twok},1,0;  // alpha is var index 2k+1 (after z, p0..p_{{2k-1}})
int da = deg(phi, deg_a);
print("CASE_RESULT (a={a}, b={b}, n={n}, k={k}): deg_alpha = " + string(da));
exit;
"""


def above_J_pairs(n: int, k: int) -> list[tuple[int, int]]:
    """Coprime 2-mono pairs (a, b) with a, b ∈ [k, n-1], gcd(a, b, n) = 1."""
    out = []
    for a in range(k, n):
        for b in range(a + 1, n):
            if gcd(gcd(a, b), n) == 1:
                out.append((a, b))
    return out


def run_case(sing_file: str, timeout_s: int = 600) -> tuple[bool, int | None, str]:
    """Run Singular on a .sing file, parse CASE_RESULT line."""
    out_file = sing_file.replace(".sing", ".out")
    t0 = time.time()
    try:
        proc = subprocess.run(
            ["Singular", "-q", sing_file],
            capture_output=True, text=True, timeout=timeout_s,
        )
        out = proc.stdout
        with open(out_file, "w") as f:
            f.write(out)
        for line in out.split("\n"):
            if "CASE_RESULT" in line:
                # Parse "deg_alpha = N"
                deg = int(line.split("deg_alpha =")[1].strip())
                dt = time.time() - t0
                return True, deg, f"deg={deg} ({dt:.1f}s)"
        return False, None, f"no CASE_RESULT in output ({time.time()-t0:.1f}s)"
    except subprocess.TimeoutExpired:
        return False, None, f"TIMEOUT ({timeout_s}s)"
    except Exception as e:
        return False, None, f"ERROR: {e}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default="/tmp/g3_rate_half_base")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    os.chdir(args.outdir)

    print("=== Rate 1/2 base case 2-mono Singular GB elimination ===")
    print("Companion to issue #411. Compares to Note 0286 (rate 1/4 K ≤ 8 RIGOROUS).")
    print()

    bases = [(4, 2), (8, 4)]
    all_results = []
    for n, k in bases:
        pairs = above_J_pairs(n, k)
        print(f"--- (n, k) = ({n}, {k}) rate {k/n:.2f}, {len(pairs)} above-J coprime pairs ---")
        for (a, b) in pairs:
            sing_file = f"2mono_n{n}_k{k}_a{a}_b{b}.sing"
            with open(sing_file, "w") as f:
                f.write(gen_sing(n, k, a, b))
            ok, deg, msg = run_case(sing_file, args.timeout)
            status = "✓" if ok else "✗"
            print(f"  {status} (a, b)=({a}, {b}): {msg}", flush=True)
            all_results.append(((n, k), (a, b), ok, deg))
        print(flush=True)

    # Summary
    print("=== SUMMARY ===")
    rate_half_max = 0
    for ((n, k), (a, b), ok, deg) in all_results:
        if ok and deg is not None and deg > rate_half_max:
            rate_half_max = deg
    print(f"Max deg_alpha(Φ) across rate-1/2 base cases: {rate_half_max}")
    print()
    print("Comparison reference (Note 0286, rate 1/4 base case (8, 2)):")
    print("  Max deg_alpha(Φ) = 8 RIGOROUS UNIVERSAL")
    print()
    if rate_half_max <= 10:
        print(f"✓ Rate 1/2 deg_alpha ≤ {rate_half_max} ≤ 10")
        print("  → empirical evidence rate 1/2 K bound is small, justifies #408 effort")
    else:
        print(f"⚠ Rate 1/2 deg_alpha = {rate_half_max} > 10")
        print("  → rate 1/2 structurally larger than rate 1/4, K10 won't extend cleanly")


if __name__ == "__main__":
    main()
