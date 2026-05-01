"""fri_2round_attack.py — Issue #344: is the 2× query overhead tight for FRI?

Setup:
  L_0 = <ω> ⊂ F_p*, |L_0| = n = 16.  Code C_0 = RS[L_0, k=8].
  L_1 = L_0² (size 8). Code C_1 = RS[L_1, 4].
  L_2 = L_1² (size 4). Code C_2 = RS[L_2, 2].

The FRI 2-round trace given f and (α₁, α₂):
  (f_e, f_o) = even/odd parts of f on L_1
  fold_1 = f_e + α₁ · f_o ∈ F_p^|L_1|
  ((fold_1)_e, (fold_1)_o) = even/odd parts of fold_1 on L_2
  fold_2 = (fold_1)_e + α₂ · (fold_1)_o ∈ F_p^|L_2|

A cheating prover (f, g_1, g_2) with g_i ∈ C_i wins at a uniform query y_1 ∈ L_1 iff
  g_1(y_1) = fold_1(y_1)  AND  g_2(y_1²) = fold_2(y_1²)
i.e. y_1 ∈ S_1(α₁) ∩ π⁻¹(S_2(α₁,α₂)),
where S_i = {agreement set of true fold_i with closest codeword},
π: L_1 → L_2 is x → x².

Cheater's optimal g_i = nearest codeword to true fold_i.

Per-query pass prob at fixed (α₁, α₂):
  P(α₁,α₂) = #{y_1 ∈ S_1(α₁) : y_1² ∈ S_2(α₁,α₂)} / |L_1|

We measure for each f:
  P_avg(f) = E_{α₁,α₂} P(α₁,α₂)
  P_max(f) = max_{α₁,α₂} P(α₁,α₂)

Compare to:
  (1 - δ/2) = 13/16 = 0.8125  (per our paper bound)
  (1 - δ)   = 5/8  = 0.625    (zero-loss target)

If P_max ≈ 0.8125: 2× tight. If between: room for improvement.
"""

from __future__ import annotations
import sys
import time
import random
from itertools import combinations
from math import comb


# ----------------------- field utilities -----------------------

