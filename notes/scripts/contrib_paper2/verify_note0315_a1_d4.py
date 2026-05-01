"""Verify the a_1 = A_1(0) claim of Note 0315 (fri-2round-tightness branch).

Note 0315 asserts:
  Q1@d reduces to (∗): a_1 ≠ 0 on every Galois-orbit of V_d^prim,
  with a_1 := A_1(0) and closed form
    F(0) = (-1)^{d/2} · 11 · 3^{d/2-2} · C_{d/2-1} · a_1^{d/2}.

Concern: substituting x_a = t^a · A_a(s), s = t^d into chain c_1 at d=4 gives
  c_1 = t·[A_1·(1 + 2sG_0) - sG_1].
Modulo H_d(s) (which has H_d(0) ≠ 0), evaluating at s=0:
  A_1(0)·1 = 0,  i.e.,  a_1 = 0  always.

If this holds, the closed form is identically 0 and the (∗) reduction is
malformed — the actual non-vanishing condition is "A_1 ≠ 0 in F̄[s]/H_d(s)",
not "A_1(0) ≠ 0 in F̄".

This script tests at d=4 numerically:
  (a) Find a length-4 orbit on V(I_chain^4).
  (b) Pick orbit-leading t (smallest |x_1/A_1| candidate).
  (c) Sample multiple distinct length-4 orbits → distinct s = t^d values.
  (d) Use the (s, x_1/t) pairs to interpolate A_1(s) ∈ F̄[s] (deg ≤ 1 since
      φ(4) = 2 ⟹ deg H_d = 2 ⟹ A_1 has at most 2 free coefficients).
  (e) Read off A_1(0).

If A_1(0) is consistently 0 across orbits, Note 0315's a_1 := A_1(0) is
forced 0 and the closed form fails.

Strategy alternative: verify directly via the chain identity. Plug a known
length-4 orbit point into  A_1·(1+2sG_0) - sG_1, with A_1 := x_1/t,
s = t^4, etc. This expression must vanish. Then reading A_1 = sG_1/(1+2sG_0)
and evaluating at s=0 gives A_1(0)=0.
"""
from __future__ import annotations

import random
from math import gcd
from functools import reduce

import numpy as np
import sympy as sp
from scipy.optimize import fsolve


def build_chain_d4():
    """Build the d=4 chain explicitly (matches Note 0315 §d=4 hand-proof)."""
    x1, x2, x3 = sp.symbols('x1 x2 x3', real=False)
    # From Note 0315 hand-proof:
    c1 = x1 - 2 * x2 * x3 + 4 * x1**2 * x3 + 2 * x1 * x2**2
    c2 = x2 - x3**2 + 3 * x1**2 + 8 * x1 * x2 * x3 + 2 * x2**3 - 4 * x2**2 * x3**2
    c3 = x3 + 6 * x1 * x2 + 6 * x1 * x3**2 + 6 * x2**2 * x3 - 4 * x2 * x3**3
    return [c1, c2, c3], (x1, x2, x3)


def classify_orbit_length(sol, d, eps=1e-6):
    nz = [a for a in range(1, d) if abs(sol[a - 1]) > eps]
    if not nz:
        return 1
    g = reduce(gcd, nz)
    return d // g


def find_length_d_orbits(d=4, n_trials=80, seed=42):
    """Find numerical length-d orbit points (real-valued)."""
    chain, vars_ = build_chain_d4()
    chain_fn = sp.lambdify(vars_, chain, 'numpy')

    def F(v):
        return np.array(chain_fn(*v), dtype=float)

    rng = random.Random(seed)
    orbits = []
    for trial in range(n_trials):
        x0 = np.array([rng.uniform(-0.6, 0.6) for _ in vars_])
        try:
            sol, info, ier, msg = fsolve(F, x0, full_output=True, xtol=1e-12, maxfev=8000)
            if ier != 1:
                continue
            if np.linalg.norm(F(sol)) > 1e-8:
                continue
            if classify_orbit_length(sol, d) != d:
                continue
            # Deduplicate (orbit by orbit)
            key = tuple(sorted([round(abs(v), 4) for v in sol]))
            if any(np.allclose(o['key'], key, atol=1e-3) for o in orbits):
                continue
            orbits.append({'sol': sol, 'key': key})
            if len(orbits) >= 5:
                break
        except Exception:
            continue
    return orbits


def extract_t_and_A_at_orbit(sol, d=4):
    """At a length-d orbit point, extract t (orbit-leading) and A_a(s) values.

    On the orbit, x_a = t^a · A_a(s) where s = t^d. This isn't unique — the
    Z/d Galois action sends t -> ω·t (ω primitive d-th root of unity). For
    REAL solutions, t is most naturally the value that makes A_a's "small"
    relative to t^a. We'll just pick t such that A_1 = x_1/t and then verify
    consistency with A_2 = x_2/t^2, A_3 = x_3/t^3.

    Note: if x_1 ≠ 0, taking t such that A_1 = 1 forces t = x_1, then
    A_2 = x_2/x_1^2, A_3 = x_3/x_1^3. This is one normalization choice.

    Alternative: use t = some "natural" parameter. We'll just compute
    s = t^d and (A_1, A_2, A_3) for various t-choices and check the
    closed-form predictions.

    Returns dict of {'t': t, 'A1': A1, 'A2': A2, 'A3': A3, 's': s}
    using t = x_1 / A_1_assumed = x_1 (if we set A_1 = 1).
    """
    x1, x2, x3 = sol
    # Normalization 1: set A_1 = 1, so t = x_1, s = t^d.
    # Then A_2 = x_2/t^2, A_3 = x_3/t^3.
    t = x1
    s = t**d
    A1 = 1.0
    A2 = x2 / t**2 if abs(t) > 1e-8 else None
    A3 = x3 / t**3 if abs(t) > 1e-8 else None
    return {'sol': sol, 't': t, 's': s, 'A1': A1, 'A2': A2, 'A3': A3}


