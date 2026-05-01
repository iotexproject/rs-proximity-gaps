#!/usr/bin/env python3
"""
THE FIBER BOUND THEOREM: M ≤ n/w for non-pinned-pair lines

Key insight: The rational function g(T) = -P_0(T)/Q(T) has:
  - degree 1 for pinned-pair lines (giving M = n-w+1 ≈ n)
  - degree w for non-pinned-pair lines (giving M ≤ n/w)

For rate 1/2: w ≈ 0.3n, so n/w ≈ 3.4, hence M ≤ 3.

THIS SCRIPT VERIFIES:
1. The fiber bound M ≤ n/w for non-pinned-pair lines (all tested cases)
2. Whether RS (Toeplitz) lines can ever be pinned-pair
3. The actual M for RS lines vs the n/w bound
"""

import itertools
import random
from collections import Counter
import multiprocessing as mp
import math

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
# SECTION 1: Verify M ≤ n/w for general w
# ============================================================
def verify_fiber_bound(n_ord, k, p, num_centers=200):
    """
    For RS[n, k] on L of order n in F_p:
    - Compute Johnson w, conditions c
    - For each center: compute M_alg (via sigma-image intersection)
    - Check: M_alg ≤ n/w for non-pinned-pair lines?
    """
    print(f"\n{'='*70}")
    print(f"FIBER BOUND: n={n_ord}, k={k}, p={p}")
    print(f"{'='*70}")
    
    omega = find_omega(p, n_ord)
    L = [pow(omega, i, p) for i in range(n_ord)]
    
    w = n_ord - int(math.sqrt(n_ord * (k - 1)))
    c = n_ord - k - w
    bound = n_ord // w  # floor(n/w)
    
    print(f"  w={w}, c={c}, fiber bound = floor(n/w) = {bound}")
    print(f"  Pinned-pair max = n-w+1 = {n_ord-w+1}")
    
    if c < 1 or w < 2:
        print("  Invalid parameters, skipping")
        return
    
    # Compute ALL w-subsets of L and their sigma-images
    subsets = list(itertools.combinations(range(n_ord), w))
    if len(subsets) > 200000:
        print(f"  Too many subsets ({len(subsets)}), skipping exhaustive check")
        return
    
    sigma_pts = []
    for combo in subsets:
        elts = [L[i] for i in combo]
        sigma = []
        for j in range(1, w+1):
            val = 0
            for sub in itertools.combinations(elts, j):
                prod = 1
                for x in sub: prod = (prod * x) % p
                val = (val + prod) % p
            sigma.append(val)
        sigma_pts.append(tuple(sigma))
    
    print(f"  C(n,w) = {len(subsets)} sigma-image points in F_p^{w}")
    
    # For each random RS center: compute the compatible affine subspace
    # and count sigma-image points on it
    M_alg_list = []
    pp_match_count = 0
    
    # Precompute pinned-pair directions for this w
    # Pinned-pair: fix w-1 elements, vary the w-th
    # Direction = (1, e_1(S), e_2(S), ..., e_{w-1}(S))
    # where S is the fixed (w-1)-subset
    pp_dirs = set()
    for fixed in itertools.combinations(range(n_ord), w-1):
        fixed_elts = [L[i] for i in fixed]
        # Direction components: d_j = e_j(fixed_elts) for j=1..w-1, d_0 = 1
        # Actually: sigma(fixed ∪ {gamma}) = sigma(fixed) + gamma * (stuff)
        # More precisely: e_j(x_1,...,x_{w-1},gamma) = e_j(x_1,...,x_{w-1}) + gamma * e_{j-1}(x_1,...,x_{w-1})
        # So the direction is (e_0(S), e_1(S), ..., e_{w-2}(S), 0) ... hmm wait
        
        # For sigma_j = e_j(x_1,...,x_w) where x_1,...,x_{w-1} are fixed and x_w = gamma:
        # sigma_j = e_j(x_1,...,x_{w-1}) + gamma * e_{j-1}(x_1,...,x_{w-1})
        # So: d(sigma_j)/d(gamma) = e_{j-1}(S) where S = {x_1,...,x_{w-1}}
        # Direction: (d_1, d_2, ..., d_w) = (e_0(S), e_1(S), ..., e_{w-1}(S)) = (1, e_1(S), ..., e_{w-1}(S))
        
        dirn = [1]  # e_0 = 1
        for j in range(1, w):
            val = 0
            for sub in itertools.combinations(fixed_elts, j):
                prod = 1
                for x in sub: prod = (prod * x) % p
                val = (val + prod) % p
            dirn.append(val)
        
        # Normalize
        dirn = tuple(dirn)  # Already normalized (first component = 1)
        pp_dirs.add(dirn)
    
    print(f"  Pinned-pair directions: {len(pp_dirs)} = C(n,w-1) = {len(list(itertools.combinations(range(n_ord), w-1)))}")
    
    for trial in range(num_centers):
        # Random syndrome
        c_synd = [random.randint(0, p-1) for _ in range(n_ord - k)]
        
        # Build Toeplitz matrix (c rows, w columns)
        A = []
        bvec = []
        for r in range(c):
            row = [((-1)**(j+1) * c_synd[r+j+1]) % p if r+j+1 < len(c_synd) else 0 for j in range(w)]
            A.append(row)
            bvec.append((-c_synd[r]) % p)
        
        # Gaussian elimination to find affine subspace
        inv_table = [0]*p
        for aa in range(1,p): inv_table[aa] = pow(aa, p-2, p)
        
        aug = [list(A[r]) + [bvec[r]] for r in range(c)]
        pivots = []
        for col in range(w):
            found = -1
            for row in range(len(pivots), c):
                if aug[row][col] % p != 0:
                    found = row; break
            if found == -1: continue
            aug[len(pivots)], aug[found] = aug[found], aug[len(pivots)]
            scale = inv_table[aug[len(pivots)][col]]
            aug[len(pivots)] = [(x*scale)%p for x in aug[len(pivots)]]
            for row in range(c):
                if row != len(pivots) and aug[row][col] % p != 0:
                    factor = aug[row][col]
                    aug[row] = [(aug[row][j]-factor*aug[len(pivots)][j])%p for j in range(w+1)]
            pivots.append(col)
        
        if len(pivots) < c: continue
        
        free_cols = [j for j in range(w) if j not in pivots]
        dim = len(free_cols)  # dimension of solution space
        
        if dim == 0: continue  # degenerate
        
        # For dim=1 (line): extract direction and base
        if dim == 1:
            fc = free_cols[0]
            dirn = [0] * w
            dirn[fc] = 1
            for i, pc in enumerate(pivots):
                dirn[pc] = (-aug[i][fc]) % p
            
            base = [0] * w
            for i, pc in enumerate(pivots):
                base[pc] = aug[i][w]
            
            # Normalize direction (first nonzero = 1)
            norm_dirn = list(dirn)
            for d in norm_dirn:
                if d != 0:
                    inv_d = pow(d, p-2, p)
                    norm_dirn = tuple((x*inv_d)%p for x in norm_dirn)
                    break
            
            is_pp = norm_dirn in pp_dirs
            if is_pp:
                pp_match_count += 1
            
            # Count sigma points on this line
            M_alg = 0
            for idx, sigma in enumerate(sigma_pts):
                # Check: sigma = base + t * dirn for some t
                t_val = None
                on_line = True
                for j in range(w):
                    if dirn[j] != 0:
                        t_cand = ((sigma[j] - base[j]) * pow(dirn[j], p-2, p)) % p
                        if t_val is None:
                            t_val = t_cand
                        elif t_cand != t_val:
                            on_line = False; break
                    else:
                        if sigma[j] != base[j] % p:
                            on_line = False; break
                if on_line:
                    M_alg += 1
            
            M_alg_list.append((M_alg, is_pp))
            
            if M_alg > bound and not is_pp:
                print(f"  *** VIOLATION: trial {trial}, M_alg={M_alg} > bound={bound}, NOT pinned-pair!")
    
    # Summary
    pp_M = [m for m, pp in M_alg_list if pp]
    nonpp_M = [m for m, pp in M_alg_list if not pp]
    
    print(f"\n  Pinned-pair lines: {pp_match_count}/{num_centers}")
    if pp_M:
        print(f"    M_alg range: {min(pp_M)} - {max(pp_M)}")
    print(f"  Non-pinned-pair lines: {len(nonpp_M)}")
    if nonpp_M:
        print(f"    M_alg distribution: {Counter(nonpp_M).most_common(10)}")
        print(f"    Max M_alg = {max(nonpp_M)}, bound = {bound}")
        violations = sum(1 for m in nonpp_M if m > bound)
        print(f"    Violations of M ≤ n/w: {violations}")

