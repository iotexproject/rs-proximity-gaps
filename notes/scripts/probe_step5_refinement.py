"""probe_step5_refinement.py — verify EXACT formula for dist(f, C_0) when image rank 1.

For rank-1 above-J f: $g_α = c(α) + ψ(α) · e$ with $H_R e = v_0$, $\\wt(e) = w'$.
Setting $\\tildeψ(x) = \\sum_b x^b μ_b$ (univariate, deg < 2^R):

    $f(x) - f_c(x) = e_y · \\tildeψ(x)$  where $y = x^{2^R}$.

Hence (when $w' ≤ m$, forcing $d_b ≡ 0$ in any alternative codeword):
    dist(f, C_0) ≤ 2^R · w' - Z   where  Z = #zeros of $\\tildeψ$ in $\\bigcup_{y∈T}$ coset(y).

Above-J: $2^R w' - Z > w_J$  ⟹  $w' > (w_J + Z)/2^R ≥ w_J/2^R$  (Johnson).

Question this probe answers:
  - Is the bound tight? Does dist = $2^R w' - Z$ in practice?
  - What is the empirical distribution of $|S|, w', Z$?
  - Does $Z > 0$ ever happen, giving a tighter $w'$ lower bound?
"""
from __future__ import annotations
import sys, math, random
from itertools import product, combinations

sys.path.insert(0, '<repo>/notes/scripts')
from fri_2round_attack import (
    setup_chain, even_odd_parts, parity_check, matvec, dist_to_code_full,
    gauss_rank, modinv
)


def true_fold_R(f, chain, alphas, p):
    R = len(alphas)
    L_chain = [chain[i][0] for i in range(R + 1)]
    fold = list(f)
    for r in range(R):
        f_e, f_o = even_odd_parts(fold, L_chain[r], p)
        a = alphas[r]
        fold = [(f_e[j] + a * f_o[j]) % p for j in range(len(f_e))]
    return fold


def evaluate_dft(fhat, L0, p):
    n = len(fhat)
    return [sum(fhat[i] * pow(L0[j], i, p) for i in range(n)) % p for j in range(n)]


def min_wt_via_MDS(target, H, n_R, p, max_w):
    """Find min-wt e with H · e = target. Uses MDS structure: enumerate w-subsets,
    solve linear system. Returns (min_w, min_T, min_e) or (None, None, None)."""
    if all(x == 0 for x in target):
        return 0, [], [0]*n_R
    H_cols = list(zip(*H))  # H_cols[j] = column j
    syn_dim = len(target)
    for w in range(1, max_w + 1):
        for T in combinations(range(n_R), w):
            # Solve H_T · x = target for x ∈ F_p^w
            A = [[H_cols[j][i] for j in T] for i in range(syn_dim)]
            # Build augmented [A | target]
            aug = [list(A[i]) + [target[i]] for i in range(syn_dim)]
            ncols = w + 1
            pivot_col = {}
            rank = 0
            col = 0
            while rank < syn_dim and col < w:
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
                for rr in range(syn_dim):
                    if rr != rank and aug[rr][col] != 0:
                        ff = aug[rr][col]
                        aug[rr] = [(aug[rr][c] - ff * aug[rank][c]) % p for c in range(ncols)]
                pivot_col[col] = rank
                rank += 1
                col += 1
            # consistency
            consistent = True
            for r in range(rank, syn_dim):
                if aug[r][w] % p != 0:
                    consistent = False; break
            if not consistent:
                continue
            x = [0]*w
            for c, r in pivot_col.items():
                x[c] = aug[r][w] % p
            # Verify all entries nonzero (so wt = w exactly)
            if all(xi != 0 for xi in x):
                e = [0]*n_R
                for idx, j in enumerate(T):
                    e[j] = x[idx]
                return w, list(T), e
    return None, None, None


