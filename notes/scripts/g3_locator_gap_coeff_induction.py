"""g3_locator_gap_coeff_induction.py — automated coefficient induction.

For (3k/2, 2k) at n=4k, k=2h, prove the locator-gap lemma by symbolic
recursion. Output:
  - R coefficients in terms of P low coefs (ρ, P_0, ..., P_{2h-1}).
  - The (P*R)_m = 0 equations for m ∈ [0, 4h-1].
  - The smallest "bad characteristic" needed for case-A elimination.

Approach mimics Note 0223's hand derivation at h=2.
"""
import sympy as sp


def setup(h):
    rho = sp.Symbol("rho")
    p = sp.symbols(f"p0:{2*h}")  # P_0, ..., P_{2h-1} (low coefs)
    # P_d for d ∈ [2h, 4h-1] \ {3h} are 0; P_{3h} = rho; P_{4h} = 1.
    P = [None] * (4 * h + 1)
    for d in range(2 * h):
        P[d] = p[d]
    for d in range(2 * h, 4 * h):
        P[d] = rho if d == 3 * h else sp.Integer(0)
    P[4 * h] = sp.Integer(1)
    return rho, p, P


def recurse_R(h, rho, p, P):
    """Compute R_d for d = 4h, 4h-1, ..., 0 from (P*R)_m = 0 at m = 8h-1, ..., 4h."""
    R = [None] * (4 * h + 1)
    R[4 * h] = sp.Integer(1)
    # m = 8h - d for d ∈ [1, 4h]
    for d in range(1, 4 * h + 1):
        # R_{4h-d} = -P_{4h-d} - sum_{l=1}^{d-1} P_{4h-l} R_{4h-d+l}
        rhs = -P[4 * h - d]
        for l in range(1, d):
            rhs -= P[4 * h - l] * R[4 * h - d + l]
        R[4 * h - d] = sp.expand(rhs)
    return R


def low_eqs(h, rho, p, P, R):
    """Compute (P*R)_m for m ∈ [0, 4h-1]. Each must = δ_{m,0} · (-1)."""
    eqs = []
    for m in range(4 * h):
        # (P*R)_m = sum_{i+j=m, 0<=i,j<=4h} P_i R_j = sum_{i=0}^m P_i R_{m-i}
        s = sp.Integer(0)
        for i in range(m + 1):
            if i <= 4 * h and m - i <= 4 * h:
                s += P[i] * R[m - i]
        s = sp.expand(s)
        target = sp.Integer(-1) if m == 0 else sp.Integer(0)
        eqs.append((m, sp.expand(s - target)))
    return eqs


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--h", type=int, default=2)
    parser.add_argument("--show-R", action="store_true")
    parser.add_argument("--show-eqs", action="store_true")
    args = parser.parse_args()

    h = args.h
    rho, p, P = setup(h)
    R = recurse_R(h, rho, p, P)

    print(f"=== h={h}, k={2*h}, n={8*h}, deg P = {4*h} ===")

    if args.show_R:
        print("\nR coefficients (in terms of ρ, p_0, ..., p_{2h-1}):")
        for d in range(4 * h + 1):
            print(f"  R_{d} = {R[d]}")

    eqs = low_eqs(h, rho, p, P, R)
    print(f"\n(P*R)_m equations for m ∈ [0, {4*h-1}]:")
    for m, eq in eqs:
        if eq == 0:
            print(f"  m={m}: 0 (automatic)")
        elif args.show_eqs:
            print(f"  m={m}: {eq} = 0")
        else:
            print(f"  m={m}: <{len(sp.Add.make_args(eq))} terms>")

    # Solve the system using groebner over rho, p_*
    print("\nSolving via Groebner basis (lex, ρ last)...")
    nontriv_eqs = [eq for _, eq in eqs if eq != 0]
    G = sp.groebner(nontriv_eqs, *p, rho, order="lex")
    print(f"  GB has {len(G)} polynomials")
    # Find ρ-only poly (eliminator)
    elim = [g for g in G if all(s not in g.free_symbols for s in p)]
    print(f"  Eliminator (ρ-only): {elim}")

    # Show which p_d are forced to 0 modulo the GB
    print("\nLocator gap check — reduction of p_d for d ∉ {0, h}:")
    for d in range(2 * h):
        if d in (0, h):
            continue
        try:
            rem = sp.Poly(G.reduce(p[d])[1], *p, rho).as_expr() if hasattr(G, 'reduce') else "?"
        except Exception:
            rem = "?"
        # Try simpler: see if p_d ∈ ideal
        try:
            rem = G.reduce(p[d])[1]
        except Exception:
            rem = "?"
        print(f"  p_{d} reduces to: {rem}")


if __name__ == "__main__":
    main()
