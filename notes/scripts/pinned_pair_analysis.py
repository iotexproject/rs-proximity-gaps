#!/usr/bin/env python3
"""
PINNED-PAIR ANALYSIS: the key to O(n)->O(1)

CORE INSIGHT from experiments:
  Max collinear = n-2 is achieved by "pinned-pair" lines: all w-subsets
  share w-1 elements, with one element varying through L.

  For w=3: fix alpha, beta in L. Direction = (1, alpha+beta, alpha*beta).
  The line passes through n-2 sigma-image points (one for each gamma != alpha, beta).

PROOF STRATEGY:
  1. Show that max collinear = n-2 is ONLY achieved by pinned-pair lines
  2. Count how many pinned-pair directions exist: C(n,2) = n(n-1)/2
  3. For a RANDOM line: probability of being pinned-pair ~ n^2/p^2 -> 0
  4. For a NON-pinned-pair line: max collinear is O(n/p + sqrt(n))
  5. For RS (Toeplitz) lines: additional structure prevents pinned-pair alignment

This script explores all of this computationally.
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

# ============================================================
# SECTION 1: Verify "only pinned-pair gives n-2"
# ============================================================
def verify_pinned_pair(n_ord, p):
    """
    For each line achieving max collinear, check if it's pinned-pair.
    """
    print(f"\n{'='*70}")
    print(f"VERIFY PINNED-PAIR: n={n_ord}, p={p}")
    print(f"{'='*70}")
    
    omega = find_omega(p, n_ord)
    L = [pow(omega, i, p) for i in range(n_ord)]
    
    # All 3-subsets -> sigma points
    subsets = list(itertools.combinations(range(n_ord), 3))
    sigma_map = {}  # sigma -> subset index
    sigma_pts = []
    for idx, combo in enumerate(subsets):
        elts = [L[i] for i in combo]
        s1 = sum(elts) % p
        s2 = (elts[0]*elts[1] + elts[0]*elts[2] + elts[1]*elts[2]) % p
        s3 = (elts[0]*elts[1]*elts[2]) % p
        sigma_pts.append((s1, s2, s3))
        sigma_map[(s1,s2,s3)] = combo
    
    # Build line index: for each pair of sigma points, record the line
    # and count how many points lie on it
    # Use direction as key (projective)
    
    line_info = defaultdict(list)  # (normalized_direction, base_representative) -> list of point indices
    
    # For efficiency: only check pairs that could give high collinearity
    # First: enumerate ALL pinned-pair lines
    print(f"\n  --- Pinned-pair lines ---")
    pinned_pair_lines = []
    for a, b in itertools.combinations(range(n_ord), 2):
        # Direction: (1, L[a]+L[b], L[a]*L[b])
        d1 = 1
        d2 = (L[a] + L[b]) % p
        d3 = (L[a] * L[b]) % p
        
        # Find all sigma points on this line
        # A sigma point (s1,s2,s3) is on the line through (s1_0, s2_0, s3_0) with direction (d1,d2,d3)
        # iff (s1-s1_0, s2-s2_0, s3-s3_0) is proportional to (d1,d2,d3)
        
        # The sigma points for subsets {a, b, c} where c != a, b
        pts_on_line = []
        for c in range(n_ord):
            if c == a or c == b:
                continue
            combo = tuple(sorted([a, b, c]))
            idx = subsets.index(combo)
            pts_on_line.append(idx)
        
        pinned_pair_lines.append((a, b, len(pts_on_line), (d1,d2,d3)))
    
    max_pp = max(x[2] for x in pinned_pair_lines)
    print(f"  Number of pinned-pair lines: {len(pinned_pair_lines)} = C({n_ord},2)")
    print(f"  Points on each pinned-pair line: {max_pp} = n-2")
    
    # Now: find ALL lines with max_pp collinear
    # Check all pairs of sigma points, find lines with >= max_pp - 1 collinear
    print(f"\n  --- Searching for ALL lines with >= {max_pp-1} collinear ---")
    
    high_collinear_lines = []
    checked = 0
    for i in range(len(sigma_pts)):
        for j in range(i+1, len(sigma_pts)):
            dx = (sigma_pts[j][0] - sigma_pts[i][0]) % p
            dy = (sigma_pts[j][1] - sigma_pts[i][1]) % p
            dz = (sigma_pts[j][2] - sigma_pts[i][2]) % p
            
            # Count points on this line
            count = 0
            pts_on = []
            for k in range(len(sigma_pts)):
                cx = (sigma_pts[k][0] - sigma_pts[i][0]) % p
                cy = (sigma_pts[k][1] - sigma_pts[i][1]) % p
                cz = (sigma_pts[k][2] - sigma_pts[i][2]) % p
                if ((cy*dz - cz*dy) % p == 0 and
                    (cz*dx - cx*dz) % p == 0 and
                    (cx*dy - cy*dx) % p == 0):
                    count += 1
                    pts_on.append(k)
            
            if count >= max_pp - 1:
                # Normalize direction
                for d in [dx, dy, dz]:
                    if d != 0:
                        inv_d = pow(d, p-2, p)
                        dx, dy, dz = (dx*inv_d)%p, (dy*inv_d)%p, (dz*inv_d)%p
                        break
                high_collinear_lines.append((count, (dx,dy,dz), pts_on))
            
            checked += 1
    
    # Deduplicate by direction
    unique_lines = {}
    for count, dirn, pts in high_collinear_lines:
        key = dirn
        if key not in unique_lines or unique_lines[key][0] < count:
            unique_lines[key] = (count, pts)
    
    print(f"  Checked {checked} pairs")
    print(f"  Lines with >= {max_pp-1} collinear: {len(unique_lines)}")
    
    # Check: are ALL max-collinear lines pinned-pair?
    pp_directions = set()
    for a, b, cnt, dirn in pinned_pair_lines:
        pp_directions.add(dirn)
    
    max_non_pp = 0
    for dirn, (count, pts) in unique_lines.items():
        if count == max_pp and dirn not in pp_directions:
            print(f"  *** NON-PINNED-PAIR LINE with max collinear! dir={dirn}, count={count}")
            # Analyze: what subsets are on this line?
            for idx in pts:
                print(f"      subset {subsets[idx]}")
        if dirn not in pp_directions:
            max_non_pp = max(max_non_pp, count)
    
    print(f"\n  Max collinear on pinned-pair lines: {max_pp}")
    print(f"  Max collinear on NON-pinned-pair lines: {max_non_pp}")
    
    # Second-highest collinear structure
    print(f"\n  Collinear distribution (all unique lines):")
    count_dist = Counter(count for count, _ in unique_lines.values())
    for cnt, freq in sorted(count_dist.items(), reverse=True):
        if freq <= 10:
            print(f"    {cnt} collinear: {freq} lines")
        else:
            print(f"    {cnt} collinear: {freq} lines")
    
    return max_pp, max_non_pp

# ============================================================
# SECTION 2: Non-pinned-pair bound as function of n and p
# ============================================================
def non_pinned_pair_bound(n_ord, p, num_random=500):
    """
    For non-pinned-pair lines: what is the maximum collinear?
    
    Theory predicts: O(n^2/p) from density argument.
    """
    print(f"\n{'='*70}")
    print(f"NON-PINNED-PAIR BOUND: n={n_ord}, p={p}")
    print(f"{'='*70}")
    
    omega = find_omega(p, n_ord)
    L = [pow(omega, i, p) for i in range(n_ord)]
    
    subsets = list(itertools.combinations(range(n_ord), 3))
    sigma_pts = []
    for combo in subsets:
        elts = [L[i] for i in combo]
        s1 = sum(elts) % p
        s2 = (elts[0]*elts[1] + elts[0]*elts[2] + elts[1]*elts[2]) % p
        s3 = (elts[0]*elts[1]*elts[2]) % p
        sigma_pts.append((s1, s2, s3))
    
    # Pinned-pair directions
    pp_dirs = set()
    for a, b in itertools.combinations(range(n_ord), 2):
        d1 = 1
        d2 = (L[a] + L[b]) % p
        d3 = (L[a] * L[b]) % p
        pp_dirs.add((d1, d2, d3))
    
    # Sample random lines and count collinear, separating pinned-pair from not
    max_pp = 0
    max_non_pp = 0
    pp_counts = []
    non_pp_counts = []
    
    for trial in range(num_random):
        # Random line through two random sigma-image points
        i, j = random.sample(range(len(sigma_pts)), 2)
        dx = (sigma_pts[j][0] - sigma_pts[i][0]) % p
        dy = (sigma_pts[j][1] - sigma_pts[i][1]) % p
        dz = (sigma_pts[j][2] - sigma_pts[i][2]) % p
        
        # Normalize
        for d in [dx, dy, dz]:
            if d != 0:
                inv_d = pow(d, p-2, p)
                dx, dy, dz = (dx*inv_d)%p, (dy*inv_d)%p, (dz*inv_d)%p
                break
        
        is_pp = (dx, dy, dz) in pp_dirs
        
        count = 0
        for k in range(len(sigma_pts)):
            cx = (sigma_pts[k][0] - sigma_pts[i][0]) % p
            cy = (sigma_pts[k][1] - sigma_pts[i][1]) % p
            cz = (sigma_pts[k][2] - sigma_pts[i][2]) % p
            if ((cy*dz - cz*dy) % p == 0 and
                (cz*dx - cx*dz) % p == 0 and
                (cx*dy - cy*dx) % p == 0):
                count += 1
        
        if is_pp:
            pp_counts.append(count)
            max_pp = max(max_pp, count)
        else:
            non_pp_counts.append(count)
            max_non_pp = max(max_non_pp, count)
    
    N = len(sigma_pts)
    expected_random = N / p**2  # expected on random line
    
    print(f"  N = C({n_ord},3) = {N}, expected on random line = N/p^2 = {expected_random:.2f}")
    print(f"  Pinned-pair lines sampled: {len(pp_counts)}")
    if pp_counts:
        print(f"    max = {max_pp}, avg = {sum(pp_counts)/len(pp_counts):.1f}")
    print(f"  Non-pinned-pair lines sampled: {len(non_pp_counts)}")
    if non_pp_counts:
        print(f"    max = {max_non_pp}, avg = {sum(non_pp_counts)/len(non_pp_counts):.1f}")
        print(f"    distribution: {Counter(non_pp_counts).most_common(10)}")
    
    # KEY: the "second maximum" (non-pinned-pair) should be O(1)
    # More precisely: O(n^2/p) from the "one shared element" construction
    
    # One-shared-element lines: fix alpha. Subsets {alpha, beta, gamma}
    # and {alpha, delta, epsilon} share alpha. Their sigma points:
    # s1 = alpha + beta + gamma, s2 = alpha*beta + ..., s3 = alpha*beta*gamma
    # The direction between these two points depends on both pairs.
    # NOT a single parameterized family like pinned-pair.
    
    print(f"\n  Theoretical predictions:")
    print(f"    Pinned-pair: n-2 = {n_ord-2}")
    print(f"    One-shared: ~ C(n-1,2)/p = {(n_ord-1)*(n_ord-2)//2}/{p} = {(n_ord-1)*(n_ord-2)/(2*p):.1f}")
    print(f"    No-shared (random): ~ N/p^2 = {expected_random:.2f}")

# ============================================================
# SECTION 3: Toeplitz line avoidance of pinned-pair directions
# ============================================================
def toeplitz_avoidance(n_ord, p, num_trials=1000):
    """
    For RS centers, the compatible sigma-subspace has Toeplitz structure.
    Check: does the Toeplitz direction ever match a pinned-pair direction?
    """
    print(f"\n{'='*70}")
    print(f"TOEPLITZ AVOIDANCE: n={n_ord}, p={p}")
    print(f"{'='*70}")
    
    k = n_ord // 2  # rate 1/2
    omega = find_omega(p, n_ord)
    L = [pow(omega, i, p) for i in range(n_ord)]
    w = n_ord - int(n_ord**0.5 * (k-1)**0.5)  # approximate Johnson radius
    # For rate 1/2: w ≈ n - sqrt(n*k) ≈ n - n/sqrt(2) ≈ n(1-1/sqrt(2))
    # Actually w = n - floor(sqrt(n(k-1)))
    import math
    w = n_ord - int(math.sqrt(n_ord * (k - 1)))
    conds = n_ord - k - w
    
    print(f"  k={k}, w={w}, conds={conds}")
    
    if w != 3 or conds != 2:
        print(f"  Skipping: need w=3, conds=2 for this analysis")
        return
    
    # Pinned-pair directions
    pp_dirs = set()
    for a, b in itertools.combinations(range(n_ord), 2):
        d1 = 1
        d2 = (L[a] + L[b]) % p
        d3 = (L[a] * L[b]) % p
        pp_dirs.add((d1, d2, d3))
    
    # For each RS center (random syndrome), compute the Toeplitz line direction
    # and check if it matches any pinned-pair direction
    match_count = 0
    m_alg_pp = []  # M_alg for pinned-pair matching lines
    m_alg_nonpp = []  # M_alg for non-matching lines
    
    for trial in range(num_trials):
        # Random syndrome
        c_synd = [random.randint(0, p-1) for _ in range(n_ord - k)]
        if all(c == 0 for c in c_synd):
            continue
        
        # Toeplitz matrix (conds x w)
        A = []
        bvec = []
        for r in range(conds):
            row = [((-1)**(j+1) * c_synd[r+j+1]) % p for j in range(w)]
            A.append(row)
            bvec.append((-c_synd[r]) % p)
        
        # Solve for the line: Ax = bvec
        inv_table = [0]*p
        for aa in range(1,p): inv_table[aa] = pow(aa, p-2, p)
        
        aug = [list(A[r]) + [bvec[r]] for r in range(conds)]
        pivots = []
        for col in range(w):
            found = -1
            for row in range(len(pivots), conds):
                if aug[row][col] % p != 0:
                    found = row; break
            if found == -1: continue
            aug[len(pivots)], aug[found] = aug[found], aug[len(pivots)]
            scale = inv_table[aug[len(pivots)][col]]
            aug[len(pivots)] = [(x*scale)%p for x in aug[len(pivots)]]
            for row in range(conds):
                if row != len(pivots) and aug[row][col] % p != 0:
                    factor = aug[row][col]
                    aug[row] = [(aug[row][j]-factor*aug[len(pivots)][j])%p for j in range(w+1)]
            pivots.append(col)
        
        if len(pivots) != conds: continue
        
        free_cols = [j for j in range(w) if j not in pivots]
        if not free_cols: continue
        fc = free_cols[0]
        
        # Direction of the line in sigma-space
        dirn = [0] * w
        dirn[fc] = 1
        for i, pc in enumerate(pivots):
            dirn[pc] = (-aug[i][fc]) % p
        
        # Normalize direction
        for d in dirn:
            if d != 0:
                inv_d = pow(d, p-2, p)
                dirn = tuple((x*inv_d)%p for x in dirn)
                break
        else:
            continue
        
        is_pp = dirn in pp_dirs
        if is_pp:
            match_count += 1
        
        # Compute M_alg on this line (count sigma-image points)
        # Base point
        base = [0] * w
        base[fc] = 0
        for i, pc in enumerate(pivots):
            base[pc] = aug[i][w]
        
        count = 0
        for combo in itertools.combinations(range(n_ord), w):
            elts = [L[i] for i in combo]
            sigma = [0] * w
            for j in range(1, w+1):
                val = 0
                for sub in itertools.combinations(elts, j):
                    prod = 1
                    for x in sub: prod = (prod * x) % p
                    val = (val + prod) % p
                sigma[j-1] = val
            
            # Check if sigma is on the line: sigma = base + t * dirn
            # Find t from first non-zero dirn component
            t_val = None
            on_line = True
            for j in range(w):
                if dirn[j] != 0:
                    t_cand = ((sigma[j] - base[j]) * pow(dirn[j], p-2, p)) % p
                    if t_val is None:
                        t_val = t_cand
                    elif t_cand != t_val:
                        on_line = False
                        break
                else:
                    if sigma[j] != base[j]:
                        on_line = False
                        break
            if on_line:
                count += 1
        
        if is_pp:
            m_alg_pp.append(count)
        else:
            m_alg_nonpp.append(count)
    
    print(f"\n  Pinned-pair matches: {match_count}/{num_trials} = {match_count/num_trials:.4f}")
    print(f"  Expected by chance: C({n_ord},2)/p^2 = {n_ord*(n_ord-1)/2}/{p**2} = {n_ord*(n_ord-1)/(2*p**2):.4f}")
    
    if m_alg_pp:
        print(f"\n  M_alg on PP lines: {Counter(m_alg_pp).most_common(5)}")
    if m_alg_nonpp:
        print(f"  M_alg on non-PP lines: {Counter(m_alg_nonpp).most_common(5)}")

# ============================================================
# SECTION 4: FRI-realistic parameter sweep (parallel)
# ============================================================
def fri_realistic_worker(args):
    """Worker for FRI parameter sweep."""
    n_ord, p, line_a, line_b = args
    
    # Poly arithmetic (inline for multiprocessing)
    def pa(a,b,p):
        n=max(len(a),len(b)); r=[0]*n
        for i in range(len(a)): r[i]=(r[i]+a[i])%p
        for i in range(len(b)): r[i]=(r[i]+b[i])%p
        while len(r)>1 and r[-1]==0: r.pop()
        return r
    def ps(a,b,p): return pa(a,[(-x)%p for x in b],p)
    def pm(a,b,p):
        if a==[0] or b==[0]: return [0]
        r=[0]*(len(a)+len(b)-1)
        for i in range(len(a)):
            for j in range(len(b)):
                r[i+j]=(r[i+j]+a[i]*b[j])%p
        while len(r)>1 and r[-1]==0: r.pop()
        return r
    def pd(a): return -1 if a==[0] else len(a)-1
    def pdm(a,b,p):
        if b==[0]: raise ZeroDivisionError
        if pd(a)<pd(b): return [0],list(a)
        il=pow(b[-1],p-2,p); a=list(a); q=[0]*(len(a)-len(b)+1)
        for i in range(len(a)-len(b),-1,-1):
            c=(a[i+len(b)-1]*il)%p; q[i]=c
            for j in range(len(b)): a[i+j]=(a[i+j]-c*b[j])%p
        while len(a)>1 and a[-1]==0: a.pop()
        while len(q)>1 and q[-1]==0: q.pop()
        return q,a
    def pg(a,b,p):
        while b!=[0]:
            _,r=pdm(a,b,p)
            a,b=b,r
        if a!=[0]:
            il=pow(a[-1],p-2,p)
            a=[(x*il)%p for x in a]
        return a
    
    s1=[line_a[0],line_b[0]]; s2=[line_a[1],line_b[1]]; s3=[line_a[2],line_b[2]]
    for s in [s1,s2,s3]:
        while len(s)>1 and s[-1]==0: s.pop()
    ak=[1]; bk=[0]; ck=[0]
    for step in range(n_ord):
        nak=pm(s3,ck,p)
        nbk=ps(ak,pm(s2,ck,p),p)
        nck=pa(bk,pm(s1,ck,p),p)
        ak,bk,ck=nak,nbk,nck
    
    r0m1=ps(ak,[1],p)
    g=pg(r0m1,bk,p)
    g=pg(g,ck,p)
    return pd(g)

def fri_sweep(n_ord, p, num_lines=5000):
    """Sweep for FRI-realistic parameters."""
    print(f"\n{'='*70}")
    print(f"FRI SWEEP: n={n_ord}, p={p}, p/n={p/n_ord:.1f}")
    print(f"{'='*70}")
    
    random.seed(42)
    tasks = []
    for _ in range(num_lines):
        a = [random.randint(0,p-1) for _ in range(3)]
        b = [random.randint(0,p-1) for _ in range(3)]
        while all(x==0 for x in b):
            b = [random.randint(0,p-1) for _ in range(3)]
        tasks.append((n_ord, p, a, b))
    
    t0 = time.time()
    with mp.Pool(24) as pool:
        results = pool.map(fri_realistic_worker, tasks)
    elapsed = time.time() - t0
    
    N = n_ord*(n_ord-1)*(n_ord-2)//6
    expected = N / p**2
    
    print(f"  Time: {elapsed:.1f}s")
    print(f"  C(n,3)/p^2 = {N}/{p**2} = {expected:.3f}")
    print(f"  GCD distribution: {Counter(results).most_common(10)}")
    print(f"  Max gcd = {max(results)}, Bezout = {n_ord-2}")
    
    return max(results)

# ============================================================
# SECTION 5: Transition analysis p/n ratio
# ============================================================
def transition_analysis():
    """Find the p/n threshold where max gcd drops from O(n) to O(1)."""
    print(f"\n{'='*70}")
    print(f"TRANSITION ANALYSIS: p/n vs max gcd")
    print(f"{'='*70}")
    
    results = []
    
    for n_ord in [10, 12, 16, 20, 24, 30]:
        for p_mult in [1, 2, 3, 5, 8, 13, 21]:
            # Find p = p_mult*n + 1 that's prime and n | p-1
            cand = p_mult * n_ord + 1
            # Find next prime with n | p-1
            for offset in range(0, 1000, n_ord):
                p = cand + offset
                if p < 3: continue
                if all(p % d != 0 for d in range(2, int(p**0.5)+1)):
                    if (p-1) % n_ord == 0:
                        break
            else:
                continue
            
            random.seed(42)
            tasks = []
            num_lines = 2000
            for _ in range(num_lines):
                a = [random.randint(0,p-1) for _ in range(3)]
                b = [random.randint(0,p-1) for _ in range(3)]
                while all(x==0 for x in b):
                    b = [random.randint(0,p-1) for _ in range(3)]
                tasks.append((n_ord, p, a, b))
            
            with mp.Pool(24) as pool:
                gcds = pool.map(fri_realistic_worker, tasks)
            
            max_gcd = max(gcds)
            avg_gcd = sum(gcds) / len(gcds)
            N = n_ord*(n_ord-1)*(n_ord-2)//6
            
            results.append((n_ord, p, p/n_ord, max_gcd, avg_gcd, N/p**2))
            print(f"  n={n_ord:3d}, p={p:5d}, p/n={p/n_ord:5.1f}: "
                  f"max_gcd={max_gcd:3d}, avg={avg_gcd:.2f}, N/p^2={N/p**2:.3f}")
    
    # Print summary table
    print(f"\n  --- Summary: max_gcd vs p/n ---")
    print(f"  {'n':>4} {'p':>6} {'p/n':>6} {'max_gcd':>8} {'N/p^2':>8} {'bound_tight':>12}")
    for n_ord, p, ratio, mg, ag, Np2 in sorted(results, key=lambda x: (x[0], x[2])):
        tight = "YES" if mg >= n_ord-3 else "no"
        print(f"  {n_ord:4d} {p:6d} {ratio:6.1f} {mg:8d} {Np2:8.3f} {tight:>12}")

def main():
    print("="*70)
    print("PINNED-PAIR STRUCTURE ANALYSIS")
    print("="*70)
    
    # Section 1: Verify pinned-pair uniqueness for small cases
    for n_ord, p in [(8, 17), (10, 11), (10, 31)]:
        verify_pinned_pair(n_ord, p)
    
    # Section 2: Non-pinned-pair bound
    for n_ord, p in [(10, 31), (12, 37), (16, 97)]:
        if (p-1) % n_ord == 0:
            non_pinned_pair_bound(n_ord, p, 500)
    
    # Section 3: Toeplitz avoidance
    for n_ord, p in [(10, 11), (10, 31)]:
        toeplitz_avoidance(n_ord, p, 500)
    
    # Section 4: FRI-realistic sweep
    for n_ord, p in [(32, 97), (64, 193), (128, 257)]:
        if (p-1) % n_ord == 0:
            fri_sweep(n_ord, p, 3000)
    
    # Section 5: Transition analysis
    transition_analysis()
    
    print("\n\nDONE.")

if __name__ == '__main__':
    main()