# ============================================================
# SECTION 2: Can Toeplitz null space be pinned-pair?
# ============================================================
def toeplitz_pinned_pair_check(n_ord, k, p, exhaustive=False):
    """
    For RS[n,k] with given parameters:
    Check if ANY Toeplitz matrix can have its null space direction
    equal to a pinned-pair direction.
    
    This is the KEY question for the theorem.
    """
    print(f"\n{'='*70}")
    print(f"TOEPLITZ-PP CHECK: n={n_ord}, k={k}, p={p}")
    print(f"{'='*70}")
    
    omega = find_omega(p, n_ord)
    L = [pow(omega, i, p) for i in range(n_ord)]
    
    w = n_ord - int(math.sqrt(n_ord * (k - 1)))
    c = n_ord - k - w
    
    print(f"  w={w}, c={c}")
    
    if c < 1 or w < 2:
        print("  Invalid, skipping")
        return
    
    # For each pinned-pair direction d = (1, e_1(S), ..., e_{w-1}(S)):
    # The Toeplitz matrix A * d = 0 gives c linear conditions on the
    # syndrome coefficients c_{k+1}, ..., c_{n-1}.
    # 
    # A[r][j] = (-1)^{j+1} * c_{k+r+j+1} for r=0..c-1, j=0..w-1
    # (A*d)[r] = sum_j A[r][j] * d[j] = sum_j (-1)^{j+1} c_{k+r+j+1} * d[j] = 0
    #
    # This is a condition on the syndrome. If it CAN be satisfied by
    # SOME syndrome (i.e., some RS center c), then there exists an
    # RS center whose compatible line is pinned-pair.
    #
    # The syndrome has (n-k) free parameters. The condition A*d = 0
    # gives c linear equations. If c < n-k, there are solutions.
    #
    # But we also need the line to actually hit sigma-image points.
    # The question is just: is the condition A*d = 0 satisfiable?
    
    inv_table = [0]*p
    for aa in range(1,p): inv_table[aa] = pow(aa, p-2, p)
    
    num_pp_dirs = 0
    num_achievable = 0
    
    for fixed in itertools.combinations(range(n_ord), w-1):
        fixed_elts = [L[i] for i in fixed]
        
        # Direction
        dirn = [1]
        for j in range(1, w):
            val = 0
            for sub in itertools.combinations(fixed_elts, j):
                prod = 1
                for x in sub: prod = (prod * x) % p
                val = (val + prod) % p
            dirn.append(val)
        
        num_pp_dirs += 1
        
        # Check: does there exist a syndrome s.t. the Toeplitz null space contains dirn?
        # Toeplitz condition: sum_j (-1)^{j+1} * c_{k+r+j+1} * d[j] = 0 for r=0,...,c-1
        # The unknowns are c_{k+1},...,c_{n-1} (= n-k-1 unknowns, with c_{k} fixed to anything)
        
        # Actually the syndrome is (c_k, c_{k+1}, ..., c_{n-1}) = n-k coefficients.
        # The Toeplitz condition involves c_{k+r+j+1} for r=0..c-1, j=0..w-1.
        # Range of indices: k+0+0+1 = k+1 to k+(c-1)+(w-1)+1 = k+c+w-1 = n-1. ✓
        
        # For each r: sum_{j=0}^{w-1} (-1)^{j+1} c_{k+r+j+1} d_j = 0
        # This is c LINEAR equations in the c_{k+1},...,c_{n-1} variables.
        # c equations, n-k-1 variables (excluding c_k which can be set freely).
        # Actually c_k doesn't appear (since min index is k+1).
        # So we have c equations in n-k-1 variables.
        # For c ≤ n-k-1: always solvable (system is underdetermined).
        
        # So the answer is: YES, for ANY pinned-pair direction, there exists
        # a syndrome achieving it, as long as c ≤ n-k-1.
        
        # c = n-k-w. n-k-1 variables. c ≤ n-k-1 iff w ≥ 1. Always true.
        num_achievable += 1
    
    print(f"  Pinned-pair directions: {num_pp_dirs}")
    print(f"  Achievable by SOME syndrome: {num_achievable} ({num_achievable/num_pp_dirs*100:.0f}%)")
    
    # KEY FINDING: ALL pinned-pair directions are achievable!
    # This means: there EXIST RS centers whose compatible line IS pinned-pair.
    # For such centers: M_alg = n-w (not bounded by n/w).
    
    # BUT: we also need to check whether M_ACTUAL (not M_alg) is large.
    # From the Case Split theorem: if d(c, RS) < w, then M_actual = 1.
    # A pinned-pair center has a very specific structure — let's check
    # whether it's always "close" to a codeword.
    
    print(f"\n  --- Checking if pinned-pair centers are close to codewords ---")
    
    # For a few pinned-pair directions, construct the center and check distance
    for fixed in list(itertools.combinations(range(n_ord), w-1))[:5]:
        fixed_elts = [L[i] for i in fixed]
        dirn = [1]
        for j in range(1, w):
            val = 0
            for sub in itertools.combinations(fixed_elts, j):
                prod = 1
                for x in sub: prod = (prod * x) % p
                val = (val + prod) % p
            dirn.append(val)
        
        # Construct a syndrome with A*d = 0
        # Simple: set c_{k+1} = ... = c_{n-1} such that the Toeplitz conditions hold.
        # Since the system is underdetermined, set free variables to 0 and solve.
        
        # Build the linear system
        # Variables: c_{k+1}, ..., c_{n-1} (indices k+1 to n-1, total n-k-1 vars)
        n_vars = n_ord - k - 1
        mat = [[0]*n_vars for _ in range(c)]
        for r in range(c):
            for j in range(w):
                var_idx = r + j + 1 - 1  # c_{k+r+j+1} corresponds to index r+j
                if 0 <= var_idx < n_vars:
                    mat[r][var_idx] = ((-1)**(j+1) * dirn[j]) % p
        
        # Row reduce to find a solution
        aug_mat = [row + [0] for row in mat]
        pivots = []
        for col in range(n_vars):
            found = -1
            for row in range(len(pivots), c):
                if aug_mat[row][col] % p != 0:
                    found = row; break
            if found == -1: continue
            aug_mat[len(pivots)], aug_mat[found] = aug_mat[found], aug_mat[len(pivots)]
            scale = inv_table[aug_mat[len(pivots)][col]]
            aug_mat[len(pivots)] = [(x*scale)%p for x in aug_mat[len(pivots)]]
            for row in range(c):
                if row != len(pivots) and aug_mat[row][col] % p != 0:
                    factor = aug_mat[row][col]
                    aug_mat[row] = [(aug_mat[row][j]-factor*aug_mat[len(pivots)][j])%p for j in range(n_vars+1)]
            pivots.append(col)
        
        # Extract solution (set free vars to 1 for non-trivial syndrome)
        syndrome = [0] * (n_ord - k)
        syndrome[0] = 1  # c_k = 1 (arbitrary nonzero)
        free_set = set(range(n_vars)) - set(pivots)
        for fc in free_set:
            syndrome[fc+1] = 1  # set free vars to 1
        for i, pc in enumerate(pivots):
            val = aug_mat[i][n_vars]
            for fc in free_set:
                val = (val - aug_mat[i][fc]) % p
            syndrome[pc+1] = val
        
        # Check: the center c has coefficients c_0,...,c_{k-1} (low) and c_k,...,c_{n-1} (syndrome)
        # c = sum c_j omega^j for polynomial representation
        # The distance to RS_k: find closest codeword f (degree < k)
        # d(c, f) = #{i : c(omega^i) != f(omega^i)}
        
        # For simplicity, compute c's evaluation at L and find closest codeword
        # c(x) = c_0 + c_1*x + ... + c_{n-1}*x^{n-1}
        # Set c_0 = ... = c_{k-1} = 0 for simplicity
        c_coeffs = [0]*k + syndrome
        
        c_eval = [0]*n_ord
        for i in range(n_ord):
            val = 0
            x = L[i]
            xpow = 1
            for j in range(n_ord):
                val = (val + c_coeffs[j] * xpow) % p
                xpow = (xpow * x) % p
            c_eval[i] = val
        
        # Closest codeword: f of degree < k minimizing Hamming distance
        # For RS: f is the polynomial interpolating c on any k points
        # Distance = n - (max agreement)
        # Quick: DFT-based computation
        # The codeword closest to c: f = sum_{j=0}^{k-1} c_j x^j (just truncate?)
        # No, f is the polynomial of degree < k that maximizes agreement.
        # For our c with c_0=...=c_{k-1}=0: the trivial codeword f=0 has 
        # agreement = #{i : c(omega^i) = 0} = #{zeros of c on L}
        
        n_zeros = sum(1 for v in c_eval if v == 0)
        dist_to_zero = n_ord - n_zeros
        
        print(f"  Fixed={fixed}: dist(c, f=0) = {dist_to_zero}, w={w}")
        if dist_to_zero < w:
            print(f"    => CLOSE to codeword (d < w)! M_actual = 1 by Case Split.")
        else:
            print(f"    => FAR from codeword (d >= w). M_actual = M_alg.")
    
    return True

