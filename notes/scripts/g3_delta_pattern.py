"""g3_delta_pattern.py — derive C_k constraint in W-form (h-uniform), then δ_k.

Per Note 0254:
  - Build chain x_c = W_c + corrections in W's, by iterating y0 c.
  - At step k: derive cubic_k_constraint = (W-poly) by substituting chain into y2_k.
  - δ_k_in_W := 7 V_k_in_W - cubic_k_constraint_in_W.
  - This δ_k is h-UNIFORM (depends only on chain, not on h).
  - Convert to x-form via inverse chain (W_c = x_c + 4 x_1², ...).
  - Test δ_k_in_x ∈ (x_1²).

This stays purely abstract in W's; no h-dependent X³ truncation.
"""
from __future__ import annotations

import argparse
import sympy as sp


def build_chain(K):
    """Iteratively build:
      - subs[x_c] = expr in W_1, ..., W_c (forward chain)
      - cubic_constraint[k] = expr in W_1, ..., W_k from y2_k after chain.

    The y0 chain: 4 y0_c = (x_c - W_c) + 3 V_c + 2 (X·W)_c - (W²)_c = 0.
    The y2 chain: 2 y2_c = 3 x_c - 3 W_c - 2 V_c + 2 cubic_c = 0.

    Sub x_1, ..., x_{c-1} via chain into BOTH y0_c and y2_c, eliminate x_c:
      y0_c gives x_c = W_c - 3 V_c - 2 (X·W)_c + (W²)_c.
      y2_c gives 3 x_c - 3 W_c - 2 V_c + 2 cubic_c = 0.
    Combine:
      3 (W_c - 3 V_c - 2 (X·W)_c + (W²)_c) - 3 W_c - 2 V_c + 2 cubic_c = 0
      ⟹ 2 cubic_c = 9 V_c + 6 (X·W)_c - 3 (W²)_c + 2 V_c
                 = 11 V_c + 6 (X·W)_c - 3 (W²)_c.
      ⟹ cubic_c = (11 V_c + 6 (X·W)_c - 3 (W²)_c) / 2.

    Hmm wait for c=1: V_1 = 0, (X·W)_1 = 0, (W²)_1 = 0, so cubic_1 = 0.
    For c=2: V_2 = x_1², (X·W)_2 = x_1 W_1, (W²)_2 = W_1². With x_1 = W_1:
      cubic_2 = (11 W_1² + 6 W_1² - 3 W_1²) / 2 = 14 W_1² / 2 = 7 W_1². ✓ matches Note.
    """
    W = [sp.Symbol(f"W{i}") for i in range(K + 2)]
    x = [sp.Symbol(f"x{i}") for i in range(K + 2)]

    subs = {}  # x_c → expr in W's
    cubic_constraint = {}  # cubic_c (= [z^{2h+c}] X³ on V(I)) as W-poly

    for c in range(1, K + 1):
        # V_c = sum_{a+b=c, a,b≥1} x_a x_b — full sum (so x_1 x_2 + x_2 x_1 = 2 x_1 x_2 etc.)
        Vc = sp.Add(*[x[a] * x[c - a] for a in range(1, c) if c - a >= 1], sp.Integer(0))
        XWc = sp.Add(*[x[a] * W[c - a] for a in range(1, c) if c - a >= 1], sp.Integer(0))
        WWc = sp.Add(*[W[a] * W[c - a] for a in range(1, c) if c - a >= 1], sp.Integer(0))

        # Apply chain to V, XW.  (W's are abstract, no chain.)
        Vc_chained = sp.expand(Vc.subs(subs))
        XWc_chained = sp.expand(XWc.subs(subs))

        # y0 elim: x_c = W_c - 3 V_c - 2 XW_c + WW_c
        x_c_expr = sp.expand(W[c] - 3 * Vc_chained - 2 * XWc_chained + WWc)
        subs[x[c]] = x_c_expr

        # y2 elim combined: cubic_c = (11 V_c + 6 XW_c - 3 WW_c) / 2
        cubic_c_expr = sp.expand((11 * Vc_chained + 6 * XWc_chained - 3 * WWc) / 2)
        cubic_constraint[c] = cubic_c_expr

    return W, x, subs, cubic_constraint


