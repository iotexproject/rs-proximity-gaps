"""g3_stage2_block_check.py — verify the BLOCK-DIAGONAL Jacobian structure.

Claim: at linear order (mod m^2), each U_{c, y^k} only contains α_c, β_c
(the c-th block). I.e., for fixed c, the linear part of U_{c, *} lives in
the 2-dim subspace spanned by α_c, β_c.

Equivalently: for c' ≠ c, the linear part of U_{c, *} has 0 coefficient
on α_{c'}, β_{c'}.

If true → Stage 2 system is block-diagonal at linear order with h-1 blocks
of size 4 eqs × 2 vars each. Each block has full rank 2 (proven separately
for each c via Stage 1 closure — independent of h). Hence total Jacobian
rank = 2(h-1) for all h.
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_stage2_jac_fast import stage2_linear_part, find_rho


def check_block(h, p, rho_val):
    eqs = stage2_linear_part(h, p, rho_val)
    nvar = 2 * (h - 1)
    print(f"=== h={h} block-diagonal check ===")

    # Group eqs by c
    by_c = {}
    for c, k, vec in eqs:
        by_c.setdefault(c, []).append((k, vec))

    all_block = True
    for c in sorted(by_c):
        # Check vars used in linear parts of U_{c, *}
        # Index ranges: α_{c'} is at index c'-1; β_{c'} is at index (h-1) + (c'-1)
        # Block c is indices {c-1, (h-1)+(c-1)}
        block_idx = {c - 1, (h-1) + (c - 1)}
        used_idx = set()
        for k, vec in by_c[c]:
            for i in range(nvar):
                if vec[i+1] != 0:
                    used_idx.add(i)
        outside = used_idx - block_idx
        if outside:
            outside_names = []
            for ii in sorted(outside):
                if ii < h-1:
                    outside_names.append(f"a{ii+1}")
                else:
                    outside_names.append(f"b{ii-(h-1)+1}")
            print(f"  c={c}: NON-BLOCK linear coeffs on {outside_names}")
            all_block = False
        else:
            # Compute 4x2 block sub-Jacobian
            sub = []
            for k, vec in sorted(by_c[c]):
                sub.append((k, vec[c-1+1], vec[(h-1)+(c-1)+1]))  # +1 because vec[0] is constant
            # Rank of 4x2 = 2 iff some 2x2 minor is non-zero
            full_rank = False
            for i in range(len(sub)):
                for j in range(i+1, len(sub)):
                    det = (sub[i][1]*sub[j][2] - sub[i][2]*sub[j][1]) % p
                    if det != 0:
                        full_rank = True
                        break
                if full_rank:
                    break
            status = "FULL RANK" if full_rank else "DEFICIENT"
            print(f"  c={c}: BLOCK ({len(sub)} eqs × 2 vars) — {status}")
            if not full_rank:
                all_block = False
                print(f"    sub-Jacobian rows: {sub}")
    print(f"\n  Overall: {'BLOCK-DIAGONAL' if all_block else 'NOT BLOCK-DIAGONAL'}")
    return all_block


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, required=True)
    parser.add_argument("--p", type=int, default=193)
    parser.add_argument("--rho", type=int, default=None)
    args = parser.parse_args()
    rho_val = args.rho or sorted(find_rho(args.p))[0]
    check_block(args.h, args.p, rho_val)


if __name__ == "__main__":
    main()