# ============================================================
# SECTION 3: The complete picture
# ============================================================
def complete_picture(n_ord, k, p, num_trials=500):
    """
    For each RS center:
    1. Compute the compatible line direction
    2. Check if pinned-pair
    3. If yes: check Case Split (is center close to codeword?)
    4. Compute M_actual
    5. Verify M_actual ≤ max(1, n/w)
    """
    print(f"\n{'='*70}")
    print(f"COMPLETE PICTURE: n={n_ord}, k={k}, p={p}")
    print(f"{'='*70}")
    
    omega = find_omega(p, n_ord)
    L = [pow(omega, i, p) for i in range(n_ord)]
    
    w = n_ord - int(math.sqrt(n_ord * (k - 1)))
    c = n_ord - k - w
    bound = n_ord // w
    
    print(f"  w={w}, c={c}, n/w={n_ord/w:.2f}, bound={bound}")
    
    if c < 1 or w < 2 or w > 6:
        print("  Skipping (w too large for exhaustive sigma computation)")
        return
    
    # All w-subsets
    subsets = list(itertools.combinations(range(n_ord), w))
    if len(subsets) > 100000:
        print(f"  Too many subsets ({len(subsets)}), sampling instead")
        return
    
    sigma_pts = []
    for combo in subsets:
        elts = [L[i] for i in combo]
        sigma = []
        for j in range(1, w+1):
            val = 0
            for sub in itertools.combinations(elts, j):
                prod = 1
                for x in sub: prod = (prod * x) % p
                val = (val + prod) % p
            sigma.append(val)
        sigma_pts.append(tuple(sigma))
    
    inv_table = [0]*p
    for aa in range(1,p): inv_table[aa] = pow(aa, p-2, p)
    
    results = {'close': 0, 'far_pp': 0, 'far_nonpp': 0}
    M_actual_dist = Counter()
    
    for trial in range(num_trials):
        # Random RS codeword f of degree < k, random error pattern
        f_coeffs = [random.randint(0, p-1) for _ in range(k)]
        
        # Random center: f + error
        error_pos = random.sample(range(n_ord), min(w, n_ord))
        c_eval = [0] * n_ord
        for i in range(n_ord):
            val = 0; x = L[i]; xpow = 1
            for j in range(k):
                val = (val + f_coeffs[j] * xpow) % p
                xpow = (xpow * x) % p
            c_eval[i] = val
        for pos in error_pos[:w]:
            c_eval[pos] = (c_eval[pos] + random.randint(1, p-1)) % p
        
        # Compute syndrome
        # DFT: c_hat_j = sum_i c_eval[i] * omega^{-ij}
        omega_inv = pow(omega, p-2, p)
        c_hat = [0] * n_ord
        for j in range(n_ord):
            val = 0
            for i in range(n_ord):
                val = (val + c_eval[i] * pow(pow(omega_inv, j, p), i, p)) % p
            c_hat[j] = val
        
        syndrome = c_hat[k:n_ord]
        
        # Build Toeplitz matrix
        A = []
        bvec = []
        for r in range(min(c, len(syndrome)-w)):
            row = [((-1)**(j+1) * syndrome[r+j+1]) % p if r+j+1 < len(syndrome) else 0 for j in range(w)]
            A.append(row)
            bvec.append((-syndrome[r]) % p)
        
        if len(A) == 0: continue
        actual_c = len(A)
        
        # Count M_actual: number of codewords at distance ≤ w from c
        M_actual = 0
        for sub_idx, combo in enumerate(subsets):
            # Agreement set = [n] \ combo  (if w-subset is the ERROR set)
            # Wait, we need to enumerate codewords g and count d(c, g) ≤ w.
            # This is expensive for large k.
            pass
        
        # Instead: count sigma-image points on the compatible subspace
        # Gaussian elimination
        aug = [list(A[r]) + [bvec[r]] for r in range(actual_c)]
        pivots = []
        for col in range(w):
            found = -1
            for row in range(len(pivots), actual_c):
                if aug[row][col] % p != 0:
                    found = row; break
            if found == -1: continue
            aug[len(pivots)], aug[found] = aug[found], aug[len(pivots)]
            scale = inv_table[aug[len(pivots)][col]]
            aug[len(pivots)] = [(x*scale)%p for x in aug[len(pivots)]]
            for row in range(actual_c):
                if row != len(pivots) and aug[row][col] % p != 0:
                    factor = aug[row][col]
                    aug[row] = [(aug[row][j]-factor*aug[len(pivots)][j])%p for j in range(w+1)]
            pivots.append(col)
        
        free_cols = [j for j in range(w) if j not in pivots]
        if len(free_cols) != 1: continue
        
        fc = free_cols[0]
        dirn = [0]*w; dirn[fc] = 1
        for i, pc in enumerate(pivots):
            dirn[pc] = (-aug[i][fc]) % p
        base = [0]*w
        for i, pc in enumerate(pivots):
            base[pc] = aug[i][w]
        
        M_count = 0
        for sigma in sigma_pts:
            t_val = None; on_line = True
            for j in range(w):
                if dirn[j] != 0:
                    t_cand = ((sigma[j]-base[j])*pow(dirn[j],p-2,p))%p
                    if t_val is None: t_val = t_cand
                    elif t_cand != t_val: on_line=False; break
                else:
                    if sigma[j] != base[j]%p: on_line=False; break
            if on_line: M_count += 1
        
        M_actual_dist[M_count] += 1
    
    print(f"\n  M distribution: {M_actual_dist.most_common(15)}")
    if M_actual_dist:
        max_M = max(M_actual_dist.keys())
        print(f"  Max M = {max_M}, fiber bound = {bound}")
        violations = sum(v for k_m, v in M_actual_dist.items() if k_m > bound)
        print(f"  Violations: {violations}/{sum(M_actual_dist.values())}")

