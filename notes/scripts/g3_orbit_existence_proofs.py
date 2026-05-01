"""Direct structural proofs of orbit existence/non-existence at various h.

For each (h, d) with d | h, restrict chain to length-d candidate slice
(x_a = 0 unless (h/d) | a), solve resulting smaller system, count solutions.
"""
import sympy as sp

def chain_at_slice(h, d):
    """Return chain restricted to length-d slice (only x_{j(h/d)} nonzero)."""
    if h % d != 0:
        return None, None
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
    # Slice: x_a = 0 unless (h/d) | a
    hd = h // d
    sub = {x[a - 1]: 0 for a in range(1, h) if a % hd != 0}
    chain_slice = [sp.expand(c.subs(sub)) for c in chain]
    nontrivial = [c for c in chain_slice if c != 0]
    free_vars = [x[a - 1] for a in range(1, h) if a % hd == 0]
    return nontrivial, free_vars


def count_orbit(h, d, char=0):
    """Count number of length-d orbit candidate solutions."""
    chain_slice, free_vars = chain_at_slice(h, d)
    if chain_slice is None:
        return None
    if not chain_slice:
        return ("any", "no constraints")
    # Solve over algebraic closure
    try:
        sols = sp.solve(chain_slice, free_vars, dict=True)
    except Exception as e:
        return f"solve error: {e}"
    # Count nontrivial solutions
    nontrivial_sols = [s for s in sols if any(s.get(v, 0) != 0 for v in free_vars)]
    return len(nontrivial_sols), len(sols), [{str(k): v for k, v in s.items()} for s in nontrivial_sols[:5]]


print("Orbit existence at various (h, d) with d | h:\n")
for h in [4, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18]:
    print(f"h = {h}:")
    divs = [d for d in range(1, h+1) if h % d == 0]
    for d in divs:
        if d == 1:
            continue  # trivial orbit always exists
        chain_slice, free_vars = chain_at_slice(h, d)
        if chain_slice is None:
            continue
        # Don't actually solve at high d (= long); use heuristic
        if len(free_vars) > 4:
            print(f"  d={d}: |free_vars| = {len(free_vars)}, slice has {len(chain_slice)} eqs (skip solve)")
            continue
        result = count_orbit(h, d)
        print(f"  d={d}, h/d={h//d}: {result}, free_vars: {[str(v) for v in free_vars]}, eqs (sliced): {chain_slice}")
    print()
