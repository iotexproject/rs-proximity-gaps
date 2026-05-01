"""g3_3pos_rate_eighth_lift_16x2.py — Substitution Principle lift verify, rate 1/8.

Note 0308 closed K ≤ 56 RIGOROUS at rate 1/8 base (8, 1). To extend to
deployment scale (16, 2), verify Substitution Principle holds via vdim sweep
on a sample of (16, 2) triples — analog of Note 0307 for rate 1/2.

For (16, 2) rate 1/8: σ deg = 6, above-J = positions {2, ..., 15} = 14 pos,
C(14, 3) = 364 triples. Sample 10 representative triples (mix of reducible
+ coprime), verify each gives vdim ≤ 56.
"""
from __future__ import annotations

import math
import os
import subprocess
import time
from math import gcd


def run_case(n: int, k: int, a: tuple[int, int, int], outdir: str,
             timeout_s: int = 120) -> dict:
    d_sig = math.isqrt(n * k)
    if d_sig * d_sig != n * k: d_sig += 1
    a1, a2, a3 = a
    p_decls = ", ".join(f"p{i}" for i in range(d_sig))
    p_terms = " + ".join(f"p{i}*z^{i}" for i in range(d_sig))
    z_decls = "\n".join(f"poly z_{i} = reduce(z^{i}, std(sigma));"
                         for i in range(1, n))
    z_list = ", ".join(f"z_{i}" for i in range(1, n))
    div_polys = "\n".join(f"poly div{c} = Mn[{c+1}, 1];" for c in range(d_sig))
    div_ids = ", ".join(f"div{c}" for c in range(d_sig))
    cert_polys = "\n".join(f"poly cert{c} = M[{c+1}, 1];"
                            for c in range(k, d_sig))
    cert_ids = ", ".join(f"cert{c}" for c in range(k, d_sig))
    elim_vars = '*'.join(f'p{i}' for i in range(d_sig))
    sing = f"""ring R = 0, (z, {p_decls}, alpha1, alpha2, alpha3), (dp(1), lp({d_sig + 3}));
poly sigma = z^{d_sig} + {p_terms};
{z_decls}
list zs = {z_list};
poly zn = reduce(z^{n} - 1, std(sigma));
matrix Mn = coeffs(zn, z);
{div_polys}
poly h = alpha1 * zs[{a1}] + alpha2 * zs[{a2}] + alpha3 * zs[{a3}];
matrix M = coeffs(h, z);
{cert_polys}
ideal I = {cert_ids}, {div_ids};
ideal E = eliminate(I, {elim_vars});
ring R2 = 0, (alpha1, alpha2, alpha3), lp;
ideal E2 = imap(R, E);
ideal E3 = E2 + ideal(alpha3 - 1);
ideal G = std(E3);
print("dim:");
print(dim(G));
print("vdim:");
print(vdim(G));
exit;
"""
    sing_file = os.path.join(outdir, f"3pos_n{n}_k{k}_a{a1}_{a2}_{a3}.sing")
    with open(sing_file, "w") as f:
        f.write(sing)
    t0 = time.time()
    try:
        proc = subprocess.run(
            ["Singular", "-q", sing_file], capture_output=True, text=True,
            timeout=timeout_s,
        )
        out = proc.stdout
        elapsed = time.time() - t0
        dim_v, vdim_v = None, None
        lines = out.split("\n")
        for i, line in enumerate(lines):
            ls = line.strip()
            if ls == "dim:" and i + 1 < len(lines):
                try: dim_v = int(lines[i + 1].strip())
                except ValueError: pass
            elif ls == "vdim:" and i + 1 < len(lines):
                try: vdim_v = int(lines[i + 1].strip())
                except ValueError: pass
        return {"ok": True, "dim": dim_v, "vdim": vdim_v, "elapsed": elapsed}
    except subprocess.TimeoutExpired:
        return {"ok": False, "msg": "TIMEOUT"}


def main():
    n, k = 16, 2
    outdir = "/tmp/g3_rate_eighth_lift"
    os.makedirs(outdir, exist_ok=True)

    print(f"=== Rate 1/8 Substitution lift sample at ({n}, {k}) ===")
    print(f"σ deg 6, sample 10 triples (mix reducible + coprime)")
    print()

    # Reducible triples (gcd > 1, reduce to base (8, 1))
    reducible = [
        (4, 6, 8),    # gcd=2 → (2, 3, 4) at (8, 1)
        (4, 8, 14),   # gcd=2 → (2, 4, 7) at (8, 1)
        (6, 10, 14),  # gcd=2 → (3, 5, 7)
        (8, 12, 14),  # gcd=2 → (4, 6, 7)
    ]
    # Coprime triples
    coprime = [
        (3, 5, 7),    # base case at smaller scale
        (5, 11, 13),  # coprime, mid range
        (7, 11, 13),  # coprime, asymmetric
        (9, 11, 13),  # coprime
        (11, 13, 15), # coprime, high range
        (3, 7, 13),   # spread coprime
    ]

    print("--- Reducible ---")
    max_K_red = 0
    for t in reducible:
        d = gcd(gcd(t[0], t[1]), gcd(t[2], n))
        base = tuple(x // d for x in t)
        r = run_case(n, k, t, outdir)
        K = r.get("vdim", -1)
        max_K_red = max(max_K_red, K) if K and K > 0 else max_K_red
        print(f"  {t} (d={d} → {base} at (8, 1)): vdim={K} ({r.get('elapsed', 0):.1f}s)",
              flush=True)

    print("\n--- Coprime ---")
    max_K_cop = 0
    for t in coprime:
        r = run_case(n, k, t, outdir)
        K = r.get("vdim", -1)
        max_K_cop = max(max_K_cop, K) if K and K > 0 else max_K_cop
        print(f"  {t}: vdim={K} ({r.get('elapsed', 0):.1f}s)", flush=True)

    print()
    print("=== SUMMARY ===")
    print(f"Max K (reducible, sample): {max_K_red}")
    print(f"Max K (coprime, sample): {max_K_cop}")
    print(f"Note 0308 base (8, 1) max: 56")
    if max(max_K_red, max_K_cop) <= 56:
        print("✓ Substitution Principle lift consistent with K ≤ 56 at (16, 2)")
    else:
        print(f"⚠ Some K > 56 — investigate")


if __name__ == "__main__":
    main()
