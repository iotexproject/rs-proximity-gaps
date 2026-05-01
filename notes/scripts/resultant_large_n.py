#!/usr/bin/env python3
"""Compute G(t) for large n with w|n, verify deg(G) = q-2 and G irreducible."""

from sympy import Symbol, Poly, Integer, resultant, ZZ, QQ
from math import gcd
from functools import reduce
import time

s1 = Symbol('s1')
sw = Symbol('sw')
t = Symbol('t')

def zpoly_zero(): return {}
def zpoly_const(c): return {} if c == 0 else {(0,0): int(c)}
def zpoly_var(idx):
    key = [0,0]; key[idx] = 1; return {tuple(key): 1}
def zpoly_add(f, g):
    r = dict(f)
    for k, v in g.items():
        r[k] = r.get(k, 0) + v
        if r[k] == 0: del r[k]
    return r
def zpoly_sub(f, g):
    r = dict(f)
    for k, v in g.items():
        r[k] = r.get(k, 0) - v
        if r[k] == 0: del r[k]
    return r
def zpoly_mul(f, g):
    r = {}
    for (a1,b1), c1 in f.items():
        for (a2,b2), c2 in g.items():
            key = (a1+a2, b1+b2)
            r[key] = r.get(key, 0) + c1*c2
            if r[key] == 0: del r[key]
    return r
def zpoly_scale(f, c):
    if c == 0: return {}
    return {k: v*c for k, v in f.items() if v*c != 0}

def compute_ri_bivariate_Z(n, w):
    eps = (-1)**(w+1)
    sigma1 = zpoly_var(0); sigmaw = zpoly_var(1)
    c_polys = [zpoly_zero() for _ in range(w)]
    c_polys[0] = zpoly_scale(sigmaw, eps)
    c_polys[w-1] = sigma1
    state = [zpoly_zero() for _ in range(w)]
    state[0] = zpoly_const(1)
    for step in range(n):
        top = state[w-1]
        new_state = [None]*w
        new_state[0] = zpoly_mul(top, c_polys[0])
        for j in range(1, w):
            new_state[j] = zpoly_add(state[j-1], zpoly_mul(top, c_polys[j]))
        state = new_state
    return state

def zpoly_to_sympy(f):
    if not f: return Integer(0)
    return sum(Integer(c) * s1**a * sw**b for (a,b), c in f.items())

