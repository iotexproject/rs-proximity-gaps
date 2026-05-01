#!/usr/bin/env python3
"""
Deep analysis of companion matrix algebraic structure.

The companion matrix C(t) for g_t(T) = T^3 - s1(t)T^2 + s2(t)T - s3(t) is:
  C(t) = [[0, 0, s3(t)],
          [1, 0, -s2(t)],
          [0, 1, s1(t)]]

where s_j(t) = a_j + t*b_j (affine in t).

C(t)^n = [[r0(t)], [r1(t)], [r2(t)]] (first column, after reducing by T^n - 1 = 0).

Actually: T^n mod g_t = r2*T^2 + r1*T + r0, and the FULL matrix C^n has 9 entries,
each a polynomial in t.

KEY INSIGHT: C^n satisfies the characteristic polynomial of C:
  C^3 - s1*C^2 + s2*C - s3*I = 0
  => C^n = (C^n mod char_poly) expressed via C^2, C, I

But char_poly has COEFFICIENTS depending on t, so this is more subtle.

THIS SCRIPT EXPLORES:
1. The full 3x3 matrix C^n(t) — all 9 entries as polynomials in t
2. Relations between the 9 entries (are there polynomial identities?)
3. The RESULTANT of pairs (r0-1, r1), (r0-1, r2), (r1, r2) — degree of resultant
   tells us the max possible common zeros
4. Syzygy module: find polynomial P(r0,r1,r2) = 0 identically
5. How gcd degree depends on the LINE DIRECTION b = (b1,b2,b3)
"""

import itertools
import random
from collections import Counter

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
def poly_add(a, b, p):
    n = max(len(a), len(b))
    r = [0]*n
    for i in range(len(a)): r[i] = (r[i]+a[i])%p
    for i in range(len(b)): r[i] = (r[i]+b[i])%p
    while len(r)>1 and r[-1]==0: r.pop()
    return r
def poly_sub(a,b,p):
    return poly_add(a,[(-x)%p for x in b],p)
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
    inv_lead=pow(b[-1],p-2,p)
    a=list(a); q=[0]*(len(a)-len(b)+1)
    for i in range(len(a)-len(b),-1,-1):
        coeff=(a[i+len(b)-1]*inv_lead)%p
        q[i]=coeff
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