def extract_mu_tildepsi(f, chain, R, p, H_R, n_R, m):
    """For rank-1 image f: extract μ_b coefficients of ψ(α) = Σ_b α^b μ_b
    by interpolation over (R+1)^R distinct α-points, then return:
       (mu_dict, S_size, v0)
    where mu_dict[b_tuple] = μ_b ∈ F_p, S_size = #nonzero μ_b, v0 = canonical syndrome.
    """
    # Sample (q^R) syndromes; identify the line F_p · v_0
    image_set = []
    for alphas in product(range(p), repeat=R):
        g = true_fold_R(f, chain, list(alphas), p)
        syn = matvec(H_R, g, p)
        image_set.append((alphas, syn))
    # Find any nonzero syndrome
    v0 = None
    for _, syn in image_set:
        if any(x != 0 for x in syn):
            v0 = syn
            break
    if v0 is None:
        return None, 0, None
    # Normalize: find first nonzero entry of v0, inv it
    for x in v0:
        if x != 0:
            inv0 = modinv(x, p)
            break
    v0_n = [(y * inv0) % p for y in v0]
    # Now ψ(α) = (first nonzero coordinate of syndrome) * inv0 (gives scalar in F_p)
    # Actually: H_R · g_α = ψ(α) · v_0, so ψ(α) = (any nonzero coord of syn) / (corresp coord of v_0).
    # Find a coord c such that v_0[c] != 0
    c_idx = None
    for i, x in enumerate(v0):
        if x != 0:
            c_idx = i
            break
    inv_v0c = modinv(v0[c_idx], p)
    psi_table = {}
    for alphas, syn in image_set:
        psi_alpha = (syn[c_idx] * inv_v0c) % p
        psi_table[alphas] = psi_alpha
    # Interpolate ψ as multilinear poly: ψ(α) = Σ_{b ∈ {0,1,...,2^R-1}} α^b μ_b ?
    # No — multilinear means ψ(α_1,...,α_R) = Σ_{S ⊂ [R]} c_S Π_{r ∈ S} α_r
    # Coefficients indexed by b ∈ {0,1}^R.
    # But the FRI fold uses α^b = Π_r α_r^{b_r}, so binary multilinear.
    # We need to recover μ_b for b ∈ {0,1}^R.
    mu = {}
    for b in product([0,1], repeat=R):
        # Möbius-like inversion: μ_b = Σ_{α ∈ {0,1}^R, α_r = 1 only if b_r = 1} (-1)^{|b| - |α|} ψ(α)
        # Standard: ψ(α) = Σ_b α^b μ_b ⟹ μ_b = Σ_α (-1)^{|b|-|α|} ψ(α) where α ranges over {0,1}^R with α ≤ b coordinatewise.
        s = 0
        for a in product([0,1], repeat=R):
            if all(a[r] <= b[r] for r in range(R)):
                sign = (-1) ** (sum(b) - sum(a))
                s = (s + sign * psi_table[tuple(a)]) % p
        mu[b] = s % p
    S_size = sum(1 for v in mu.values() if v != 0)
    # Verify: ψ(α) at random α matches Σ_b α^b μ_b
    return mu, S_size, v0_n


def tildepsi_eval(mu, x, R, p):
    """Evaluate $\\tildeψ(x) = Σ_b x^b · μ_b$ where b ∈ {0,1}^R, b interpreted as int."""
    s = 0
    for b, m_b in mu.items():
        b_int = sum(b[r] * (1 << r) for r in range(R))  # binary -> integer in [0, 2^R)
        s = (s + m_b * pow(x, b_int, p)) % p
    return s