def check_a1_via_chain_identity(d=4):
    """At a length-d orbit, the chain c_1 says
      A_1 (1 + 2 s G_0) = s G_1
    where G_0(s) = sum_{i+j=d, 1≤i,j≤d-1} A_i A_j evaluated at s,
          G_1(s) = sum_{i+j=d+1, 1≤i,j≤d-1} A_i A_j.

    This script numerically checks (a) the identity holds at sampled orbits,
    and (b) what A_1 evaluated at s=0 would be (if we had multiple orbits to
    interpolate s-polynomials).
    """
    print("=" * 64)
    print(f"d = {d}: chain c_1 identity check")
    print("=" * 64)

    orbits = find_length_d_orbits(d=d, n_trials=200)
    print(f"Found {len(orbits)} distinct length-{d} orbits.")
    if not orbits:
        return

    # For each orbit, normalize A_1 = 1 (so t = x_1), get s, A_2, A_3.
    rows = []
    for orbit in orbits:
        info = extract_t_and_A_at_orbit(orbit['sol'], d=d)
        rows.append(info)
        print(f"\n  orbit: x = {orbit['sol']}")
        print(f"    t = x_1 = {info['t']:.6g}")
        print(f"    s = t^{d} = {info['s']:.6g}")
        print(f"    (A_1, A_2, A_3) = (1, {info['A2']:.6g}, {info['A3']:.6g})")

        # Chain c_1 identity: A_1·(1 + 2s G_0) - s G_1 = 0?
        # G_0 = 2 A_1 A_3 + A_2^2 (i+j=4: (1,3) twice + (2,2))
        # G_1 = 2 A_2 A_3 (i+j=5: (2,3) twice)
        A1, A2, A3 = info['A1'], info['A2'], info['A3']
        s = info['s']
        G0 = 2 * A1 * A3 + A2**2
        G1 = 2 * A2 * A3
        lhs = A1 * (1 + 2 * s * G0)
        rhs = s * G1
        residual = lhs - rhs
        print(f"    A_1·(1 + 2s·G_0) = {lhs:.6g}")
        print(f"    s · G_1          = {rhs:.6g}")
        print(f"    residual (should be 0): {residual:.3e}")

    # Now: the question of "A_1(0)". We have orbits giving (s_k, A_1_k=1) pairs.
    # But A_1 is normalized to 1 at every orbit. Different normalization!
    # The right approach: use a NATURAL parameterization that's orbit-independent.
    #
    # In Note 0315's framing, A_a(s) ∈ F̄[s]/H_d(s) is a SINGLE polynomial that
    # works on the variety V_d^prim. Different orbits correspond to different
    # values of s, but A_a(s) is the SAME function.
    #
    # If we have orbit 1 with s = s_1 and orbit 2 with s = s_2, and we extract
    # x_1/t at each (with consistent t-choice), we get (A_1)(s_1) and (A_1)(s_2).
    # Then we can interpolate A_1(s) as a polynomial in s.
    #
    # But the t-choice MATTERS: different orbits have DIFFERENT s-values, but
    # the t-choice itself is normalized per-orbit (Z/d acts on the orbit, so
    # t is only defined up to ω^k for a primitive d-th root ω).
    #
    # CRITICAL: my "set A_1 = 1, t = x_1" normalization makes A_1 ≡ 1 by fiat.
    # So I cannot extract A_1(0) this way.
    #
    # Correct approach: pick a DIFFERENT normalization that doesn't depend on
    # A_1. E.g., set A_3 = 1 (so t = x_3^{1/3}), then read A_1 = x_1 / t.
    print("\n" + "-" * 64)
    print("Re-normalization with t = x_3^{1/3} (set A_3 = 1):")
    print("-" * 64)
    rows2 = []
    for orbit in orbits:
        x1, x2, x3 = orbit['sol']
        if abs(x3) < 1e-8:
            continue
        # t = x_3^(1/3), then A_3 = 1, A_1 = x_1/t, A_2 = x_2/t^2, s = t^d.
        # Use real cube root.
        t = np.sign(x3) * abs(x3) ** (1.0 / 3)
        s = t ** d
        A1 = x1 / t
        A2 = x2 / t**2
        A3 = x3 / t**3
        rows2.append({'s': s, 'A1': A1, 'A2': A2, 'A3': A3})
        print(f"  orbit x={orbit['sol']}: t={t:.6g}, s={s:.6g}, A_1={A1:.6g}, A_2={A2:.6g}, A_3={A3:.6g}")

    if len(rows2) >= 2:
        print("\nInterpolation: fit A_1(s) ≈ c_0 + c_1·s via least squares.")
        s_vals = np.array([r['s'] for r in rows2])
        A1_vals = np.array([r['A1'] for r in rows2])
        # Linear fit
        coeffs = np.polyfit(s_vals, A1_vals, 1)  # [c_1, c_0]
        c1_fit, c0_fit = coeffs
        print(f"  fit:  A_1(s) ≈ {c0_fit:.6g} + {c1_fit:.6g}·s")
        print(f"  ⟹ A_1(0) ≈ {c0_fit:.6g}")
        if abs(c0_fit) < 1e-3:
            print(f"  ✓ consistent with a_1 := A_1(0) = 0 (Note 0315 closed form vacuous)")
        else:
            print(f"  ✗ A_1(0) appears nonzero — Note 0315's reduction may be valid")


if __name__ == '__main__':
    check_a1_via_chain_identity(d=4)
