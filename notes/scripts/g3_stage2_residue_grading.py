"""g3_stage2_residue_grading.py — verify the conjectured Z/h GRADING:
every monomial in U_c has variable-index-sum ≡ c (mod h).

Variable index for α_j is j; for β_j is h + j (so β_j contributes h+j to the
index sum, which is just j mod h). Note: β_j and α_j contribute the same residue.

Stronger version: each monomial M = prod α^{n_i} prod β^{m_j} has
"weight" w(M) = sum n_i · i + sum m_j · j (mod h). Claim: w(M) ≡ c (mod h)
for every M appearing in U_{c, y^k}.
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_stage2_fast import build_stage2, find_rho


def check_grading(h, p, rho_val):
    eqs, nvar = build_stage2(h, p, rho_val)
    print(f"=== h={h}, p={p}, rho={rho_val}: residue grading check ===")
    print(f"  {len(eqs)} equations")

    all_good = True
    by_c_violation = {}
    for c, k, poly in eqs:
        for monom, coef in poly.items():
            # Compute weight
            w = 0
            for i, ex in enumerate(monom):
                if i < h - 1:
                    var_idx = i + 1  # α_{i+1}
                else:
                    var_idx = i - (h - 1) + 1  # β_{i-(h-1)+1}
                w += ex * var_idx
            w_mod = w % h
            if w_mod != c % h:
                by_c_violation.setdefault(c, []).append((k, monom, coef, w_mod))
                all_good = False

    if all_good:
        print(f"  ✓ ALL monomials in U_c have index-weight ≡ c (mod h). "
              f"GRADING HOLDS.")
    else:
        for c in sorted(by_c_violation):
            n = len(by_c_violation[c])
            print(f"  ✗ c={c}: {n} violating monomials")
            for k, m, coef, w in by_c_violation[c][:3]:
                print(f"      y^{k}: monom {m} coef {coef} weight {w} (expect c={c%h})")
    return all_good


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, required=True)
    parser.add_argument("--p", type=int, default=193)
    parser.add_argument("--rho", type=int, default=None)
    args = parser.parse_args()
    rho_val = args.rho or sorted(find_rho(args.p))[0]
    check_grading(args.h, args.p, rho_val)


if __name__ == "__main__":
    main()