def main():
    p = int(sys.argv[1]); n0 = int(sys.argv[2]); k0 = int(sys.argv[3])
    R = int(sys.argv[4])
    n_trials = int(sys.argv[5]) if len(sys.argv) > 5 else 100

    chain = setup_chain(p, n0, k0, R=R)
    L0, _, H0 = chain[0]
    L_R, k_R, _ = chain[R]
    n_R = len(L_R)
    H_R = parity_check(L_R, n_R, k_R, p)
    rho0 = k0 / n0
    w_J = int((1 - math.sqrt(rho0)) * n0)
    m = n_R - k_R
    bound_naive = math.ceil(w_J / (2**R)) + 1  # naive lower bound on w'

    print(f"# Setup: p={p}, n_0={n0}, k_0={k0}, R={R}")
    print(f"# n_R={n_R}, k_R={k_R}, m={m}, w_J={w_J}")
    print(f"# Naive lower bound w' >= {bound_naive} (= ceil(w_J/2^R) + 1)")
    print(f"# Path γ closes if w' > w_R; for our test we explore w_R up to m-1")
    print()

    rng = random.Random(2026)
    n_above = 0
    rank1_data = []

    for trial in range(n_trials):
        sparsity = rng.choice([2, 3, 4, 5, 6])
        positions = rng.sample(range(k0, n0), sparsity)
        fhat = [0]*n0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f = evaluate_dft(fhat, L0, p)
        d0, _ = dist_to_code_full(f, H0, n0, k0, p, max_w=w_J)
        if d0 is not None and d0 <= w_J:
            continue
        n_above += 1

        # Image rank
        image_set = set()
        for alphas in product(range(p), repeat=R):
            g = true_fold_R(f, chain, list(alphas), p)
            syn = tuple(matvec(H_R, g, p))
            image_set.add(syn)
        nonzero = [list(s) for s in image_set if any(x != 0 for x in s)]
        r = gauss_rank(nonzero, p) if nonzero else 0

        if r != 1:
            continue

        mu, S_size, v0_n = extract_mu_tildepsi(f, chain, R, p, H_R, n_R, m)
        if mu is None:
            continue
        # min-wt of e via MDS
        w_prime, T, e = min_wt_via_MDS(v0_n, H_R, n_R, p, max_w=m)
        if w_prime is None:
            continue
        # Compute Z = zeros of tildepsi in cosets(y) for y ∈ T
        Z = 0
        zeros_per_y = []
        # Map y ∈ L_R → coset in L_0
        # L_0[j] for j ∈ [0, n0). L_R is L_0 squared R times.
        # coset(L_R[j]) = {L_0[i] : L_0[i]^{2^R} = L_R[j]} = {L_0[j + r*n_R] : r ∈ [0, 2^R)}
        # because L_0[i]^{2^R} = ω^{i * 2^R} = ω_R^{i mod n_R}
        for j in T:
            y = L_R[j]
            # find x's in L_0 with x^{2^R} = y
            coset_xs = [L0[j + r*n_R] for r in range(2**R)]
            zs = sum(1 for x in coset_xs if tildepsi_eval(mu, x, R, p) == 0)
            zeros_per_y.append(zs)
            Z += zs

        # Theoretical upper bound: dist <= 2^R * w' - Z
        bound = (2**R) * w_prime - Z
        # Compute actual dist with higher cap (for verification)
        if d0 is None:
            actual_dist, _ = dist_to_code_full(f, H0, n0, k0, p, max_w=min(2**R * m, n0))
        else:
            actual_dist = d0
        matches = (actual_dist == bound) if actual_dist is not None else None
        rank1_data.append({
            'positions': sorted(positions),
            'd0': d0, 'actual_dist': actual_dist, 'w_prime': w_prime, 'S_size': S_size, 'Z': Z,
            'bound_2Rwp_minus_Z': bound, 'matches': matches,
            'v0_n': v0_n, 'T': T, 'mu': mu, 'zeros_per_y': zeros_per_y,
        })

        if trial % 10 == 0:
            print(f"  trial {trial}: {n_above} above-J, {len(rank1_data)} rank-1", flush=True)

    print()
    print(f"# === Rank-1 cases: ({len(rank1_data)} found) ===")
    print(f"# {'positions':<22s} {'dist':>4s} {'w*':>3s} {'|S|':>4s} {'Z':>3s} {'bound':>6s} {'match':>6s}")
    print("-" * 60)
    matches_all = True
    for d in rank1_data:
        if d['matches'] is None:
            match_str = "?"
        elif d['matches']:
            match_str = "YES"
        else:
            match_str = "NO"; matches_all = False
        ad = d['actual_dist']
        ad_str = f"{ad}" if ad is not None else f">{w_J}"
        print(f"  sparse_{str(d['positions']):<15s} {ad_str:>4s} {d['w_prime']:>3d} {d['S_size']:>4d} {d['Z']:>3d} {d['bound_2Rwp_minus_Z']:>6d} {match_str:>6s}")

    print()
    if rank1_data:
        wps = [d['w_prime'] for d in rank1_data]
        zs = [d['Z'] for d in rank1_data]
        ss = [d['S_size'] for d in rank1_data]
        print(f"# w' distribution: min={min(wps)}, max={max(wps)}, m={m}")
        print(f"# Z distribution: min={min(zs)}, max={max(zs)}")
        print(f"# |S| distribution: min={min(ss)}, max={max(ss)}, max possible={2**R}")
        print(f"# Formula dist = 2^R w' - Z holds for ALL: {matches_all}")
        # Test the key claim: above-J ⟹ w' > w_J/2^R
        violations = sum(1 for d in rank1_data if d['w_prime'] <= w_J // (2**R))
        print(f"# Violations of w' > w_J/2^R: {violations}/{len(rank1_data)}")


if __name__ == '__main__':
    main()
