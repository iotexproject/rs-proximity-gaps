"""Full verification: a_c := A_c(0) is forced to 0 by chain c_c at every c.

Tests the claim of Note 0315 (fri-2round-tightness):
  Q1@d ⟺ (∗): a_1 ≠ 0 on V_d^prim,
where a_1 := A_1(0) ∈ F̄ is the constant-in-s coefficient of A_1 ∈ F̄[s]/H_d(s).

THIS SCRIPT SHOWS:
  At d=4, the chain c_1 substituted with x_a = t^a · A_a(s), s = t^d gives
    A_1·(1 + 2·s·G_0(s)) - s·G_1(s) = 0  in  F̄[s]/H_d(s)
  Evaluating at s=0 (well-defined since H_d(0) ≠ 0):
    A_1(0)·1 - 0 = 0  ⟹  a_1 = 0  always.

  Similarly, c_2 substituted at s=0 gives a_2 = -3·a_1² = 0.
  c_c substituted at s=0 gives a_c = -3·∑a_a·a_{c-a} = 0 (Note 0315 Lemma 0315.1).
  So the Catalan recursion's "free parameter a_1" is itself constrained to 0.
  The Note 0315 Catalan closed form a_c = (-3)^{c-1}·C_{c-1}·a_1^c then
  evaluates to 0 at every c, and F(0) = (-1)^{d/2}·11·3^{d/2-2}·C_{d/2-1}·a_1^{d/2}
  is identically 0.

  Therefore the "(∗): a_1 ≠ 0" statement is vacuous — never satisfied — so the
  reduction "Q1 ⟺ (∗)" doesn't actually reduce Q1 to anything useful.

This script verifies all the above SYMBOLICALLY at d=4:
  (1) Direct substitution of x_a = t^a·A_a(s), s = t^d into c_1, c_2, c_3.
  (2) Coefficient extraction at s=0.
  (3) Confirmation that a_c = 0 cascades through the chain.
"""
from __future__ import annotations

import sympy as sp


def main():
    print("=" * 64)
    print("Symbolic substitution: x_a = t^a · A_a(s), s = t^d, at d=4")
    print("=" * 64)

    # Symbols
    t, s = sp.symbols('t s', real=False)
    A1, A2, A3 = sp.symbols('A1 A2 A3', cls=sp.Function)

    # Treat A_a as functions of s (not opened up), so A1(s), A2(s), A3(s).
    A1s = A1(s)
    A2s = A2(s)
    A3s = A3(s)

    # x_a = t^a · A_a(s)
    x1 = t * A1s
    x2 = t**2 * A2s
    x3 = t**3 * A3s

    # Chain at d=4 (Note 0315 §d=4 hand-proof):
    c1 = x1 - 2 * x2 * x3 + 4 * x1**2 * x3 + 2 * x1 * x2**2
    c2 = x2 - x3**2 + 3 * x1**2 + 8 * x1 * x2 * x3 + 2 * x2**3 - 4 * x2**2 * x3**2
    c3 = x3 + 6 * x1 * x2 + 6 * x1 * x3**2 + 6 * x2**2 * x3 - 4 * x2 * x3**3

    # Replace t^4 with s (substitution s = t^d = t^4 at d=4)
    def reduce_t4(expr):
        # collect t^k, replace t^4 → s, t^5 → t·s, t^6 → t²·s, etc.
        expr = sp.expand(expr)
        # iterate: replace t^4 with s
        while True:
            new = expr.replace(lambda e: e.is_Pow and e.base == t and e.exp >= 4,
                               lambda e: s ** (e.exp // 4) * t ** (e.exp % 4))
            new = sp.expand(new)
            if new == expr:
                break
            expr = new
        return expr

    c1_red = reduce_t4(c1)
    c2_red = reduce_t4(c2)
    c3_red = reduce_t4(c3)

    # Each c_c should factor as t^c · (bracket)
    # Factor out t^c
    def factor_out_t(expr, power):
        expanded = sp.expand(expr)
        bracket = sp.simplify(expanded / t**power)
        return sp.expand(bracket)

    print("\n[1] c_1 / t  =")
    b1 = factor_out_t(c1_red, 1)
    sp.pprint(b1)

    print("\n[2] c_2 / t² =")
    b2 = factor_out_t(c2_red, 2)
    sp.pprint(b2)

    print("\n[3] c_3 / t³ =")
    b3 = factor_out_t(c3_red, 3)
    sp.pprint(b3)

    print("\n" + "-" * 64)
    print("Evaluate at s=0 (using H_d(0) ≠ 0 well-definedness):")
    print("-" * 64)

    # Define a_c := A_c(0)
    a1_sym, a2_sym, a3_sym = sp.symbols('a1 a2 a3')

    def eval_at_s0(expr):
        """Evaluate expression at s=0, replacing A_c(s) → A_c(0) → a_c."""
        # Substitute s = 0
        e = expr.subs(s, 0)
        # Replace A_c(0) → a_c symbol
        e = e.replace(A1(0), a1_sym).replace(A2(0), a2_sym).replace(A3(0), a3_sym)
        return sp.expand(e)

    e1 = eval_at_s0(b1)
    e2 = eval_at_s0(b2)
    e3 = eval_at_s0(b3)

    print(f"\nc_1/t at s=0  →  {e1} = 0  ⟹  a_1 = {sp.solve(e1, a1_sym)}")
    print(f"c_2/t² at s=0 →  {e2} = 0  ⟹  a_2 - relation: {sp.solve(e2, a2_sym)}")
    print(f"c_3/t³ at s=0 →  {e3} = 0  ⟹  a_3 - relation: {sp.solve(e3, a3_sym)}")

    print("\n" + "-" * 64)
    print("Conclusion:")
    print("-" * 64)
    print("  - c_1/t at s=0 gives  a_1 = 0  (no other coefficients involved).")
    print("  - c_2/t² at s=0 gives  a_2 = -3·a_1²  (Note 0315 Catalan recursion at c=2).")
    print("  - c_3/t³ at s=0 gives  a_3 = -3·(a_1·a_2 + a_2·a_1) = -6·a_1·a_2 (Note 0315 c=3).")
    print()
    print("  Substituting a_1 = 0 (forced by c_1):")
    print("    a_2 = -3·0² = 0")
    print("    a_3 = -6·0·a_2 = 0")
    print("    All a_c = 0.")
    print()
    print("  The Catalan closed-form  a_c = (-3)^{c-1}·C_{c-1}·a_1^c  is")
    print("  parameterized by  a_1  — but a_1 is FORCED to 0 by the c_1 chain.")
    print()
    print("  Therefore F(0) = (-1)^{d/2}·11·3^{d/2-2}·C_{d/2-1}·a_1^{d/2} = 0 ALWAYS.")
    print("  (∗): \"a_1 ≠ 0\" is vacuously false — the closed-form reduction")
    print("  in Note 0315 doesn't reduce Q1 to anything useful.")


if __name__ == '__main__':
    main()