def compute_full_Cn(n_order, a, b, p):
    """
    Compute all 9 entries of C(t)^n as polynomials in t.
    C(t) = [[0,0,s3], [1,0,-s2], [0,1,s1]]
    
    Returns 3x3 matrix of polynomials.
    """
    s1 = [a[0], b[0]]  # σ1(t) = a1 + t*b1
    s2 = [a[1], b[1]]
    s3 = [a[2], b[2]]
    # trim
    for s in [s1,s2,s3]:
        while len(s)>1 and s[-1]==0: s.pop()
    
    # M = C^0 = I (as polys in t)
    M = [[[1],[0],[0]], [[0],[1],[0]], [[0],[0],[1]]]
    
    # C as a function: C[i][j] is a polynomial in t
    # C = [[0,0,s3],[1,0,-s2],[0,1,s1]]
    neg_s2 = [(-x)%p for x in s2]
    C = [[[0], [0], list(s3)],
         [[1], [0], neg_s2],
         [[0], [1], list(s1)]]
    
    for step in range(n_order):
        # New = M * C  (matrix multiply, poly multiply for entries)
        new_M = [[[0] for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                s = [0]
                for k in range(3):
                    s = poly_add(s, poly_mul(M[i][k], C[k][j], p), p)
                new_M[i][j] = s
        M = new_M
    
    return M

def compute_remainders(n_order, w, a, b, p):
    """For w=3: compute r0,r1,r2 via companion matrix recurrence."""
    s1=[a[0],b[0]]; s2=[a[1],b[1]]; s3=[a[2],b[2]]
    for s in [s1,s2,s3]:
        while len(s)>1 and s[-1]==0: s.pop()
    ak=[1]; bk=[0]; ck=[0]
    for step in range(n_order):
        new_ak=poly_mul(s3,ck,p)
        new_bk=poly_sub(ak,poly_mul(s2,ck,p),p)
        new_ck=poly_add(bk,poly_mul(s1,ck,p),p)
        ak,bk,ck=new_ak,new_bk,new_ck
    return ak,bk,ck  # r0,r1,r2

def poly_resultant(f, g, p):
    """Compute resultant of f,g in F_p[t] via subresultant / Sylvester determinant."""
    m, n_d = poly_deg(f), poly_deg(g)
    if m < 0 or n_d < 0:
        return 0
    # Build Sylvester matrix (m+n) x (m+n)
    sz = m + n_d
    if sz == 0:
        return 1
    mat = [[0]*sz for _ in range(sz)]
    # First n rows: coefficients of f shifted
    for i in range(n_d):
        for j in range(m+1):
            mat[i][i+j] = f[j] % p
    # Next m rows: coefficients of g shifted
    for i in range(m):
        for j in range(n_d+1):
            mat[n_d+i][i+j] = g[j] % p
    # Determinant mod p
    det = 1
    for col in range(sz):
        pivot = -1
        for row in range(col, sz):
            if mat[row][col] % p != 0:
                pivot = row
                break
        if pivot == -1:
            return 0
        if pivot != col:
            mat[col], mat[pivot] = mat[pivot], mat[col]
            det = (-det) % p
        inv_piv = pow(mat[col][col], p-2, p)
        det = (det * mat[col][col]) % p
        mat[col] = [(x * inv_piv) % p for x in mat[col]]
        for row in range(col+1, sz):
            factor = mat[row][col]
            if factor != 0:
                for j in range(sz):
                    mat[row][j] = (mat[row][j] - factor * mat[col][j]) % p
    return det % p

# ========== EXPERIMENT 1: Full C^n matrix structure ==========
def exp1_full_matrix(n_order, p):
    print(f"\n{'='*70}")
    print(f"EXP 1: Full C^n matrix, n={n_order}, p={p}")
    print(f"{'='*70}")
    
    # Random line
    random.seed(42)
    a = [random.randint(0,p-1) for _ in range(3)]
    b = [random.randint(0,p-1) for _ in range(3)]
    
    M = compute_full_Cn(n_order, a, b, p)
    
    print("Degrees of C^n entries:")
    for i in range(3):
        degs = [poly_deg(M[i][j]) for j in range(3)]
        print(f"  Row {i}: {degs}")
    
    # The first column gives (r0, r1, r2)
    r0, r1, r2 = M[0][0], M[1][0], M[2][0]
    
    # Check: det(C^n) = det(C)^n = s3^n
    # det(C) = s3 for the companion matrix
    # So det(C^n) should equal s3^n as a polynomial in t
    s3_poly = [a[2], b[2]]
    while len(s3_poly)>1 and s3_poly[-1]==0: s3_poly.pop()
    
    s3_n = [1]
    tmp = list(s3_poly)
    for _ in range(n_order):
        s3_n = poly_mul(s3_n, tmp, p)
    
    # Compute det(M) using the 3x3 formula
    def det3(M, p):
        # det = a(ei-fh) - b(di-fg) + c(dh-eg)
        a,b,c = M[0][0], M[0][1], M[0][2]
        d,e,f = M[1][0], M[1][1], M[1][2]
        g,h,i = M[2][0], M[2][1], M[2][2]
        t1 = poly_mul(a, poly_sub(poly_mul(e,i,p), poly_mul(f,h,p), p), p)
        t2 = poly_mul(b, poly_sub(poly_mul(d,i,p), poly_mul(f,g,p), p), p)
        t3 = poly_mul(c, poly_sub(poly_mul(d,h,p), poly_mul(e,g,p), p), p)
        return poly_sub(poly_add(t1, t3, p), t2, p)
    
    det_Cn = det3(M, p)
    print(f"\ndeg(det(C^n)) = {poly_deg(det_Cn)}, deg(s3^n) = {poly_deg(s3_n)}")
    # Check equality
    if det_Cn == s3_n:
        print("det(C^n) == s3^n: VERIFIED ✓")
    else:
        # Might differ by sign or scaling
        ratio_match = True
        for t_val in range(min(p, 20)):
            d1 = poly_eval(det_Cn, t_val, p)
            d2 = poly_eval(s3_n, t_val, p)
            if d1 != d2:
                ratio_match = False
                print(f"  t={t_val}: det={d1}, s3^n={d2}")
                break
        if ratio_match:
            print("det(C^n) == s3^n: VERIFIED (pointwise) ✓")
    
    # Trace: tr(C^n) = r0 + M[1][1] + M[2][2]
    tr_Cn = poly_add(poly_add(M[0][0], M[1][1], p), M[2][2], p)
    print(f"deg(tr(C^n)) = {poly_deg(tr_Cn)}")
    
    # KEY: Cayley-Hamilton for C(t) says C^3 = s1*C^2 - s2*C + s3*I
    # But s1,s2,s3 depend on t. So C^n is NOT simply a function of s1,s2,s3
    # evaluated at generic values — the t-dependence creates structure.
    
    # The IMPORTANT algebraic identity:
    # C^n ≡ I (mod char poly of T^n-1 factorization)
    # i.e., the condition g_t | T^n - 1 means C^n = I.
    # So r0=1, r1=0, r2=0 AND the off-diagonal entries have conditions too.
    
    # Look at ALL 9 conditions for C^n = I:
    print("\nConditions for C^n = I (degrees of the 9 polynomials):")
    identity = [[[1],[0],[0]], [[0],[1],[0]], [[0],[0],[1]]]
    for i in range(3):
        for j in range(3):
            diff = poly_sub(M[i][j], identity[i][j], p)
            print(f"  C^n[{i}][{j}] - I[{i}][{j}]: deg = {poly_deg(diff)}")
    
    return M

# ========== EXPERIMENT 2: Resultant analysis ==========
def exp2_resultants(n_order, p, num_trials=50):
    print(f"\n{'='*70}")
    print(f"EXP 2: Resultant analysis, n={n_order}, p={p}")
    print(f"{'='*70}")
    
    gcd_degs = []
    res_vals = {'01': [], '02': [], '12': []}
    
    for trial in range(num_trials):
        a = [random.randint(0,p-1) for _ in range(3)]
        b = [random.randint(0,p-1) for _ in range(3)]
        if all(x==0 for x in b): continue
        
        r0,r1,r2 = compute_remainders(n_order, 3, a, b, p)
        r0m1 = poly_sub(r0, [1], p)
        
        g = poly_gcd(r0m1, r1, p)
        g = poly_gcd(g, r2, p)
        d = poly_deg(g)
        gcd_degs.append(d)
        
        # Resultants
        res01 = poly_resultant(r0m1, r1, p)
        res02 = poly_resultant(r0m1, r2, p)
        res12 = poly_resultant(r1, r2, p)
        
        res_vals['01'].append(1 if res01 == 0 else 0)
        res_vals['02'].append(1 if res02 == 0 else 0)
        res_vals['12'].append(1 if res12 == 0 else 0)
        
        if trial < 5:
            print(f"  Trial {trial}: gcd_deg={d}, res(r0-1,r1)={'0' if res01==0 else '≠0'}, "
                  f"res(r0-1,r2)={'0' if res02==0 else '≠0'}, res(r1,r2)={'0' if res12==0 else '≠0'}")
    
    print(f"\nGCD degree distribution: {Counter(gcd_degs).most_common(10)}")
    print(f"Fraction with resultant=0: res(r0-1,r1)={sum(res_vals['01'])/len(res_vals['01']):.3f}, "
          f"res(r0-1,r2)={sum(res_vals['02'])/len(res_vals['02']):.3f}, "
          f"res(r1,r2)={sum(res_vals['12'])/len(res_vals['12']):.3f}")

# ========== EXPERIMENT 3: ALL 9 entries of C^n = I give conditions ==========
def exp3_all_nine_conditions(n_order, p, num_trials=200):
    """
    Instead of using just 3 conditions (first column), use ALL 9 conditions from C^n = I.
    The 9 conditions are:
      C^n[i][j] = delta_{ij}  for i,j in {0,1,2}
    
    From the first column: r0=1, r1=0, r2=0 (3 conditions, 1 variable t)
    From other columns: 6 MORE conditions.
    
    The gcd of ALL 9 should be SMALLER than gcd of just 3.
    """
    print(f"\n{'='*70}")
    print(f"EXP 3: All 9 conditions from C^n = I, n={n_order}, p={p}")
    print(f"{'='*70}")
    
    gcd3_degs = []
    gcd9_degs = []
    
    for trial in range(num_trials):
        a = [random.randint(0,p-1) for _ in range(3)]
        b = [random.randint(0,p-1) for _ in range(3)]
        if all(x==0 for x in b): continue
        
        M = compute_full_Cn(n_order, a, b, p)
        
        # 3-condition gcd (first column)
        r0m1 = poly_sub(M[0][0], [1], p)
        g3 = poly_gcd(r0m1, M[1][0], p)
        g3 = poly_gcd(g3, M[2][0], p)
        
        # 9-condition gcd (all entries of C^n - I)
        identity = [[[1],[0],[0]], [[0],[1],[0]], [[0],[0],[1]]]
        g9 = None
        for i in range(3):
            for j in range(3):
                diff = poly_sub(M[i][j], identity[i][j], p)
                if g9 is None:
                    g9 = diff
                else:
                    g9 = poly_gcd(g9, diff, p)
        
        d3 = poly_deg(g3)
        d9 = poly_deg(g9)
        gcd3_degs.append(d3)
        gcd9_degs.append(d9)
        
        if d3 != d9 and trial < 20:
            print(f"  Trial {trial}: gcd3={d3}, gcd9={d9} {'*** DIFFERENT ***' if d3!=d9 else ''}")
    
    print(f"\n3-condition GCD: {Counter(gcd3_degs).most_common(10)}")
    print(f"9-condition GCD: {Counter(gcd9_degs).most_common(10)}")
    print(f"Cases where 9-cond < 3-cond: {sum(1 for a,b in zip(gcd3_degs,gcd9_degs) if b<a)}/{len(gcd3_degs)}")

# ========== EXPERIMENT 4: Syzygy — find algebraic relations ==========
def exp4_syzygy(n_order, p):
    """
    The three polys r0(t), r1(t), r2(t) (degree n-2 each) come from C^n.
    
    Cayley-Hamilton: C^3 = s1*C^2 - s2*C + s3*I, so:
    C^n can be written as alpha_2(t)*C^2 + alpha_1(t)*C + alpha_0(t)*I
    where alpha_i are polynomials in t.
    
    This means:
    r0 = alpha_0 + ... (contributions from C^2, C columns)
    r1 = alpha_1 + ...
    r2 = alpha_2 + ...
    (not exactly, need to work out the matrix entries)
    
    But the KEY is: C satisfies its char poly, so C^n is determined by
    (alpha_0, alpha_1, alpha_2), which are 3 unknowns. And we have 9 equations
    (entries of C^n). So there are 6 ALGEBRAIC DEPENDENCIES among the 9 entries.
    
    For the first column alone: (r0, r1, r2) are 3 functions of 3 unknowns
    (alpha_0, alpha_1, alpha_2). So generically, there's NO syzygy among (r0,r1,r2)
    per se — they're a coordinate transformation of (alpha_0,alpha_1,alpha_2).
    
    But wait — C^0, C^1, C^2 have SPECIFIC structure (companion matrix).
    The first columns of I, C, C^2 are:
    I col 0: (1, 0, 0)
    C col 0: (0, 1, 0)
    C^2 col 0: (0, 0, 1)  ... wait, is that right?
    
    C = [[0,0,s3],[1,0,-s2],[0,1,s1]]
    C col 0 = (0, 1, 0)
    C^2 col 0 = C * (0,1,0) = (0*0+0*1+s3*0, 1*0+0*1-s2*0, 0*0+1*1+s1*0) = (0, 0, 1)
    
    So C^n col 0 = alpha_0*(1,0,0) + alpha_1*(0,1,0) + alpha_2*(0,0,1)
    = (alpha_0, alpha_1, alpha_2)
    
    THEREFORE: r0 = alpha_0, r1 = alpha_1, r2 = alpha_2.
    
    The first column IS the Cayley-Hamilton coordinates!
    
    So there's no syzygy among r0,r1,r2 from Cayley-Hamilton alone.
    
    But the OTHER columns give additional constraints:
    C^n col 1 = alpha_0*(0,0,0) + alpha_1*C_col1 + alpha_2*(C^2)_col1
    
    C col 1 = (0, 0, 1)
    C^2 col 1 = C * (0,0,1) = (s3, -s2, s1)
    
    So C^n col 1 = alpha_1*(0,0,1) + alpha_2*(s3,-s2,s1)
    = (alpha_2*s3, -alpha_2*s2, alpha_1 + alpha_2*s1)
    = (r2*s3, -r2*s2, r1 + r2*s1)
    
    For C^n = I, col 1 must be (0,1,0):
    r2*s3 = 0
    -r2*s2 = 1
    r1 + r2*s1 = 0
    
    Similarly col 2 = alpha_0*(0,0,0) + alpha_1*(0,0,0) + alpha_2*(C^2)_col2
    Wait... I_col2 = (0,0,1), C_col2 = (s3,-s2,s1), C^2_col2 = ?
    
    Actually C^2 col 2 = C * C_col2 = C * (s3, -s2, s1)
    = (s3*s1, s3 - (-s2)*s1, -s2 + s1*s1) ... wait, need to be more careful.
    
    This is getting complex. Let me just verify computationally.
    """
    print(f"\n{'='*70}")
    print(f"EXP 4: Syzygy analysis (Cayley-Hamilton), n={n_order}, p={p}")
    print(f"{'='*70}")
    
    random.seed(123)
    a = [random.randint(0,p-1) for _ in range(3)]
    b = [random.randint(0,p-1) for _ in range(3)]
    
    M = compute_full_Cn(n_order, a, b, p)
    
    r0, r1, r2 = M[0][0], M[1][0], M[2][0]
    s1 = [a[0], b[0]]; s2 = [a[1], b[1]]; s3 = [a[2], b[2]]
    for s in [s1,s2,s3]:
        while len(s)>1 and s[-1]==0: s.pop()
    
    # Verify: C^n col 1 = (r2*s3, -r2*s2, r1 + r2*s1)
    col1_0 = poly_mul(r2, s3, p)
    col1_1 = poly_mul([(-1)%p], poly_mul(r2, s2, p), p)
    col1_2 = poly_add(r1, poly_mul(r2, s1, p), p)
    
    print("Verifying C^n column 1 = (r2*s3, -r2*s2, r1+r2*s1):")
    for i, (computed, actual) in enumerate([(col1_0, M[0][1]), (col1_1, M[1][1]), (col1_2, M[2][1])]):
        match = computed == actual
        print(f"  Entry [{i}][1]: {'MATCH ✓' if match else 'MISMATCH ✗'}")
    
    # Column 2: C^n col 2 should be expressible via r0,r1,r2 and s1,s2,s3
    # C^2 col 2 = C * (s3, -s2, s1)
    # = (0*s3 + 0*(-s2) + s3*s1, 1*s3 + 0*(-s2) + (-s2)*s1, 0*s3 + 1*(-s2) + s1*s1)
    # = (s3*s1, s3 - s2*s1, s1^2 - s2)
    # Hmm wait, let me recompute.
    # C = [[0,0,s3],[1,0,-s2],[0,1,s1]]
    # C * (s3, -s2, s1)^T = (0*s3 + 0*(-s2) + s3*s1, 1*s3 + 0*(-s2) + (-s2)*s1, 0*s3 + 1*(-s2) + s1*s1)
    # = (s1*s3, s3 - s1*s2, s1^2 - s2)
    
    # So C^n col 2 = r0*(0,0,1) + r1*(s3,-s2,s1) + r2*(s1*s3, s3-s1*s2, s1^2-s2)
    # Wait: I_col2 = (0,0,1), C_col2 = (s3,-s2,s1), C^2_col2 = (s1*s3, s3-s1*s2, s1^2-s2)
    
    s1s3 = poly_mul(s1, s3, p)
    s1s2 = poly_mul(s1, s2, p)
    s1sq = poly_mul(s1, s1, p)
    
    col2_0_expected = poly_add(poly_mul(r1, s3, p), poly_mul(r2, s1s3, p), p)
    col2_1_expected = poly_add(
        poly_mul(r1, [(-1)%p], p),
        poly_add(
            poly_mul(poly_mul(r1, [(-1)%p], p), [0], p),  # wrong
            [0], p
        ), p
    )
    # Let me just do it entry by entry properly
    # col2[0] = r0*0 + r1*s3 + r2*(s1*s3) = s3*(r1 + r2*s1)
    col2_0_exp = poly_mul(s3, poly_add(r1, poly_mul(r2, s1, p), p), p)
    # col2[1] = r0*0 + r1*(-s2) + r2*(s3 - s1*s2) = -s2*(r1 + r2*s1) + r2*s3
    col2_1_exp = poly_add(
        poly_mul([(-1)%p], poly_mul(s2, poly_add(r1, poly_mul(r2, s1, p), p), p), p),
        poly_mul(r2, s3, p),
        p
    )
    # col2[2] = r0*1 + r1*s1 + r2*(s1^2 - s2) = r0 + s1*(r1 + r2*s1) - r2*s2
    col2_2_exp = poly_add(
        poly_add(r0, poly_mul(s1, poly_add(r1, poly_mul(r2, s1, p), p), p), p),
        poly_mul([(-1)%p], poly_mul(r2, s2, p), p),
        p
    )
    
    print("\nVerifying C^n column 2 formula:")
    for i, (computed, actual) in enumerate([(col2_0_exp, M[0][2]), (col2_1_exp, M[1][2]), (col2_2_exp, M[2][2])]):
        match = computed == actual
        print(f"  Entry [{i}][2]: {'MATCH ✓' if match else 'MISMATCH ✗'}")
    
    # Now the KEY insight:
    # When C^n = I, we need ALL columns to match.
    # Column 0: r0=1, r1=0, r2=0
    # Column 1: r2*s3=0, -r2*s2=1, r1+r2*s1=0
    # Column 2: s3*(r1+r2*s1)=0, -s2*(r1+r2*s1)+r2*s3=0, r0+s1*(r1+r2*s1)-r2*s2=1
    
    # From col 0: r1=0, r2=0 => col 1 gives: 0=0, 0=1 ???
    # Wait, col1[1] = -r2*s2. If r2=0, then col1[1] = 0, but we need it = 1.
    # That means col 0 conditions (r2=0) and col 1 conditions (-r2*s2=1) are INCONSISTENT
    # unless they only hold at specific t values!
    
    # Ah, I see: the conditions are for specific VALUES of t, not identically in t.
    # At a value t0 where g_{t0} | T^n - 1, ALL 9 entries of C(t0)^n equal delta_{ij}.
    # So the 9 conditions ARE all satisfied simultaneously at the same t values.
    
    # But as POLYNOMIALS in t, gcd of 3 conditions may differ from gcd of 9 conditions.
    # The 9-condition gcd should be tighter.
    
    # From columns 1 and 2, we get ADDITIONAL polynomial conditions on t.
    # These can lower the gcd degree.
    
    print("\n--- Checking: do 9 conditions give smaller gcd than 3? ---")
    # Already done in exp3. Let's check a specific example here.
    r0m1 = poly_sub(r0, [1], p)
    g3 = poly_gcd(r0m1, r1, p)
    g3 = poly_gcd(g3, r2, p)
    
    # Column 1 conditions
    c1_0 = poly_mul(r2, s3, p)  # should be 0
    c1_1 = poly_sub(poly_mul([(-1)%p], poly_mul(r2, s2, p), p), [1], p)  # should be 0 (i.e., -r2*s2 - 1 = 0)
    c1_2 = poly_add(r1, poly_mul(r2, s1, p), p)  # should be 0
    
    g9 = g3
    for cond in [c1_0, c1_1, c1_2]:
        g9 = poly_gcd(g9, cond, p)
    # Add col 2 conditions too
    c2_0 = col2_0_exp  # should be 0
    c2_1 = poly_sub(col2_1_exp, [0], p)  # should be 0... wait
    # col2[1] should equal 0 (I[1][2] = 0)
    c2_2 = poly_sub(col2_2_exp, [1], p)  # should be 0 (I[2][2] = 1)
    for cond in [c2_0, c2_1, c2_2]:
        g9 = poly_gcd(g9, cond, p)
    
    print(f"  gcd(3 conditions) = {poly_deg(g3)}")
    print(f"  gcd(9 conditions) = {poly_deg(g9)}")
    
    # KEY OBSERVATION: column 1, entry [1][1] gives -r2*s2 = 1, i.e., r2*s2 = -1.
    # But r2 is degree n-2 and s2 is degree 1. Their product r2*s2 is degree n-1.
    # For this to equal -1 (constant), we'd need r2*s2 + 1 = 0 identically, which
    # is impossible for deg > 0. So the only solutions are ISOLATED t values.
    # This means gcd with (r2*s2 + 1) should give O(1) degree!
    
    print("\n--- KEY: condition r2*s2 + 1 = 0 ---")
    r2s2_plus1 = poly_add(poly_mul(r2, s2, p), [1], p)
    print(f"  deg(r2*s2 + 1) = {poly_deg(r2s2_plus1)}")
    g_key = poly_gcd(g3, r2s2_plus1, p)
    print(f"  gcd(3-cond, r2*s2+1) = deg {poly_deg(g_key)}")

# ========== EXPERIMENT 5: Scaling of gcd with n ==========
def exp5_scaling(p):
    """How does max gcd degree scale with n for fixed p?"""
    print(f"\n{'='*70}")
    print(f"EXP 5: Scaling of gcd with n, p={p}")
    print(f"{'='*70}")
    
    for n_order in [6, 8, 10, 12, 14, 16, 18, 20, 24, 30]:
        if (p-1) % n_order != 0:
            continue
        
        max_gcd = 0
        trials = min(500, p*2)
        for trial in range(trials):
            a = [random.randint(0,p-1) for _ in range(3)]
            b = [random.randint(0,p-1) for _ in range(3)]
            if all(x==0 for x in b): continue
            
            r0,r1,r2 = compute_remainders(n_order, 3, a, b, p)
            r0m1 = poly_sub(r0, [1], p)
            g = poly_gcd(r0m1, r1, p)
            g = poly_gcd(g, r2, p)
            d = poly_deg(g)
            if d > max_gcd:
                max_gcd = d
        
        print(f"  n={n_order:3d}: max gcd deg = {max_gcd:3d} (Bezout bound = {n_order-2}), ratio = {max_gcd/(n_order-2) if n_order>2 else 0:.3f}")

# ========== EXPERIMENT 6: The r_i algebraic dependency via companion recurrence ==========
def exp6_companion_deps(n_order, p):
    """
    r_0, r_1, r_2 satisfy:
      r_0 = coefficient of T^0 in T^n mod g_t
      r_1 = coefficient of T^1
      r_2 = coefficient of T^2
    
    And T^{n+1} mod g_t = T * (r2 T^2 + r1 T + r0) mod g_t
                        = r2*(s1 T^2 - s2 T + s3) + r1 T^2 + r0 T
                        = (r2*s1 + r1) T^2 + (r0 - r2*s2) T + r2*s3
    
    But T^{n+1} mod g_t also equals T * (T^n mod g_t) re-reduced.
    Since n is the order of omega, T^n = 1 on L, so T^{n+1} = T on L.
    But as polynomials, T^{n+1} mod g_t = T only when g_t | T^n - 1.
    
    For GENERAL t: T^{n+j} mod g_t = C^j * (r0, r1, r2) gives a recurrence
    for the k-step remainders.
    
    The point: r_0, r_1, r_2 live on the IMAGE of the map
      t -> C(t)^n * e_0
    where e_0 = (1,0,0). This image is a CURVE in F_p^3 (parameterized by t).
    
    The intersection of this curve with the point (1,0,0) gives the solutions.
    
    For the curve to pass through (1,0,0) many times, it would need to be
    highly non-generic. Let's check the DEGREE of this curve.
    """
    print(f"\n{'='*70}")
    print(f"EXP 6: Companion curve analysis, n={n_order}, p={p}")
    print(f"{'='*70}")
    
    random.seed(42)
    a = [random.randint(0,p-1) for _ in range(3)]
    b = [random.randint(0,p-1) for _ in range(3)]
    
    r0,r1,r2 = compute_remainders(n_order, 3, a, b, p)
    print(f"Degrees: r0={poly_deg(r0)}, r1={poly_deg(r1)}, r2={poly_deg(r2)}")
    
    # The curve (r0(t), r1(t), r2(t)) has degree n-2 in F_p^3.
    # A point (1,0,0) can intersect a degree-d curve at most d times (Bezout).
    # But the REAL question is: does the curve have special structure
    # that limits how often it passes through (1,0,0)?
    
    # Check: is the map t -> (r0,r1,r2) birational? (i.e., generically injective)
    print("\nInjectivity test: evaluating (r0,r1,r2) at all t in F_p")
    images = {}
    for t in range(p):
        v = (poly_eval(r0,t,p), poly_eval(r1,t,p), poly_eval(r2,t,p))
        if v in images:
            images[v].append(t)
        else:
            images[v] = [t]
    
    collisions = {k:v for k,v in images.items() if len(v) > 1}
    print(f"  Distinct images: {len(images)}/{p}")
    print(f"  Collisions (same (r0,r1,r2), different t): {len(collisions)}")
    if collisions:
        for k,v in list(collisions.items())[:5]:
            print(f"    {k}: t = {v}")

def main():
    # Use parameters from the existing work
    print("="*70)
    print("COMPANION MATRIX ALGEBRAIC STRUCTURE EXPLORATION")
    print("="*70)
    
    # Start with n=10, p=11 (well-understood case)
    exp1_full_matrix(10, 11)
    exp2_resultants(10, 11, 100)
    exp3_all_nine_conditions(10, 11, 200)
    exp4_syzygy(10, 11)
    
    # Scaling analysis with larger p
    exp5_scaling(61)  # 61-1=60 has many divisors
    exp5_scaling(181) # 180 has many divisors
    
    # Curve analysis
    exp6_companion_deps(10, 11)
    exp6_companion_deps(10, 31)

if __name__ == '__main__':
    main()