def deltas_in_W(K, verbose=False):
    """Compute δ_k_in_W = 7 V_k_in_W - cubic_constraint[k] for k = 2..K."""
    W, x, subs, cubic_constraint = build_chain(K)

    deltas_W = {}
    for k in range(2, K + 1):
        Vk = sp.Add(*[x[a] * x[k - a] for a in range(1, k) if k - a >= 1], sp.Integer(0))
        Vk_chained = sp.expand(Vk.subs(subs))
        delta_k_W = sp.expand(7 * Vk_chained - cubic_constraint[k])
        deltas_W[k] = delta_k_W
        if verbose:
            print(f"  k={k}: δ_k_in_W = {sp.factor(delta_k_W)}")

    return W, x, subs, deltas_W


def invert_chain(K, subs, x, W):
    """Compute W_c = expr in x_1, ..., x_c via inverse chain.

    Given x_c = W_c + (terms in W_1, ..., W_{c-1}), invert:
      W_c = x_c - (terms in W_1, ..., W_{c-1})
          = x_c - (terms after substituting W_a = expr in x's for a<c).
    """
    inv = {}  # W_c → expr in x's
    for c in range(1, K + 1):
        # subs[x_c] = W_c + corr. Solve W_c = x_c - corr, where corr is in
        # W_1, ..., W_{c-1}. After substituting inv (which maps W_a → x's),
        # we get W_c in x's.
        x_c_expr = subs[x[c]]
        # x_c = W_c + (rest); rest = x_c_expr - W_c.
        rest = sp.expand(x_c_expr - W[c])
        # W_c = x_c - rest, with rest evaluated via inv:
        rest_in_x = sp.expand(rest.subs(inv))
        W_c_expr = sp.expand(x[c] - rest_in_x)
        inv[W[c]] = W_c_expr
    return inv


def deltas_in_x(K, verbose=False):
    """Compute δ_k in x-form via inverse chain."""
    W, x, subs, deltas_W = deltas_in_W(K, verbose=False)
    inv = invert_chain(K, subs, x, W)

    deltas_x = {}
    for k in sorted(deltas_W):
        d_W = deltas_W[k]
        d_x = sp.expand(d_W.subs(inv))
        deltas_x[k] = d_x
        if verbose:
            df = sp.factor(d_x)
            s = str(df)
            if len(s) > 200: s = s[:200] + " ..."
            print(f"  k={k}: δ_k_in_x = {s}")

    return W, x, subs, inv, deltas_W, deltas_x


def x1_squared_test(d, x1):
    d_x1_0 = sp.expand(d.subs(x1, 0))
    d_dx1_0 = sp.expand(sp.diff(d, x1).subs(x1, 0))
    return (d_x1_0 == 0 and d_dx1_0 == 0), d_x1_0, d_dx1_0


def report(K, verbose=False):
    print(f"\n========== K = {K} (h-uniform W-form) ==========")
    W, x, subs, inv, deltas_W, deltas_x = deltas_in_x(K, verbose=verbose)

    print("\n--- Chain x_c in W's ---")
    for c in range(1, K + 1):
        print(f"  x_{c} = {sp.factor(subs[x[c]])}")

    print("\n--- Inverse chain W_c in x's ---")
    for c in range(1, K + 1):
        print(f"  W_{c} = {sp.factor(inv[W[c]])}")

    print("\n--- δ_k_in_W (h-uniform) ---")
    for k in sorted(deltas_W):
        df = sp.factor(deltas_W[k])
        s = str(df)
        if len(s) > 250: s = s[:250] + " ..."
        print(f"  δ_{k} (W) = {s}")

    print("\n--- δ_k_in_x and x_1² test ---")
    x1 = x[1]
    for k in sorted(deltas_x):
        d_x = deltas_x[k]
        in_sq, d0, d1 = x1_squared_test(d_x, x1)
        marker = "[x_1²]" if in_sq else "[NOT x_1²]"
        df = sp.factor(d_x)
        s = str(df)
        if len(s) > 250: s = s[:250] + " ..."
        print(f"\n  k = {k}: {marker}")
        print(f"    δ_{k} = {s}")
        if in_sq:
            try:
                quot, _ = sp.div(d_x, x1**2, x1)
                qf = sp.factor(quot)
                qs = str(qf)
                if len(qs) > 250: qs = qs[:250] + " ..."
                print(f"    δ_{k} / x_1² = {qs}")
            except Exception:
                pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--K", type=int, default=8)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    report(args.K, verbose=args.verbose)


if __name__ == "__main__":
    main()