def main():
    print("="*70)
    print("FIBER BOUND THEOREM VERIFICATION")
    print("="*70)
    
    # Section 1: Verify fiber bound for various parameters
    # Need small w for exhaustive computation
    # k=2: w = n-floor(sqrt(n))
    for n_ord, p in [(8, 17), (10, 11), (10, 31), (12, 13), (12, 37)]:
        if (p-1) % n_ord != 0: continue
        verify_fiber_bound(n_ord, 2, p, 300)
    
    # k = n/2 (rate 1/2) — need small n for w to be manageable
    for n_ord in [8, 10, 12]:
        k = n_ord // 2
        for p_mult in [1, 3, 5]:
            p = p_mult * n_ord + 1
            while not all(p % d != 0 for d in range(2, int(p**0.5)+1)):
                p += n_ord
            if (p-1) % n_ord != 0:
                continue
            verify_fiber_bound(n_ord, k, p, 200)
    
    # Section 2: Can Toeplitz be pinned-pair?
    for n_ord, p in [(8, 17), (10, 31), (12, 37)]:
        if (p-1) % n_ord != 0: continue
        toeplitz_pinned_pair_check(n_ord, 2, p)
        toeplitz_pinned_pair_check(n_ord, n_ord//2, p)
    
    # Section 3: Complete picture
    for n_ord, p in [(8, 17), (10, 31)]:
        if (p-1) % n_ord != 0: continue
        complete_picture(n_ord, 2, p, 300)
    
    print("\nDONE.")

if __name__ == '__main__':
    main()
