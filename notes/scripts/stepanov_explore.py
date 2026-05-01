#!/usr/bin/env python3
"""
Stepanov method exploration for companion matrix gcd bound.

CORE QUESTION: Why is gcd(r0-1, r1, r2) = O(1) instead of O(n)?

APPROACH:
1. Study the factorization of r0-1, r1, r2 — do they share common factors?
2. At the solutions where gcd > 0: what 3-subsets of L give the roots?
3. The determinant identity Res(h, g_t) = s3^n constrains solutions:
   s3(t0)^n = 1, giving n candidate t-values.
   Among these, how many also satisfy r0=1, r1=0, r2=0?
4. Companion matrix rank-1 perturbation: C(t) = C_0 + t*(rank-1 matrix).
   This structure should constrain the common zeros.
5. STEPANOV: try to construct auxiliary polynomial P(r0,r1,r2,s1,s2,s3,t) = 0
   that vanishes with high multiplicity at solutions and has low degree.

Uses multiprocessing for parallel computation on the 28-core Studio.
"""

import itertools
import random
from collections import Counter, defaultdict
import multiprocessing as mp
import time

def primitive_root(p):
    for g in range(2, p):
        if all(pow(g, (p-1)//q, p) != 1 for q in prime_factors(p-1)):
            return g
def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0: factors.add(d); n //= d
        d += 1
    if n > 1: factors.add(n)
    return factors
def find_omega(p, n):
    g = primitive_root(p)
    return pow(g, (p-1)//n, p)

# Poly arithmetic over F_p[t]
def poly_add(a,b,p):
    n=max(len(a),len(b)); r=[0]*n
    for i in range(len(a)): r[i]=(r[i]+a[i])%p
    for i in range(len(b)): r[i]=(r[i]+b[i])%p
    while len(r)>1 and r[-1]==0: r.pop()
    return r
def poly_sub(a,b,p): return poly_add(a,[(-x)%p for x in b],p)
def poly_mul(a,b,p):
    if a==[0] or b==[0]: return [0]
    r=[0]*(len(a)+len(b)-1)
    for i in range(len(a)):
        for j in range(len(b)):
            r[i+j]=(r[i+j]+a[i]*b[j])%p
    while len(r)>1 and r[-1]==0: r.pop()
    return r
def poly_deg(a): return -1 if a==[0] else len(a)-1
def poly_divmod(a,b,p):
    if b==[0]: raise ZeroDivisionError
    if poly_deg(a)<poly_deg(b): return [0],list(a)
    inv_lead=pow(b[-1],p-2,p); a=list(a); q=[0]*(len(a)-len(b)+1)
    for i in range(len(a)-len(b),-1,-1):
        coeff=(a[i+len(b)-1]*inv_lead)%p; q[i]=coeff
        for j in range(len(b)): a[i+j]=(a[i+j]-coeff*b[j])%p
    while len(a)>1 and a[-1]==0: a.pop()
    while len(q)>1 and q[-1]==0: q.pop()
    return q,a
def poly_gcd(a,b,p):
    while b!=[0]:
        _,r=poly_divmod(a,b,p)
        a,b=b,r
    if a!=[0]:
        inv_lead=pow(a[-1],p-2,p)
        a=[(x*inv_lead)%p for x in a]
    return a
def poly_eval(a,t,p):
    val=0
    for c in reversed(a): val=(val*t+c)%p
    return val
def poly_derivative(a, p):
    if len(a) <= 1: return [0]
    return [(i * a[i]) % p for i in range(1, len(a))]

def compute_remainders(n_ord, a, b, p):
    """Compute r0,r1,r2 for line sigma = a + t*b, w=3."""
    s1=[a[0],b[0]]; s2=[a[1],b[1]]; s3=[a[2],b[2]]
    for s in [s1,s2,s3]:
        while len(s)>1 and s[-1]==0: s.pop()
    ak=[1]; bk=[0]; ck=[0]
    for step in range(n_ord):
        new_ak=poly_mul(s3,ck,p)
        new_bk=poly_sub(ak,poly_mul(s2,ck,p),p)
        new_ck=poly_add(bk,poly_mul(s1,ck,p),p)
        ak,bk,ck=new_ak,new_bk,new_ck
    return ak,bk,ck

# ============================================================
# EXP 1: Exhaustive analysis of solutions for small (n, p)
# ============================================================
def exp1_exhaustive_solutions(n_ord, p):
    """
    For small (n, p):
    1. Compute ALL C(n,3) sigma-image points
    2. For each pair of sigma-image points, compute the LINE through them
    3. Count how many sigma-image points lie on each line
    4. Find the max-collinear lines and analyze their structure
    """
    print(f"\n{'='*70}")
    print(f"EXP 1: Exhaustive solution analysis, n={n_ord}, p={p}")
    print(f"{'='*70}")
    
    omega = find_omega(p, n_ord)
    L = [pow(omega, i, p) for i in range(n_ord)]
    
    # Compute sigma-image: all 3-subsets of L -> (s1, s2, s3)
    sigma_points = {}  # (s1,s2,s3) -> subset
    for combo in itertools.combinations(range(n_ord), 3):
        elts = [L[i] for i in combo]
        s1 = sum(elts) % p
        s2 = (elts[0]*elts[1] + elts[0]*elts[2] + elts[1]*elts[2]) % p
        s3 = (elts[0]*elts[1]*elts[2]) % p
        sigma_points[(s1,s2,s3)] = combo
    
    N = len(sigma_points)
    print(f"  Sigma-image: {N} points (C({n_ord},3) = {n_ord*(n_ord-1)*(n_ord-2)//6})")
    
    # Check injectivity
    all_combos = list(itertools.combinations(range(n_ord), 3))
    all_sigmas = [(sum(L[i] for i in c) % p, 
                   (L[c[0]]*L[c[1]]+L[c[0]]*L[c[2]]+L[c[1]]*L[c[2]]) % p,
                   (L[c[0]]*L[c[1]]*L[c[2]]) % p) for c in all_combos]
    
    if N < len(all_combos):
        print(f"  *** COLLISION: {len(all_combos) - N} colliding pairs ***")
    else:
        print(f"  Sigma-map is injective ✓")
    
    # Find max collinear
    pts = list(sigma_points.keys())
    
    # For each direction (b1:b2:b3) in projective space, find max collinear
    max_collinear = 0
    max_line = None
    
    # Group points by lines
    line_counts = Counter()
    
    # For each pair of sigma-image points, compute their line direction
    # and intercept (canonical form)
    for i in range(len(pts)):
        for j in range(i+1, len(pts)):
            dx = (pts[j][0] - pts[i][0]) % p
            dy = (pts[j][1] - pts[i][1]) % p
            dz = (pts[j][2] - pts[i][2]) % p
            
            # Normalize direction: first nonzero coord = 1
            for d in [dx, dy, dz]:
                if d != 0:
                    inv_d = pow(d, p-2, p)
                    dx, dy, dz = (dx*inv_d)%p, (dy*inv_d)%p, (dz*inv_d)%p
                    break
            
            # Canonical point on line: project pts[i] perpendicular to direction
            # For simplicity, use (direction, base_point_modulo_direction) as key
            # Actually just count points on this line
            count = 0
            for k in range(len(pts)):
                # Check if pts[k] is on line through pts[i] with direction (dx,dy,dz)
                cx = (pts[k][0] - pts[i][0]) % p
                cy = (pts[k][1] - pts[i][1]) % p
                cz = (pts[k][2] - pts[i][2]) % p
                # Check if (cx,cy,cz) is proportional to (dx,dy,dz)
                # Cross product should be zero
                if ((cy*dz - cz*dy) % p == 0 and
                    (cz*dx - cx*dz) % p == 0 and
                    (cx*dy - cy*dx) % p == 0):
                    count += 1
            
            if count > max_collinear:
                max_collinear = count
                max_line = (pts[i], (dx,dy,dz), 
                           [k for k in range(len(pts)) 
                            if ((pts[k][0]-pts[i][0])*dy - (pts[k][1]-pts[i][1])*dx) % p == 0 and
                               ((pts[k][0]-pts[i][0])*dz - (pts[k][2]-pts[i][2])*dx) % p == 0 and
                               ((pts[k][1]-pts[i][1])*dz - (pts[k][2]-pts[i][2])*dy) % p == 0])
    
    print(f"\n  Max collinear = {max_collinear}")
    if max_line:
        base, dirn, indices = max_line
        print(f"  Line: base={base}, direction={dirn}")
        print(f"  Subsets on this line:")
        for idx in indices[:10]:
            pt = pts[idx]
            combo = sigma_points[pt]
            print(f"    {combo} -> σ = {pt}")
        if len(indices) > 10:
            print(f"    ... and {len(indices)-10} more")
        
        # Analyze the INDEX STRUCTURE of these subsets
        subsets_on_line = [sigma_points[pts[idx]] for idx in indices]
        # What elements of Z/nZ are most used?
        elem_counts = Counter()
        for s in subsets_on_line:
            for e in s:
                elem_counts[e] += 1
        print(f"\n  Element frequency in max-collinear subsets:")
        for e, c in sorted(elem_counts.items()):
            print(f"    {e}: {c}/{len(subsets_on_line)}")
        
        # Check: do all subsets share a common element?
        common = set(subsets_on_line[0])
        for s in subsets_on_line[1:]:
            common &= set(s)
        if common:
            print(f"  Common element(s): {common}")
            # If all share element e, then the line is parameterized by
            # the remaining 2-element subsets of L \ {e}
            for e in common:
                remaining = [tuple(sorted(set(s) - {e})) for s in subsets_on_line]
                print(f"  Removing common {e}: remaining pairs = {remaining[:10]}...")
        else:
            print(f"  No common element")
    
    return max_collinear

# ============================================================
# EXP 2: Determinant constraint analysis
# ============================================================
def exp2_determinant_constraint(n_ord, p, num_trials=200):
    """
    At a solution t0: s3(t0)^n = 1.
    Since s3(t) = a3 + t*b3, the candidates are t = (zeta - a3) / b3
    where zeta^n = 1.
    
    So there are exactly n candidate t-values (when b3 != 0).
    Among these, how many satisfy r0=1, r1=0, r2=0?
    
    This gives a TIGHTER view than Bezout: instead of n-2 from degree,
    we have n from the determinant constraint, and the actual count << n.
    """
    print(f"\n{'='*70}")
    print(f"EXP 2: Determinant constraint, n={n_ord}, p={p}")
    print(f"{'='*70}")
    
    omega = find_omega(p, n_ord)
    # All n-th roots of unity
    nth_roots = [pow(omega, j, p) for j in range(n_ord)]
    
    actual_counts = []
    candidate_counts = []
    
    for trial in range(num_trials):
        a = [random.randint(0,p-1) for _ in range(3)]
        b = [random.randint(0,p-1) for _ in range(3)]
        if b[2] == 0: continue  # skip b3=0 lines
        
        r0,r1,r2 = compute_remainders(n_ord, a, b, p)
        r0m1 = poly_sub(r0, [1], p)
        
        # Count actual solutions
        actual = 0
        for t in range(p):
            if poly_eval(r0m1,t,p)==0 and poly_eval(r1,t,p)==0 and poly_eval(r2,t,p)==0:
                actual += 1
        
        # Count candidates from s3(t)^n = 1
        inv_b3 = pow(b[2], p-2, p)
        candidates = 0
        candidate_solutions = 0
        for zeta in nth_roots:
            t0 = ((zeta - a[2]) * inv_b3) % p
            candidates += 1
            if poly_eval(r0m1,t0,p)==0 and poly_eval(r1,t0,p)==0 and poly_eval(r2,t0,p)==0:
                candidate_solutions += 1
        
        actual_counts.append(actual)
        candidate_counts.append(candidate_solutions)
        
        if actual != candidate_solutions and trial < 20:
            print(f"  *** Trial {trial}: actual={actual}, from det constraint={candidate_solutions}")
    
    print(f"\n  Actual M distribution: {Counter(actual_counts).most_common(10)}")
    print(f"  Det-constrained M distribution: {Counter(candidate_counts).most_common(10)}")
    print(f"  Match rate: {sum(1 for a,c in zip(actual_counts,candidate_counts) if a==c)/len(actual_counts):.3f}")
    
    # KEY: are ALL solutions among the det-constraint candidates?
    all_subset = all(a <= c for a, c in zip(actual_counts, candidate_counts))
    print(f"  All solutions ⊆ det candidates: {all_subset}")

# ============================================================
# EXP 3: Multiplicity analysis at solutions
# ============================================================
def exp3_multiplicity(n_ord, p, num_trials=100):
    """
    At each solution t0 of gcd(r0-1, r1, r2):
    - Compute the multiplicity (order of vanishing)
    - Check if derivative conditions are automatically satisfied
    
    If multiplicity > 1, Stepanov gives better bounds.
    """
    print(f"\n{'='*70}")
    print(f"EXP 3: Multiplicity analysis, n={n_ord}, p={p}")
    print(f"{'='*70}")
    
    mult_dist = Counter()
    
    for trial in range(num_trials):
        a = [random.randint(0,p-1) for _ in range(3)]
        b = [random.randint(0,p-1) for _ in range(3)]
        if all(x==0 for x in b): continue
        
        r0,r1,r2 = compute_remainders(n_ord, a, b, p)
        r0m1 = poly_sub(r0, [1], p)
        
        g = poly_gcd(r0m1, r1, p)
        g = poly_gcd(g, r2, p)
        
        if poly_deg(g) <= 0:
            continue
        
        # Factor g to find the roots and their multiplicities
        # g = product of (t - t_i)^{m_i}
        for t0 in range(p):
            if poly_eval(g, t0, p) == 0:
                # Compute multiplicity
                mult = 0
                tmp = g
                while poly_eval(tmp, t0, p) == 0:
                    mult += 1
                    _, tmp = poly_divmod(tmp, [(-t0)%p, 1], p)
                    if tmp == [0]:
                        break
                mult_dist[mult] += 1
                
                if mult > 1 and trial < 20:
                    # Check derivatives of r_i at t0
                    dr0 = poly_derivative(r0m1, p)
                    dr1 = poly_derivative(r1, p)
                    dr2 = poly_derivative(r2, p)
                    print(f"  Trial {trial}, t0={t0}: mult={mult}, "
                          f"r0'={poly_eval(dr0,t0,p)}, r1'={poly_eval(dr1,t0,p)}, r2'={poly_eval(dr2,t0,p)}")
    
    print(f"\n  Multiplicity distribution: {dict(mult_dist)}")
    if 1 in mult_dist:
        print(f"  Fraction simple: {mult_dist[1]/sum(mult_dist.values()):.3f}")

# ============================================================
# EXP 4: The r0, r1, r2 factorization patterns
# ============================================================
def exp4_factorization(n_ord, p, num_trials=50):
    """
    Factor r0-1, r1, r2 over F_p[t] and study the shared factors.
    
    Key questions:
    - What is the typical factorization pattern?
    - Do r1 and r2 share more factors with each other than with r0-1?
    - Is there a "core" shared factor that appears in ALL three?
    """
    print(f"\n{'='*70}")
    print(f"EXP 4: Factorization patterns, n={n_ord}, p={p}")
    print(f"{'='*70}")
    
    gcd01_degs = []
    gcd02_degs = []
    gcd12_degs = []
    gcd012_degs = []
    
    for trial in range(num_trials):
        a = [random.randint(0,p-1) for _ in range(3)]
        b = [random.randint(0,p-1) for _ in range(3)]
        if all(x==0 for x in b): continue
        
        r0,r1,r2 = compute_remainders(n_ord, a, b, p)
        r0m1 = poly_sub(r0, [1], p)
        
        g01 = poly_gcd(r0m1, r1, p)
        g02 = poly_gcd(r0m1, r2, p)
        g12 = poly_gcd(r1, r2, p)
        g012 = poly_gcd(g01, r2, p)
        
        gcd01_degs.append(poly_deg(g01))
        gcd02_degs.append(poly_deg(g02))
        gcd12_degs.append(poly_deg(g12))
        gcd012_degs.append(poly_deg(g012))
        
        if trial < 5:
            print(f"  Trial {trial}: gcd(r0-1,r1)={poly_deg(g01)}, "
                  f"gcd(r0-1,r2)={poly_deg(g02)}, gcd(r1,r2)={poly_deg(g12)}, "
                  f"gcd_all={poly_deg(g012)}")
    
    print(f"\n  Pairwise GCD degrees:")
    print(f"    gcd(r0-1, r1): {Counter(gcd01_degs).most_common(5)}")
    print(f"    gcd(r0-1, r2): {Counter(gcd02_degs).most_common(5)}")
    print(f"    gcd(r1, r2):   {Counter(gcd12_degs).most_common(5)}")
    print(f"    gcd(all three): {Counter(gcd012_degs).most_common(5)}")
    
    # Key: what's the typical factor LOSS at each step?
    losses_01_to_012 = [g01 - g012 for g01, g012 in zip(gcd01_degs, gcd012_degs)]
    print(f"\n  deg gcd(r0-1,r1) - deg gcd_all: avg = {sum(losses_01_to_012)/len(losses_01_to_012):.1f}")

# ============================================================
# EXP 5: Rank-1 perturbation structure of C(t) = C_0 + t*C_1
# ============================================================
def exp5_rank1_structure(n_ord, p):
    """
    C(t) = C_0 + t * v * e_2^T where v = (b3, -b2, b1)^T.
    
    C(t)^n = sum_{k=0}^{n} t^k * M_k where M_k involves k insertions of v*e_2^T.
    
    Specifically: M_k = sum over all ways to place k copies of (v*e_2^T) among n-k copies of C_0.
    This is related to the DERIVATIVE of C(t)^n at t=0.
    
    M_0 = C_0^n
    M_1 = sum_{j=0}^{n-1} C_0^j * (v*e_2^T) * C_0^{n-1-j} = (sum C_0^j v) * (e_2^T * C_0^{n-1-j})
    Actually M_1 = sum_j C_0^j * v * (e_2^T * C_0^{n-1-j})
    
    Note: e_2^T * C_0^k extracts the (2,·) row of C_0^k — this is the LAST ROW.
    And C_0^j * v is a matrix-vector product.
    
    So M_1 = sum_j (C_0^j v) ⊗ (e_2^T C_0^{n-1-j}).
    
    This sum of rank-1 matrices has rank ≤ min(n, 3) = 3.
    
    The higher M_k have similar structure with k-fold sums.
    
    KEY: the degree of r_i (first column of C^n) in t is ≤ n-3 (= n-w).
    But we showed deg ≤ n-2 earlier. Let me verify which is correct.
    """
    print(f"\n{'='*70}")
    print(f"EXP 5: Rank-1 structure, n={n_ord}, p={p}")
    print(f"{'='*70}")
    
    # Compute C_0^j for j = 0, ..., n-1
    random.seed(42)
    a = [random.randint(0,p-1) for _ in range(3)]
    b = [random.randint(0,p-1) for _ in range(3)]
    
    # C_0 = [[0,0,a3],[1,0,-a2],[0,1,a1]]
    C0 = [[0, 0, a[2]], [1, 0, (-a[1])%p], [0, 1, a[0]]]
    v = [b[2], (-b[1])%p, b[0]]  # column perturbation
    
    # Matrix multiply mod p
    def mat_mul(A, B, p):
        n = len(A)
        return [[(sum(A[i][k]*B[k][j] for k in range(n)))%p for j in range(n)] for i in range(n)]
    
    def mat_vec(A, v, p):
        return [(sum(A[i][k]*v[k] for k in range(len(v))))%p for i in range(len(A))]
    
    def vec_row(v, u, p):
        # Outer product v ⊗ u
        return [[(v[i]*u[j])%p for j in range(len(u))] for i in range(len(v))]
    
    # Compute C_0^j for j=0..n-1
    powers = [[[1,0,0],[0,1,0],[0,0,1]]]  # C_0^0 = I
    for j in range(1, n_ord):
        powers.append(mat_mul(powers[-1], C0, p))
    
    # M_1 = sum_j C_0^j * v * (e_2^T * C_0^{n-1-j})
    # C_0^j * v is a 3-vector
    # e_2^T * C_0^{n-1-j} is a 3-vector (last row of C_0^{n-1-j})
    M1 = [[0]*3 for _ in range(3)]
    for j in range(n_ord):
        left = mat_vec(powers[j], v, p)  # C_0^j * v
        right = powers[n_ord-1-j][2]  # last row of C_0^{n-1-j}
        outer = vec_row(left, right, p)
        for i in range(3):
            for k in range(3):
                M1[i][k] = (M1[i][k] + outer[i][k]) % p
    
    print(f"  M_1 (coefficient of t in C^n):")
    for row in M1:
        print(f"    {row}")
    print(f"  rank(M_1) = ?")  # For a 3x3 matrix, just check determinant
    det_M1 = (M1[0][0]*(M1[1][1]*M1[2][2]-M1[1][2]*M1[2][1]) -
              M1[0][1]*(M1[1][0]*M1[2][2]-M1[1][2]*M1[2][0]) +
              M1[0][2]*(M1[1][0]*M1[2][1]-M1[1][1]*M1[2][0])) % p
    print(f"  det(M_1) = {det_M1}")
    
    # The first column of M_1 gives the coefficient of t in (r0, r1, r2)
    # Verify against the polynomial computation
    r0,r1,r2 = compute_remainders(n_ord, a, b, p)
    # Coefficient of t^1 in r_i
    r0_t1 = r0[1] if len(r0) > 1 else 0
    r1_t1 = r1[1] if len(r1) > 1 else 0
    r2_t1 = r2[1] if len(r2) > 1 else 0
    
    print(f"\n  Coefficient of t in r_i:")
    print(f"    From M_1 col 0: ({M1[0][0]}, {M1[1][0]}, {M1[2][0]})")
    print(f"    From poly r_i:  ({r0_t1}, {r1_t1}, {r2_t1})")
    
    # Now check the leading coefficient of r_i (coefficient of t^{n-w})
    D = n_ord - 3  # expected max degree
    print(f"\n  Expected degree: {D}")
    print(f"  Actual degrees: r0={poly_deg(r0)}, r1={poly_deg(r1)}, r2={poly_deg(r2)}")
    
    # Leading coefficients
    if poly_deg(r0) == D:
        print(f"  Leading coeff of r0: {r0[D]}")
    if poly_deg(r1) == D:
        print(f"  Leading coeff of r1: {r1[D]}")
    if poly_deg(r2) == D:
        print(f"  Leading coeff of r2: {r2[D]}")
    
    # The leading term of r_i(t) is the coefficient of t^{n-3} in the expansion of C(t)^n.
    # This comes from M_{n-3} * col_0, which involves picking (n-3) copies of the
    # rank-1 perturbation from n total factors.
    # That means M_{n-3} = sum over (n-3)-insertions of (v*e_2^T) in 3 copies of C_0.
    # There are C(n, n-3) = C(n, 3) terms, each a product involving 3 copies of C_0
    # and (n-3) copies of v*e_2^T.
    
    print(f"\n  Leading coefficient structure:")
    print(f"  Involves C({n_ord},3) = {n_ord*(n_ord-1)*(n_ord-2)//6} terms")
    print(f"  Each term is a product of 3 copies of C_0 and {n_ord-3} rank-1 terms")

# ============================================================
# EXP 6: Parallel large-scale sweep
# ============================================================
def sweep_line_worker(args):
    """Worker for parallel sweep: compute gcd degree for one line."""
    n_ord, a, b, p = args
    r0,r1,r2 = compute_remainders(n_ord, a, b, p)
    r0m1 = poly_sub(r0, [1], p)
    g = poly_gcd(r0m1, r1, p)
    g = poly_gcd(g, r2, p)
    return poly_deg(g)

def exp6_large_scale_sweep(n_ord, p, num_lines=2000):
    """Parallel sweep over random lines to find max gcd."""
    print(f"\n{'='*70}")
    print(f"EXP 6: Large-scale parallel sweep, n={n_ord}, p={p}, lines={num_lines}")
    print(f"{'='*70}")
    
    random.seed(12345)
    tasks = []
    for _ in range(num_lines):
        a = [random.randint(0,p-1) for _ in range(3)]
        b = [random.randint(0,p-1) for _ in range(3)]
        while all(x==0 for x in b):
            b = [random.randint(0,p-1) for _ in range(3)]
        tasks.append((n_ord, a, b, p))
    
    t0 = time.time()
    with mp.Pool(24) as pool:
        results = pool.map(sweep_line_worker, tasks)
    elapsed = time.time() - t0
    
    print(f"  Time: {elapsed:.1f}s ({num_lines/elapsed:.0f} lines/sec)")
    print(f"  GCD distribution: {Counter(results).most_common(10)}")
    print(f"  Max gcd = {max(results)}, Bezout bound = {n_ord-2}")

# ============================================================
# EXP 7: Stepanov auxiliary polynomial attempt
# ============================================================
def exp7_stepanov_attempt(n_ord, p):
    """
    Stepanov idea: construct P(t) that vanishes at all solutions of
    {r0=1, r1=0, r2=0} with HIGH MULTIPLICITY.
    
    Candidate 1: Use the Frobenius structure.
    For t ∈ F_p: r_i(t)^p = r_i(t) (since coefficients ∈ F_p and t^p = t).
    So r_i(t)^p - r_i(t) = 0 for all t ∈ F_p (not just solutions).
    This gives t^p - t | r_i(t)^p - r_i(t), which is trivial.
    
    Candidate 2: Cross-relations.
    Consider P(t) = r1(t) * r0'(t) - r0(t) * r1'(t) (Wronskian of r0, r1).
    At a solution t0 where r0(t0)=1, r1(t0)=0:
    P(t0) = 0 * r0'(t0) - 1 * r1'(t0) = -r1'(t0).
    
    If r1'(t0) ≠ 0 (simple zero of r1), then P(t0) ≠ 0. Not helpful.
    If r1'(t0) = 0 (double zero), then P(t0) = 0. Higher multiplicity!
    
    Candidate 3: The determinant derivative.
    d/dt [det(C^n)] = d/dt [s3^n] = n * s3^{n-1} * b3.
    
    det(C^n) = det(r0I + r1C + r2C^2) = Res(r0+r1T+r2T^2, g_t).
    
    d/dt Res = (partial derivatives w.r.t. coefficients) * (derivatives of coefficients w.r.t. t).
    
    At a solution: h(T) = 1, g_t has roots that are n-th roots of unity.
    The derivative gives a LINEAR relation on (r0', r1', r2').
    
    This is one constraint. Combined with the original 3 conditions,
    we get: at each solution, (r0', r1', r2') satisfies a linear equation.
    
    Candidate 4: MOST PROMISING — use the trace and higher Newton identities.
    
    Define: for j = 1, 2, ..., n-1:
    T_j(t) = tr(C(t)^j) = sum of j-th powers of eigenvalues.
    
    These are polynomials in t (via companion matrix).
    At a solution where ALL eigenvalues are n-th roots of unity:
    T_j = sum of three n-th roots of unity raised to power j.
    
    For j = n: T_n = 3 (all eigenvalues → 1).
    For j = 1: T_1 = s1(t).
    For j = 2: T_2 = s1^2 - 2s2.
    ...
    
    At a solution t0: T_j(t0) is a sum of three roots of unity.
    The possible values of T_j are DISCRETE (finitely many).
    
    Specifically: T_j = ω^{ja} + ω^{jb} + ω^{jc} for some a,b,c ∈ Z/nZ.
    There are at most C(n,3) possible values of the TUPLE (T_1,...,T_{n-1}).
    
    But each T_j(t) is a polynomial in t, and it must take one of finitely many values.
    So T_j(t) = v_j has at most deg(T_j) solutions for each value v_j.
    
    IDEA: use MULTIPLE T_j conditions simultaneously.
    """
    print(f"\n{'='*70}")
    print(f"EXP 7: Stepanov auxiliary polynomial, n={n_ord}, p={p}")
    print(f"{'='*70}")
    
    omega = find_omega(p, n_ord)
    L = [pow(omega, i, p) for i in range(n_ord)]
    
    # Compute Tr(C^j) as polynomial in t for various j
    # Tr(C^j) = r0_j * tr(I) + r1_j * tr(C) + r2_j * tr(C^2)
    # where (r0_j, r1_j, r2_j) are from T^j mod g_t.
    # tr(I) = 3, tr(C) = s1, tr(C^2) = s1^2 - 2s2
    
    random.seed(42)
    a = [random.randint(0,p-1) for _ in range(3)]
    b = [random.randint(0,p-1) for _ in range(3)]
    
    s1_poly = [a[0], b[0]]
    s2_poly = [a[1], b[1]]
    for s in [s1_poly, s2_poly]:
        while len(s)>1 and s[-1]==0: s.pop()
    
    # tr(C^2) = s1^2 - 2*s2
    trC2 = poly_sub(poly_mul(s1_poly, s1_poly, p), poly_mul([2], s2_poly, p), p)
    
    # Compute traces for j = 1, ..., n
    print("  Computing Tr(C^j) as polynomials in t...")
    traces = {}
    
    # For j < 3, use direct formulas:
    # j=1: Tr(C) = s1 (degree 1)
    # j=2: Tr(C^2) = s1^2 - 2s2 (degree 2)
    # For j >= 3: use recurrence Tr(C^j) = s1*Tr(C^{j-1}) - s2*Tr(C^{j-2}) + s3*Tr(C^{j-3})
    
    s3_poly = [a[2], b[2]]
    while len(s3_poly)>1 and s3_poly[-1]==0: s3_poly.pop()
    
    traces[0] = [3]  # Tr(I) = 3
    traces[1] = list(s1_poly)
    traces[2] = list(trC2)
    
    for j in range(3, n_ord+1):
        t_j = poly_add(
            poly_sub(
                poly_mul(s1_poly, traces[j-1], p),
                poly_mul(s2_poly, traces[j-2], p),
                p
            ),
            poly_mul(s3_poly, traces[j-3], p),
            p
        )
        traces[j] = t_j
    
    print(f"  deg Tr(C^j) for j=1..{n_ord}:")
    for j in range(1, min(n_ord+1, 15)):
        print(f"    j={j}: deg = {poly_deg(traces[j])}")
    
    # At a solution: Tr(C^n) = 3.
    # Check: compute Tr(C^n) and verify it's related to r0,r1,r2.
    # Tr(C^n) = 3*r0 + r1*s1 + r2*(s1^2 - 2s2)
    r0,r1,r2 = compute_remainders(n_ord, a, b, p)
    tr_n_via_ri = poly_add(poly_add(
        poly_mul([3], r0, p),
        poly_mul(r1, s1_poly, p), p),
        poly_mul(r2, trC2, p), p)
    
    match = traces[n_ord] == tr_n_via_ri
    print(f"\n  Tr(C^n) via recurrence == via r0,r1,r2: {match}")
    
    # KEY TEST: at solution points, what values do Tr(C^j) take?
    # Find solutions first
    r0m1 = poly_sub(r0, [1], p)
    solutions = []
    for t in range(p):
        if poly_eval(r0m1,t,p)==0 and poly_eval(r1,t,p)==0 and poly_eval(r2,t,p)==0:
            solutions.append(t)
    
    if not solutions:
        print(f"  No solutions found for this line.")
        return
    
    print(f"\n  Solutions: {solutions}")
    print(f"  Trace values at solutions:")
    for t0 in solutions[:5]:
        vals = [poly_eval(traces[j], t0, p) for j in range(1, min(n_ord+1, 8))]
        print(f"    t={t0}: Tr(C^j) for j=1..{min(n_ord,7)} = {vals}")
    
    # Check: how many DISTINCT trace-value tuples exist?
    # Each tuple (Tr(C^1),...,Tr(C^{n-1})) at a solution corresponds to
    # a 3-subset {a,b,c} of Z/nZ.
    all_trace_tuples = set()
    for combo in itertools.combinations(range(n_ord), 3):
        tup = tuple((L[combo[0]]**j + L[combo[1]]**j + L[combo[2]]**j) % p for j in range(1, n_ord))
        all_trace_tuples.add(tup)
    print(f"\n  Number of possible trace tuples: {len(all_trace_tuples)} (C({n_ord},3)={n_ord*(n_ord-1)*(n_ord-2)//6})")
    
    # Stepanov construction: Tr(C^j)(t) = v_j is a polynomial equation in t.
    # For each j, deg(Tr(C^j)) = j (bounded by companion structure).
    # The values v_j have at most n^2 options (crude bound from all 3-subsets).
    
    # So each condition Tr(C^j) = v_j has at most j solutions in t.
    # Using j=1: at most 1 solution. But there are n distinct values of v_1!
    
    # Wait, for j=1: Tr(C^1) = s1(t) = a1 + t*b1 (degree 1).
    # So Tr(C^1) = v_1 has EXACTLY 1 solution for each v_1.
    # The number of possible v_1 values is at most n (since v_1 = omega^a + omega^b + omega^c).
    
    # So from Tr(C^1) alone, there are at most n candidate t-values.
    # Combined with s3^n = 1 (also n candidates), the intersection could be small.
    
    # STRONGER: use Tr(C^1) AND Tr(C^2) jointly.
    # Tr(C^1)(t) = v_1 gives 1 value of t.
    # Tr(C^2)(t) = v_2 gives ≤ 2 values of t.
    # For consistency: v_1 and v_2 must come from the SAME 3-subset.
    # Number of (v_1, v_2) pairs: C(n,3).
    # But for each pair, the system Tr(C^1)=v_1, Tr(C^2)=v_2 has at most 1 solution
    # (since Tr(C^1)=v_1 gives exactly 1 t, and then check Tr(C^2)=v_2).
    
    # So M ≤ C(n,3), from using two trace conditions. Still too large.
    
    # The REAL strength: after fixing v_1 (determines t uniquely since deg=1),
    # we need Tr(C^j)(t) to equal the correct value for ALL j.
    # But since t is already determined, this is AUTOMATIC (tautological).
    
    # OK so the trace approach doesn't add information beyond what we already have.
    
    # Let me try something different: RESULTANT between pairs of r_i polynomials.
    print(f"\n--- Resultant structure ---")
    
    # gcd(r0-1, r1) degree
    g01 = poly_gcd(r0m1, r1, p)
    g02 = poly_gcd(r0m1, r2, p)
    g12 = poly_gcd(r1, r2, p)
    
    print(f"  deg gcd(r0-1, r1) = {poly_deg(g01)}")
    print(f"  deg gcd(r0-1, r2) = {poly_deg(g02)}")
    print(f"  deg gcd(r1, r2) = {poly_deg(g12)}")
    
    # r0-1 = gcd(r0-1,r1) * Q01
    # r1 = gcd(r0-1,r1) * Q01'
    # gcd_all = gcd(gcd(r0-1,r1), r2)
    # So gcd_all | gcd(r0-1,r1) and gcd_all | r2.
    
    # The KEY: why is gcd(gcd(r0-1,r1), r2) much smaller than gcd(r0-1,r1)?
    # Answer: r2 is "independent" of the common factor of r0-1 and r1.
    
    # From companion matrix: r0, r1, r2 are the coordinates of C^n * e_0 in the
    # {I, C, C^2} basis. They share the companion matrix origin.
    # But in the {e_0, e_1, e_2} basis, they are different PROJECTIONS
    # of the same matrix-vector product.
    
    # The common factors of r0-1 and r1 correspond to the LINE in (r0,r1,r2)-space
    # passing through (1,0,*) — these are the t where r0=1 AND r1=0 but r2 is free.
    # The condition r2=0 then picks out discrete points on this line.
    
    # QUANTITATIVE: deg gcd(r0-1, r1) = D01 = number of t where (r0,r1) = (1,0).
    # From Bezout: D01 ≤ (n-2)^2 / (n-2) = n-2 (since both have degree n-2).
    # Actually D01 = deg gcd ≤ min(deg(r0-1), deg(r1)) = n-2.
    
    # Then gcd_all = number of t where r2(t) = 0 AMONG these D01 values.
    # If r2 behaves "generically" on these D01 points, expected count = D01/p.
    
    print(f"\n  Expected gcd_all from density: deg(gcd01)/p = {poly_deg(g01)}/{p} = {poly_deg(g01)/p:.3f}")
    print(f"  Actual gcd_all = {poly_deg(poly_gcd(g01, r2, p))}")

def main():
    print("="*70)
    print("STEPANOV METHOD EXPLORATION")
    print("="*70)
    
    # Small case first
    exp1_exhaustive_solutions(8, 17)
    exp2_determinant_constraint(10, 11, 200)
    exp2_determinant_constraint(10, 31, 200)
    exp3_multiplicity(10, 11, 200)
    exp4_factorization(10, 11, 100)
    exp4_factorization(10, 31, 100)
    exp5_rank1_structure(10, 11)
    exp7_stepanov_attempt(10, 11)
    
    # Large-scale parallel sweeps
    for n_ord, p in [(20, 61), (30, 61), (24, 97), (36, 109), (48, 97), (60, 61)]:
        if (p-1) % n_ord != 0:
            continue
        exp6_large_scale_sweep(n_ord, p, 5000)
    
    print("\n\nDONE.")

if __name__ == '__main__':
    main()
