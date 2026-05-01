"""g3_stage2_residue_split.py — examine the residue-c split at h vs h/2.

At h, equations U_c for c=1..h-1. Hypothesis: equations at c ∈ {h/2, 2*h/2}
(i.e., c values divisible by GCD(h, 2)) form a subsystem matching Stage 2
at h/2.

Concretely: at h=8, examine equations at c=2, 4, 6 — do they only involve
α_2, α_4, α_6, β_2, β_4, β_6? If yes, the system splits into even/odd
blocks; the even block is potentially Stage 2 at h=4.
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_stage2_fast import build_stage2, find_rho


def analyze(h, p, rho_val):
    print(f"=== Stage 2 at h={h}, p={p}, rho={rho_val} ===")
    eqs, nvar = build_stage2(h, p, rho_val)
    print(f"  {len(eqs)} eqs, {nvar} vars (a1..a_{h-1}, b1..b_{h-1})")

    # Group by c
    by_c = {}
    for c, k, poly in eqs:
        by_c.setdefault(c, []).append((k, poly))

    print(f"\n  Per-c equation count:")
    for c in sorted(by_c):
        eqs_c = by_c[c]
        # Get vars used in this c-block
        vars_used = set()
        for k, poly in eqs_c:
            for monom in poly:
                for i, ex in enumerate(monom):
                    if ex > 0:
                        vars_used.add(i)
        # Translate var indices back
        avars = [f"a{ai+1}" for ai in vars_used if ai < h-1]
        bvars = [f"b{bi-(h-1)+1}" for bi in vars_used if bi >= h-1]
        print(f"    c={c}: {len(eqs_c)} eqs; vars used: a={sorted(avars)} b={sorted(bvars)}")

    # Check: equations at even c involve which vars?
    print(f"\n  Even-c equations:")
    even_c = [c for c in by_c if c % 2 == 0]
    even_vars_used = set()
    for c in even_c:
        for k, poly in by_c[c]:
            for monom in poly:
                for i, ex in enumerate(monom):
                    if ex > 0:
                        even_vars_used.add(i)
    avars = [f"a{ai+1}" for ai in even_vars_used if ai < h-1]
    bvars = [f"b{bi-(h-1)+1}" for bi in even_vars_used if bi >= h-1]
    print(f"    c ∈ {even_c}: {sum(len(by_c[c]) for c in even_c)} eqs; "
          f"vars used: a={sorted(avars)} b={sorted(bvars)}")
    # Even-only var indices: a_2, a_4, ... and b_2, b_4, ...
    even_only_a = [f"a{2*j}" for j in range(1, (h+1)//2)]
    even_only_b = [f"b{2*j}" for j in range(1, (h+1)//2)]
    a_used = set(avars)
    b_used = set(bvars)
    a_only_even = a_used <= set(even_only_a)
    b_only_even = b_used <= set(even_only_b)
    print(f"    only even-α used? {a_only_even} (need to be in {even_only_a})")
    print(f"    only even-β used? {b_only_even} (need to be in {even_only_b})")
    print(f"    ⟹ even-c block self-contained iff above are both True")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, required=True)
    parser.add_argument("--p", type=int, default=193)
    parser.add_argument("--rho", type=int, default=None)
    args = parser.parse_args()
    rho_val = args.rho or sorted(find_rho(args.p))[0]
    analyze(args.h, args.p, rho_val)


if __name__ == "__main__":
    main()