def analyze(n, w):
    q = n // w
    print(f"\nn={n}, w={w}, q={q}, D={n-w+1}")
    
    t0 = time.time()
    r_all = compute_ri_bivariate_Z(n, w)
    r0m1 = zpoly_sub(r_all[0], zpoly_const(1))
    r1 = r_all[1]
    t_ri = time.time() - t0
    print(f"  r_i computation: {t_ri:.1f}s, #terms(r0m1)={len(r0m1)}, #terms(r1)={len(r1)}")

    r0m1_expr = zpoly_to_sympy(r0m1)
    r1_expr = zpoly_to_sympy(r1)

    t1 = time.time()
    res_expr = resultant(r0m1_expr, r1_expr, sw)
    t_res = time.time() - t1
    
    res_poly = Poly(res_expr, s1, domain=ZZ)
    res_deg = res_poly.degree()
    res_coeffs = res_poly.all_coeffs()
    content = reduce(gcd, [abs(int(c)) for c in res_coeffs if c != 0])
    print(f"  Resultant: deg={res_deg}, content={content}, time={t_res:.1f}s")

    # Remove content and extract primitive part
    if content > 1:
        prim_coeffs = [int(c)//content for c in res_coeffs]
    else:
        prim_coeffs = [int(c) for c in res_coeffs]

    # Find multiplicity of s1=0
    k = 0
    while k < len(prim_coeffs) and prim_coeffs[-(k+1)] == 0:
        k += 1
    # but prim_coeffs might end with the constant, let me do it properly
    k = 0
    for i in range(res_deg, -1, -1):
        idx = res_deg - i
        if idx < len(prim_coeffs) and prim_coeffs[idx] != 0:
            break
    # Actually just check from the lowest degree
    k = 0
    rev = list(reversed(prim_coeffs))  # rev[0] = constant, rev[1] = coeff of s1, ...
    while k < len(rev) and rev[k] == 0:
        k += 1
    
    print(f"  s1^k factor: k={k}")
    print(f"  Predicted k = n-q = {n-q}")

    # Extract the remaining factor (after removing s1^k)
    if k > 0:
        remaining_coeffs = prim_coeffs[:res_deg - k + 1]
    else:
        remaining_coeffs = prim_coeffs
    
    rem_deg = len(remaining_coeffs) - 1
    
    # Check G(s1^n) structure: nonzero coeffs should be at positions divisible by n
    nonzero_positions = []
    for i, c in enumerate(remaining_coeffs):
        if c != 0:
            exp = rem_deg - i
            nonzero_positions.append(exp)
    
    print(f"  Remaining factor: degree {rem_deg}")
    print(f"  Nonzero exponent positions: {nonzero_positions}")
    
    if all(e % n == 0 for e in nonzero_positions):
        print(f"  *** G(s1^{n}) CONFIRMED ***")
        G_coeffs = {}
        for i, c in enumerate(remaining_coeffs):
            if c != 0:
                exp = rem_deg - i
                G_coeffs[exp // n] = c
        G_deg = max(G_coeffs.keys())
        print(f"  deg(G) = {G_deg}")
        print(f"  Predicted deg(G) = q-2 = {q-2}")
        
        # Build G as sympy polynomial
        G_expr = sum(Integer(c) * t**e for e, c in G_coeffs.items())
        print(f"  G(t) = {G_expr}")
        
        # Factor G over Q
        t2 = time.time()
        G_fl = Poly(G_expr, t, domain=QQ).factor_list()
        t_fac = time.time() - t2
        G_factors = [(Poly(f, t).degree(), m) for f, m in G_fl[1]]
        is_irred = (len(G_fl[1]) == 1 and G_fl[1][0][1] == 1)
        print(f"  G factors: {G_factors}, irreducible={is_irred}, time={t_fac:.1f}s")
        
        return {'n': n, 'w': w, 'q': q, 'k': k, 'deg_G': G_deg, 
                'G_irred': is_irred, 'G_str': str(G_expr)[:100]}
    else:
        # Check other periods
        diffs = [nonzero_positions[i] - nonzero_positions[i+1] 
                for i in range(len(nonzero_positions)-1)] if len(nonzero_positions) > 1 else [0]
        period = reduce(gcd, diffs) if diffs and all(d > 0 for d in diffs) else 0
        print(f"  NOT G(s1^n). Period of exponents: {period}")
        return {'n': n, 'w': w, 'q': q, 'k': k, 'deg_G': -1, 'G_irred': None, 'G_str': 'N/A'}

# Focus on w|n cases with w=3,4,5
configs = []
for w in [3, 4, 5]:
    for q in range(3, 15):
        n = w * q
        if n > 100:
            break
        configs.append((n, w))

# Also add a few w=6,7 cases
for w in [6, 7]:
    for q in [3, 4, 5]:
        configs.append((w*q, w))

results = []
for n, w in configs:
    try:
        r = analyze(n, w)
        if r:
            results.append(r)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"  ERROR: {e}")

# Summary
print(f"\n\n{'='*80}")
print("SUMMARY TABLE (w|n cases)")
print(f"{'='*80}")
print(f"{'n':>4} {'w':>3} {'q':>3} {'k':>5} {'k=n-q?':>7} {'deg(G)':>7} {'q-2':>4} {'G_irred':>8} {'G(t)':>40}")
for r in results:
    k_match = "Y" if r['k'] == r['n'] - r['q'] else "N"
    dg_match = "Y" if r['deg_G'] == r['q'] - 2 else ("?" if r['deg_G'] < 0 else "N")
    gi = "Y" if r['G_irred'] else ("?" if r['G_irred'] is None else "N")
    print(f"{r['n']:>4} {r['w']:>3} {r['q']:>3} {r['k']:>5} {k_match:>7} {r['deg_G']:>7} {r['q']-2:>4} {gi:>8} {r['G_str'][:40]:>40}")