def find_prim_root(p: int, n: int) -> int | None:
    if (p - 1) % n != 0:
        return None
    factors = set()
    t = n
    for q in range(2, n + 1):
        while t % q == 0:
            factors.add(q)
            t //= q
        if t == 1:
            break
    for g in range(2, p):
        w = pow(g, (p - 1) // n, p)
        if pow(w, n, p) != 1:
            continue
        if all(pow(w, n // q, p) != 1 for q in factors):
            return w
    return None


def modinv(a: int, p: int) -> int:
    return pow(a % p, p - 2, p)


# ----------------------- linear algebra over F_p -----------------------

def gauss_rank(rows, p):
    if not rows:
        return 0
    rows = [list(r) for r in rows]
    nrows = len(rows)
    ncols = len(rows[0])
    rank = 0
    col = 0
    while rank < nrows and col < ncols:
        pr = None
        for r in range(rank, nrows):
            if rows[r][col] % p != 0:
                pr = r
                break
        if pr is None:
            col += 1
            continue
        rows[rank], rows[pr] = rows[pr], rows[rank]
        inv = modinv(rows[rank][col], p)
        rows[rank] = [(x * inv) % p for x in rows[rank]]
        for r in range(nrows):
            if r != rank and rows[r][col] != 0:
                f = rows[r][col]
                rows[r] = [(rows[r][c] - f * rows[rank][c]) % p for c in range(ncols)]
        rank += 1
        col += 1
    return rank


def matvec(M, v, p):
    return [sum(M[i][j] * v[j] for j in range(len(v))) % p for i in range(len(M))]


# ----------------------- RS parity-check + distance -----------------------

def parity_check(L, n, k, p):
    """H[i,j] = ω^{-(k+i)j} so that H f = 0 iff f's DFT supported on [0, k)."""
    H = []
    for i in range(n - k):
        H.append([pow(L[j], (-(k + i)) % n, p) for j in range(n)])
    return H


def dist_to_code_full(f, H, n, k, p, max_w=None):
    """Returns (d, S) where d = dist(f, RS_k) and S ⊂ [n] is the agreement set
    of a closest codeword. Brute force: enumerate T = error-positions of size d."""
    syn = matvec(H, f, p)
    if all(x == 0 for x in syn):
        return 0, list(range(n))
    syn_dim = n - k
    H_cols = list(zip(*H))
    cap = max_w if max_w is not None else (n - k)
    for d in range(1, cap + 1):
        for T in combinations(range(n), d):
            A = [[H_cols[j][i] for j in T] for i in range(syn_dim)]
            rA = gauss_rank(A, p)
            A_s = [A[i] + [syn[i]] for i in range(syn_dim)]
            rA_s = gauss_rank(A_s, p)
            if rA_s == rA:
                # Found T; reconstruct error vector e supported on T.
                # Solve A · e_T = syn for the error values on T.
                e = solve_system(A, syn, p, T_size=len(T))
                if e is None:
                    continue
                # Codeword g = f - error vector (with error supported on T)
                err_vec = [0] * n
                for idx, j in enumerate(T):
                    err_vec[j] = e[idx]
                # Agreement = positions where err_vec == 0 = [n] \ T
                S = [j for j in range(n) if err_vec[j] == 0]
                return d, S
    return None, None  # dist > cap


def solve_system(A, b, p, T_size):
    """Solve A·x = b for x ∈ F_p^T_size. Returns x (any solution) or None."""
    syn_dim = len(b)
    aug = [list(A[i]) + [b[i]] for i in range(syn_dim)]
    ncols = T_size + 1
    pivot_col = {}
    rank = 0
    col = 0
    while rank < syn_dim and col < T_size:
        pr = None
        for r in range(rank, syn_dim):
            if aug[r][col] % p != 0:
                pr = r
                break
        if pr is None:
            col += 1
            continue
        aug[rank], aug[pr] = aug[pr], aug[rank]
        inv = modinv(aug[rank][col], p)
        aug[rank] = [(x * inv) % p for x in aug[rank]]
        for r in range(syn_dim):
            if r != rank and aug[r][col] != 0:
                f = aug[r][col]
                aug[r] = [(aug[r][c] - f * aug[rank][c]) % p for c in range(ncols)]
        pivot_col[col] = rank
        rank += 1
        col += 1
    # Inconsistent if any row has all zeros in cols 0..T_size-1 but nonzero last
    for r in range(rank, syn_dim):
        if aug[r][T_size] % p != 0:
            return None
    # Read off x: free vars = 0, pivots = aug[r][T_size]
    x = [0] * T_size
    for c, r in pivot_col.items():
        x[c] = aug[r][T_size] % p
    return x


# ----------------------- FRI even/odd folding -----------------------

def even_odd_parts(f, L_in, p):
    """Given f: L_in → F_p with L_in indexed s.t. L_in[i+n/2] = -L_in[i],
    return (f_e, f_o) on L_out = {x² : x ∈ L_in} (size n/2),
    indexed so L_out[i] = L_in[i]².

    f_e(y) = (f(x) + f(-x)) / 2
    f_o(y) = (f(x) - f(-x)) / (2x)
    where y = x²; we use x = L_in[i].
    """
    n_in = len(f)
    half = n_in // 2
    inv2 = modinv(2, p)
    f_e = [None] * half
    f_o = [None] * half
    for i in range(half):
        x = L_in[i]
        f_e[i] = ((f[i] + f[i + half]) * inv2) % p
        # 2x · f_o(y) = f(x) - f(-x); so f_o = (f(x) - f(-x))/(2x)
        f_o[i] = ((f[i] - f[i + half]) * inv2 * modinv(x, p)) % p
    return f_e, f_o


def setup_chain(p, n0, k0, R=2):
    """Build the FRI chain L_0 → L_1 → ... → L_R with proper indexing.
    Returns chain[i] = (L_i, k_i, H_i) for i = 0, 1, ..., R.
    L_i[j] = ω^{2^i · j} mod p where ω is primitive n_0-th root.
    """
    omega = find_prim_root(p, n0)
    if omega is None:
        raise ValueError(f"no primitive {n0}-th root mod {p}")
    chain = []
    n_cur = n0
    k_cur = k0
    omega_cur = omega
    for i in range(R + 1):
        L = [pow(omega_cur, j, p) for j in range(n_cur)]
        H = parity_check(L, n_cur, k_cur, p)
        chain.append((L, k_cur, H))
        n_cur //= 2
        k_cur //= 2
        omega_cur = (omega_cur * omega_cur) % p
    return chain


# ----------------------- 2-round FRI cheater analysis -----------------------

def R_round_pass_probs(f, chain, p, R=3, sample_alphas=None, rng=None):
    """For input f on L_0 and R rounds of FRI fold: enumerate (α_1,...,α_R) ∈ F_p^R
    and compute single-query pass for the optimal cheat-at-last cheater (cheats
    at the last round only; commits g_i = true_fold_i for i < R, g_R ∈ RS_{k_R}).

    For R rounds: per-query pass = 1 - d_R/|L_R|, where d_R = dist(true_fold_R, RS_{k_R}).

    sample_alphas: if int, sample roughly this many α-tuples; else full F_p^R grid.
    """
    L_chain = [chain[i][0] for i in range(R + 1)]
    k_chain = [chain[i][1] for i in range(R + 1)]
    H_chain = [chain[i][2] for i in range(R + 1)]
    n_chain = [len(L) for L in L_chain]

    if sample_alphas is None:
        alpha_lists = [list(range(p)) for _ in range(R)]
    else:
        if rng is None:
            rng = random.Random(0)
        per_dim = max(2, int(sample_alphas ** (1.0 / R)))
        alpha_lists = [rng.sample(range(p), min(per_dim, p)) for _ in range(R)]

    results = []  # list of (alpha-tuple, d_R, P)

    # Iterate (α_1, …, α_R) lexicographically.
    # For efficiency, cache true_fold_i for each prefix (α_1, ..., α_i).
    def recurse(level, fold_prev, alphas):
        if level == R:
            d_R, _ = dist_to_code_full(fold_prev, H_chain[R], n_chain[R], k_chain[R], p)
            if d_R is None:
                d_R = n_chain[R]
            P = 1.0 - d_R / n_chain[R]
            results.append((tuple(alphas), d_R, P))
            return
        f_e, f_o = even_odd_parts(fold_prev, L_chain[level], p)
        for a in alpha_lists[level]:
            fold_next = [(f_e[j] + a * f_o[j]) % p for j in range(n_chain[level + 1])]
            recurse(level + 1, fold_next, alphas + [a])

    recurse(0, f, [])
    return results


def two_round_pass_probs(f, chain, p, sample_alphas=None, rng=None):
    """For input f (on L_0), iterate over (α₁, α₂) and compute single-query
    pass prob P(α₁,α₂) for the optimal cheating prover.

    sample_alphas: if int, sample this many random (α₁, α₂); else full F_p² grid.
    """
    L0, k0, H0 = chain[0]
    L1, k1, H1 = chain[1]
    L2, k2, H2 = chain[2]
    n1 = len(L1)
    n2 = len(L2)

    # Even/odd of f on L_1
    f_e, f_o = even_odd_parts(f, L0, p)
    sq_idx = [j % n2 for j in range(n1)]

    if sample_alphas is None:
        a1_list = list(range(p))
        a2_list = list(range(p))
    else:
        if rng is None:
            rng = random.Random(0)
        # Sample distinct α_1's then for each enumerate α_2 (so d_1 cached)
        # Pick k = sqrt(sample_alphas) distinct α_1's, ditto α_2's
        import math
        k = max(1, int(math.sqrt(sample_alphas)))
        a1_list = rng.sample(range(p), min(k, p))
        a2_list = rng.sample(range(p), min(k, p))

    results = []
    for a1 in a1_list:
        # true fold 1
        fold1 = [(f_e[j] + a1 * f_o[j]) % p for j in range(n1)]
        d1, S1 = dist_to_code_full(fold1, H1, n1, k1, p)
        if d1 is None:
            d1 = n1  # treat as max
            S1 = []
        # even/odd of fold1
        g_e, g_o = even_odd_parts(fold1, L1, p)
        S1_set = set(S1)
        for a2 in a2_list:
            fold2 = [(g_e[j] + a2 * g_o[j]) % p for j in range(n2)]
            d2, S2 = dist_to_code_full(fold2, H2, n2, k2, p)
            if d2 is None:
                d2 = n2
                S2 = []
            S2_set = set(S2)
            # Strategy A (closest codeword at every level):
            #   Single-query pass per query at random y_1 ∈ L_1:
            #     pass iff y_1 ∈ S_1 (link 1) AND y_1² ∈ S_2 (link 2)
            count = 0
            for j in range(n1):
                if j in S1_set and sq_idx[j] in S2_set:
                    count += 1
            P_A = count / n1
            # Strategy B (cheat-at-last): commit g_1 = true_fold_1 (not in RS),
            # g_2 = closest codeword to true_fold_2 (only g_R must be RS).
            # Link 1 always passes (g_1 ≡ true_fold_1).
            # Link 2 passes iff g_2(y_2) = fold(g_1)(y_2) = true_fold_2(y_2).
            # Per-query pass at random y_1: pass iff y_1² ∈ S_2 = (n_1 - 2 d_2)/n_1 = 1 - d_2/n_2.
            P_B = 1.0 - d2 / n2
            # Cheater picks the better strategy
            P = max(P_A, P_B)
            results.append((a1, a2, d1, d2, P))
    return results


# ----------------------- driver -----------------------

def quick_dist_only(f, H, n, k, p, max_w):
    """Check if dist(f, RS_k) > max_w. Brute force; only used for verification."""
    syn = matvec(H, f, p)
    if all(x == 0 for x in syn):
        return False
    syn_dim = n - k
    H_cols = list(zip(*H))
    for d in range(1, max_w + 1):
        for T in combinations(range(n), d):
            A = [[H_cols[j][i] for j in T] for i in range(syn_dim)]
            rA = gauss_rank(A, p)
            A_s = [A[i] + [syn[i]] for i in range(syn_dim)]
            rA_s = gauss_rank(A_s, p)
            if rA_s == rA:
                return False
    return True


def true_dist(f, H, n, k, p, cap=None):
    """Compute dist(f, RS_k) by brute force. Returns the smallest d such that
    syndrome of f lies in col(H[:, T]) for some |T|=d, or cap+1 if dist > cap.
    """
    syn = matvec(H, f, p)
    if all(x == 0 for x in syn):
        return 0
    syn_dim = n - k
    H_cols = list(zip(*H))
    cap_ = cap if cap is not None else (n - k)
    for d in range(1, cap_ + 1):
        for T in combinations(range(n), d):
            A = [[H_cols[j][i] for j in T] for i in range(syn_dim)]
            rA = gauss_rank(A, p)
            A_s = [A[i] + [syn[i]] for i in range(syn_dim)]
            rA_s = gauss_rank(A_s, p)
            if rA_s == rA:
                return d
    return cap_ + 1


def poly_eval_horner(coeffs, x, p):
    val = 0
    for c in reversed(coeffs):
        val = (val * x + c) % p
    return val


def sample_far_input(p, n0, k0, w_target, rng, chain, verify=False):
    """Sample f = c + e where c is a random RS_k codeword and e has weight
    w_target. Almost always dist(f, RS_k) = w_target (random e rarely admits
    a shorter representation). With verify=True, brute-force confirm.
    """
    L0, _, H0 = chain[0]
    coeffs = [rng.randrange(p) for _ in range(k0)]
    c = [poly_eval_horner(coeffs, x, p) for x in L0]
    positions = rng.sample(range(n0), w_target)
    e = [0] * n0
    for j in positions:
        e[j] = rng.randrange(1, p)
    f = [(c[j] + e[j]) % p for j in range(n0)]
    if verify:
        d = true_dist(f, H0, n0, k0, p, cap=w_target)
        return f, d
    return f, None


def monomial_inputs(p, n0, omega, deg_range=(8, 16)):
    """Generate f = X^j on L_0 for j in deg_range."""
    L0 = [pow(omega, i, p) for i in range(n0)]
    out = []
    for j in range(deg_range[0], deg_range[1]):
        f = [pow(x, j, p) for x in L0]
        out.append((f"X^{j}", f))
    return out


def cs_lift_input(p, n0, omega, mode):
    """Construct an FRI input f on L_0 by lifting a CS-style adversarial pair
    on L_1 = L_0².

    mode = 'l1':  f_e = X^{r·m}|_{L_1}, f_o = X^{(r-1)m}|_{L_1} with CS at L_1 (size n0/2).
                  At n0=16: L_1 size 8, k_1=4. CS: m=1, r=5, s=8 → f_e=X^5, f_o=X^4.
                  Lifted: f(x) = (x²)^5 + x·(x²)^4 = x^{10} + x^{9}.
                  Predicted: 8 bad α₁'s in round 1.

    mode = 'l0':  CS directly at L_0 (size n0=16, k=k0=8). Then (f₁,f₂) = (X^{rm}, X^{(r-1)m}) on L_0.
                  CS: m=1, r=9, s=16 → (X^9, X^8) on L_0. δ=7/16 (above Johnson).
                  But this is NOT an FRI input (it's the (f₁,f₂) of CA, not f of FRI).
                  Need to combine into single FRI input: pick a γ, set f = X^9 + γ·X^8 on L_0.

    mode = 'l1_scale': Like 'l1' but with random scalars: f(x) = a·x^10 + b·x^9, randomized.
    """
    L0 = [pow(omega, i, p) for i in range(n0)]
    if mode == 'l1':
        # f(x) = x^10 + x^9
        f = [(pow(x, 10, p) + pow(x, 9, p)) % p for x in L0]
    elif mode == 'l1_only_e':
        # Just X^10, no odd part contribution
        f = [pow(x, 10, p) for x in L0]
    elif mode == 'l0_X9':
        # f = X^9 (a single CS-style monomial on L_0)
        f = [pow(x, 9, p) for x in L0]
    elif mode == 'l1_alt':
        # Try f_e = X^{r·m}, f_o = X^{(r-1)m} with different (m,r,s) at L_1
        # CS at L_1=size 8, k_1=4: alternative (m=2, r=4, s=4)? Then k_1=(r-2)m+1 = 5 ≠ 4.
        # No clean alternative for k_1=4. Skip.
        # Actually consider CS-shifted: f_e = c1·X^a + c2·X^b, f_o = ... with multiple monomials
        # in DFT support. Here just try (X^7, X^6) variant.
        f = [(pow(x, 14, p) + pow(x, 13, p)) % p for x in L0]
    else:
        raise ValueError(f"unknown mode {mode}")
    return f


def main():
    # --- Parameters ---
    n0 = 16
    k0 = 8
    p = 17  # start small
    delta_num = 6  # δ = 6/16 = 0.375 (above Johnson 0.293)
    if len(sys.argv) > 1:
        p = int(sys.argv[1])
    if len(sys.argv) > 2:
        delta_num = int(sys.argv[2])
    if len(sys.argv) > 5:
        n0 = int(sys.argv[5])
    if len(sys.argv) > 6:
        k0 = int(sys.argv[6])

    delta = delta_num / n0
    rho = k0 / n0
    delta_J = 1 - rho ** 0.5

    print(f"=" * 70, flush=True)
    print(f"FRI 2-round attack: n0={n0}, k0={k0}, p={p}, δ={delta:.4f} (δ_J={delta_J:.4f})", flush=True)
    print(f"  Per-paper bound (1-δ/2)^q baseline: 1-δ/2 = {1 - delta/2:.4f}", flush=True)
    print(f"  Zero-loss target  (1-δ)^q baseline:  1-δ   = {1 - delta:.4f}", flush=True)
    print(f"=" * 70, flush=True)

    chain = setup_chain(p, n0, k0)
    L0, _, H0 = chain[0]
    omega = L0[1]  # generator

    rng = random.Random(2026)
    n_samples = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    mode = sys.argv[4] if len(sys.argv) > 4 else 'random'
    summaries = []
    t_start = time.time()
    # Construct f
    w_target = delta_num + 1
    inputs = []
    if mode == 'random':
        for trial in range(n_samples):
            f, _ = sample_far_input(p, n0, k0, w_target, rng, chain, verify=False)
            inputs.append((f"random+wt{w_target}", f))
    elif mode == 'cs':
        # Various CS-style lifts
        for cs_mode in ['l1', 'l1_only_e', 'l0_X9', 'l1_alt']:
            f = cs_lift_input(p, n0, omega, cs_mode)
            inputs.append((f"cs:{cs_mode}", f))
    elif mode == 'cs_random':
        # CS construction perturbed by random codeword shift
        for trial in range(n_samples):
            f_cs = cs_lift_input(p, n0, omega, 'l1')
            coeffs = [rng.randrange(p) for _ in range(k0)]
            c = [poly_eval_horner(coeffs, x, p) for x in L0]
            f = [(f_cs[j] + c[j]) % p for j in range(n0)]
            inputs.append((f"cs:l1+rand_codeword", f))
    elif mode == 'mixed':
        for cs_mode in ['l1', 'l1_only_e', 'l0_X9']:
            f = cs_lift_input(p, n0, omega, cs_mode)
            inputs.append((f"cs:{cs_mode}", f))
        for trial in range(n_samples):
            f, _ = sample_far_input(p, n0, k0, w_target, rng, chain, verify=False)
            inputs.append((f"random+wt{w_target}", f))
    elif mode == 'monomial':
        # All monomials X^j for j ∈ [k0, n0]
        inputs = monomial_inputs(p, n0, omega, deg_range=(k0, n0))
    elif mode == 'monomial_few':
        # A few representative monomials: X^k0, X^{k0+1}, X^{n0-1}
        inputs = []
        for j in [k0, k0 + 1, k0 + 2, n0 - 2, n0 - 1]:
            L0 = [pow(omega, i, p) for i in range(n0)]
            f = [pow(x, j, p) for x in L0]
            inputs.append((f"X^{j}", f))
    elif mode == 'mono_pair':
        # All pairs X^a + b·X^c for a, c ∈ [k0, n0), b ∈ {1, ω, ω², ...}
        # Limit to a few representative pairs to keep runtime reasonable
        for a in range(k0, n0):
            for c in range(k0, a):
                for b_idx in range(0, n0, 4):
                    b = pow(omega, b_idx, p)
                    L0 = [pow(omega, i, p) for i in range(n0)]
                    f = [(pow(x, a, p) + b * pow(x, c, p)) % p for x in L0]
                    inputs.append((f"X^{a}+ω^{b_idx}·X^{c}", f))
    else:
        raise ValueError(f"unknown mode {mode}")

    skip_dist_check = (n0 > 16)  # too expensive; trust constructions
    sample_alphas = None if n0 <= 16 else 400  # 20×20 grid for n>16
    for trial, (label, f) in enumerate(inputs):
        if skip_dist_check:
            print(f"\n--- trial {trial} [{label}]: dist(f, C_0) check skipped (n={n0} too large)", flush=True)
        else:
            d0 = true_dist(f, H0, n0, k0, p, cap=min(delta_num + 1, n0 - k0))
            print(f"\n--- trial {trial} [{label}]: dist(f, C_0) {'=' if d0 <= delta_num else '>'}{d0}/{n0}", flush=True)
            if d0 <= delta_num:
                print(f"  [skip: dist {d0} ≤ δn={delta_num}, CA premise fails]", flush=True)
                continue
        results = two_round_pass_probs(f, chain, p, sample_alphas=sample_alphas, rng=rng)
        # Aggregate
        Ps = [r[4] for r in results]
        d1s = [r[2] for r in results]
        d2s = [r[3] for r in results]
        P_avg = sum(Ps) / len(Ps)
        P_max = max(Ps)
        P_min = min(Ps)
        d1_min = min(d1s)
        d2_min = min(d2s)
        # Report best (α1, α2)
        best_idx = max(range(len(results)), key=lambda i: results[i][4])
        a1_b, a2_b, d1_b, d2_b, P_b = results[best_idx]
        print(f"  P_avg = {P_avg:.4f}, P_max = {P_max:.4f}, P_min = {P_min:.4f}", flush=True)
        print(f"  d1_min = {d1_min}/{n0//2}, d2_min = {d2_min}/{n0//4}", flush=True)
        print(f"  best (α1={a1_b}, α2={a2_b}): d1={d1_b}, d2={d2_b}, P={P_b:.4f}", flush=True)
        # Distribution of (d1, d2) over (α1, α2)
        joint = {}
        for r in results:
            key = (r[2], r[3])
            joint[key] = joint.get(key, 0) + 1
        # Show top 5 most common
        top = sorted(joint.items(), key=lambda x: -x[1])[:5]
        print(f"  (d1,d2) joint dist (top 5): {top}", flush=True)
        # P_typical: average over (α₁, α₂) where BOTH d1 and d2 are typical
        # (i.e., away from the bad rounds). Use those with d1 ≥ d1_25 and d2 ≥ d2_25
        # where d1_25, d2_25 are the 25th-percentile distances.
        d1_sorted = sorted(d1s)
        d2_sorted = sorted(d2s)
        # Define typical = top 90% by distance (excluding the smallest 10%)
        thresh = max(1, int(0.1 * len(d1s)))
        d1_typ_min = d1_sorted[thresh]
        d2_typ_min = d2_sorted[thresh]
        typical_Ps = [r[4] for r in results if r[2] >= d1_typ_min and r[3] >= d2_typ_min]
        P_typical = max(typical_Ps) if typical_Ps else P_avg
        print(f"  P_typical = {P_typical:.4f} (worst single-query among non-bad rounds; d1≥{d1_typ_min}, d2≥{d2_typ_min})", flush=True)
        summaries.append({
            "trial": trial,
            "P_avg": P_avg, "P_max": P_max, "P_typical": P_typical,
            "d1_min": d1_min, "d2_min": d2_min,
            "best": (a1_b, a2_b, d1_b, d2_b, P_b),
            "joint_top": top,
        })

    elapsed = time.time() - t_start
    print(f"\n{'='*70}", flush=True)
    print(f"SUMMARY ({len(summaries)} inputs tested, {elapsed:.1f}s)", flush=True)
    print(f"{'='*70}", flush=True)
    print(f"  Theoretical baselines for q=1: (1-δ/2)={1-delta/2:.4f}, (1-δ)={1-delta:.4f}", flush=True)
    if summaries:
        worst_Pavg = max(s["P_avg"] for s in summaries)
        worst_Pmax = max(s["P_max"] for s in summaries)
        # Typical P (excluding bad rounds): use a quantile or non-extremal
        worst_Ptypical = max(s.get("P_typical", s["P_avg"]) for s in summaries)
        print(f"  Worst-case P_avg     (over f): {worst_Pavg:.4f}", flush=True)
        print(f"  Worst-case P_max     (over f): {worst_Pmax:.4f}  (1 bad-round event)", flush=True)
        print(f"  Worst-case P_typical (over f): {worst_Ptypical:.4f}  (≥1 round bad excluded)", flush=True)
        # Interpretation based on TYPICAL (since P_max is dominated by rare bad rounds)
        if worst_Ptypical >= 1 - delta / 2 - 1e-6:
            print(f"  ⇒ 2× tight: typical P_typical ≥ (1-δ/2). FRI bound saturated.", flush=True)
        elif worst_Ptypical <= 1 - delta + 1e-6:
            print(f"  ⇒ Zero-loss achievable: typical P_typical ≤ (1-δ). Bound improvable to 1×.", flush=True)
        else:
            c_eff = delta / (1 - worst_Ptypical)
            print(f"  ⇒ Effective c ≈ {c_eff:.3f} (1=zero-loss, 2=our bound)", flush=True)


if __name__ == "__main__":
    main()
