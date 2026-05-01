"""optimize_p_avg.py — direct attack on issue #344.

Question: is the (1-δ/2)^q FRI upper bound tight, i.e., does there exist a cheater
above Johnson achieving per-α pass-prob → 1-δ/2 = 0.75 on average?

Search space: (T_1, T_2, ε_1, ε_2, c, msg) for the dense K≥2 construction
(probe_K2_construct.construct_f_with_psi_in_U), plus comparison modes:
  - random above-J (sample_far_input)
  - CS-lift modes (cs_lift_input)
  - codeword-shifted CS-lifts
  - monomials

For each f, compute P_avg via Strategy B (cheat-at-last) full F_p² grid, ~40s/f.

Strategy: random-restart hill-climb. Keep top-K. Every K_restart restarts try a
different mode. Print running max + best f's metadata.

Usage:
  python3 optimize_p_avg.py [n_iter=200] [seed=2026]
"""
from __future__ import annotations
import sys, os, random, time, math
from itertools import product, combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fri_2round_attack import (
    setup_chain, parity_check, matvec, gauss_rank,
    even_odd_parts, dist_to_code_full, cs_lift_input, sample_far_input,
)
from probe_step5_n32_studio import (
    P, N0, K0, R, N_R, W_J, evaluate_dft,
)
from mds_decoder import is_above_johnson_sampling, dist_lower_bound_sampling
from probe_K2_construct import construct_f_with_psi_in_U


W_R = 3
M = N_R - 2


def fast_P_avg(f, chain, p):
    """Strategy B (cheat-at-last) P_avg over full F_p² grid. ~40s at our params."""
    L0, _, _ = chain[0]
    L1, _, _ = chain[1]
    L2, k2, H2 = chain[2]
    n1, n2 = len(L1), len(L2)
    f_e, f_o = even_odd_parts(f, L0, p)
    total_d2 = 0
    n_pairs = 0
    d2_dist = {}
    for a1 in range(p):
        fold1 = [(f_e[j] + a1 * f_o[j]) % p for j in range(n1)]
        g_e, g_o = even_odd_parts(fold1, L1, p)
        for a2 in range(p):
            fold2 = [(g_e[j] + a2 * g_o[j]) % p for j in range(n2)]
            d2, _ = dist_to_code_full(fold2, H2, n2, k2, p)
            if d2 is None:
                d2 = n2
            total_d2 += d2
            n_pairs += 1
            d2_dist[d2] = d2_dist.get(d2, 0) + 1
    P_avg = 1.0 - (total_d2 / n_pairs) / n2
    return P_avg, d2_dist


def construct_K2_f(rng, p, n_R, w_R, H_R, msg=None, c=None, eps1=None, eps2=None,
                   T1=None, T2=None, max_overlap=1):
    """One random K=2 construction. Returns (f, meta) or (None, None) if rank fails."""
    if T1 is None:
        T1 = tuple(sorted(rng.sample(range(n_R), w_R)))
    if T2 is None:
        # overlap ≤ 1
        overlap = rng.randint(0, max_overlap)
        if overlap == 0:
            available = [j for j in range(n_R) if j not in T1]
            if len(available) < w_R:
                return None, None
            T2 = tuple(sorted(rng.sample(available, w_R)))
        else:
            shared = rng.sample(list(T1), overlap)
            others_pool = [j for j in range(n_R) if j not in T1]
            others = rng.sample(others_pool, w_R - overlap)
            T2 = tuple(sorted(list(shared) + others))
    if T1 == T2:
        return None, None
    if eps1 is None:
        eps1 = [0] * n_R
        for j in T1:
            eps1[j] = rng.randrange(1, p)
    if eps2 is None:
        eps2 = [0] * n_R
        for j in T2:
            eps2[j] = rng.randrange(1, p)
    u1 = matvec(H_R, eps1, p)
    u2 = matvec(H_R, eps2, p)
    if gauss_rank([u1, u2], p) != 2:
        return None, None
    if c is None:
        c = {b: (rng.randrange(p), rng.randrange(p)) for b in product([0, 1], repeat=R)}
    if msg is None:
        msg = [rng.randrange(p) for _ in range(K0)]
    fhat = construct_f_with_psi_in_U(u1, u2, c, msg, p)
    return fhat, {'T1': T1, 'T2': T2, 'eps1': eps1, 'eps2': eps2, 'c': c, 'msg': msg, 'u1': u1, 'u2': u2}


def main():
    n_iter = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026

    n0, k0, p = N0, K0, P
    delta = W_J / n0  # 0.5

    print("=" * 72)
    print(f"P_AVG OPTIMIZER  (issue #344: is (1-δ/2)^q tight for FRI?)")
    print(f"  Params: n_0={n0}, k_0={k0}, p={p}, R={R}, w_J={W_J}, δ={delta:.4f}")
    print(f"  Targets:")
    print(f"    P_avg ≥ 1-δ/2 = {1-delta/2:.4f}  → BCIKS bound TIGHT, settles #344 'yes'")
    print(f"    P_avg ≥ 1-δ   = {1-delta:.4f}  → improvement over random possible")
    print(f"    P_avg < 1-δ stuck → coupling theorem target for c < 2")
    print(f"  Search budget: {n_iter} P_avg evaluations (≈ {n_iter*40/60:.0f}min)")
    print("=" * 72, flush=True)

    chain = setup_chain(p, n0, k0, R=R)
    L0 = chain[0][0]
    L_R, k_R, _ = chain[R]
    H_R = parity_check(L_R, N_R, k_R, p)
    H0 = chain[0][2]

    rng = random.Random(seed)
    best = {'P_avg': -1.0, 'f': None, 'meta': None}
    history = []

    # Mode rotation: random sparse, K=2 dense, CS-style, K=3 (3 disjoint), random codeword shift
    modes = ['K2_dense', 'sparse_random', 'cs_lift', 'cs_shifted', 'K3_dense', 'monomial_pair']
    omega = L0[1] if len(L0) > 1 else None

    t_start = time.time()
    for it in range(n_iter):
        mode = modes[it % len(modes)]
        f = None
        meta = {'mode': mode, 'iter': it}

        if mode == 'K2_dense':
            for attempt in range(20):
                fhat, m = construct_K2_f(rng, p, N_R, W_R, H_R)
                if fhat is None:
                    continue
                f = evaluate_dft(fhat, L0, p)
                if dist_lower_bound_sampling(f, L0, k0, p, n_samples=20000, batch=4096, seed=seed+it) > W_J:
                    meta.update(m)
                    break
                f = None

        elif mode == 'sparse_random':
            for attempt in range(20):
                w_target = W_J + rng.randint(1, 4)  # above-J weight target
                f, _ = sample_far_input(p, n0, k0, w_target, rng, chain, verify=False)
                d_lb = dist_lower_bound_sampling(f, L0, k0, p, n_samples=20000, batch=4096, seed=seed+it)
                if d_lb > W_J:
                    meta['w_target'] = w_target
                    meta['d_lb'] = d_lb
                    break
                f = None

        elif mode == 'cs_lift':
            cs_modes = ['l1', 'l1_only_e', 'l0_X9', 'l1_alt']
            cs_mode = cs_modes[it % len(cs_modes)]
            f = cs_lift_input(p, n0, omega, cs_mode)
            d_lb = dist_lower_bound_sampling(f, L0, k0, p, n_samples=20000, batch=4096, seed=seed+it)
            if d_lb <= W_J:
                f = None
            else:
                meta['cs_mode'] = cs_mode
                meta['d_lb'] = d_lb

        elif mode == 'cs_shifted':
            cs_modes = ['l1', 'l1_only_e', 'l0_X9']
            cs_mode = rng.choice(cs_modes)
            f_cs = cs_lift_input(p, n0, omega, cs_mode)
            coeffs = [rng.randrange(p) for _ in range(k0)]
            shift = [sum(coeffs[i] * pow(L0[j], i, p) for i in range(k0)) % p for j in range(n0)]
            f = [(f_cs[j] + shift[j]) % p for j in range(n0)]
            d_lb = dist_lower_bound_sampling(f, L0, k0, p, n_samples=20000, batch=4096, seed=seed+it)
            if d_lb <= W_J:
                f = None
            else:
                meta['cs_mode'] = cs_mode
                meta['d_lb'] = d_lb

        elif mode == 'K3_dense':
            # 3 disjoint T's of size w_R = 3 — needs n_R ≥ 9, we have n_R = 8 ⇒ skip
            continue

        elif mode == 'monomial_pair':
            # X^a + b X^c for a, c ∈ [k_0, n_0)
            a = rng.randint(k0, n0 - 1)
            c_deg = rng.randint(k0, n0 - 1)
            if a == c_deg:
                continue
            b_idx = rng.randrange(n0)
            b = pow(omega, b_idx, p)
            f = [(pow(x, a, p) + b * pow(x, c_deg, p)) % p for x in L0]
            d_lb = dist_lower_bound_sampling(f, L0, k0, p, n_samples=20000, batch=4096, seed=seed+it)
            if d_lb <= W_J:
                f = None
            else:
                meta['a'] = a
                meta['b_idx'] = b_idx
                meta['c_deg'] = c_deg
                meta['d_lb'] = d_lb

        if f is None:
            continue

        t_eval = time.time()
        P_avg, d2_dist = fast_P_avg(f, chain, p)
        eval_time = time.time() - t_eval
        record = {**meta, 'P_avg': P_avg, 'd2_dist': dict(d2_dist), 'time': eval_time}
        history.append(record)

        is_best = P_avg > best['P_avg']
        if is_best:
            best['P_avg'] = P_avg
            best['f'] = list(f)
            best['meta'] = meta

        elapsed = time.time() - t_start
        marker = " ★ NEW BEST" if is_best else ""
        print(f"[it {it:>4}/{n_iter} mode={mode:<14}] P_avg = {P_avg:.4f} | best = {best['P_avg']:.4f} | "
              f"thresh: 1-δ/2={1-delta/2:.3f} | {eval_time:.0f}s | total {elapsed/60:.1f}min{marker}",
              flush=True)

    # Final report
    print()
    print("=" * 72)
    print(f"FINAL ({len(history)} successful evals)")
    print("=" * 72)
    print(f"  Best P_avg = {best['P_avg']:.4f}  (mode: {best['meta'].get('mode')})")
    print(f"  Compare:  1-δ/2 = {1-delta/2:.4f}  |  1-δ = {1-delta:.4f}")
    print()

    # Per-mode statistics
    by_mode = {}
    for r in history:
        m = r['mode']
        by_mode.setdefault(m, []).append(r['P_avg'])
    print(f"{'mode':<16} {'count':>6} {'max P_avg':>10} {'mean P_avg':>11}")
    print('-' * 50)
    for m in sorted(by_mode):
        ps = by_mode[m]
        print(f"{m:<16} {len(ps):>6d} {max(ps):>10.4f} {sum(ps)/len(ps):>11.4f}")

    # Ground truth: K=2 known breach (from audit) at P_avg ≈ 0.39
    print()
    print(f"  Reference: 0114 K=2 breaches achieve P_avg ≈ 0.39 (from audit_K2_breach_acceptance)")
    print(f"  Random above-J for comparison: typical P_avg ≈ 1 - (n-k_R)/n = {1-(N_R-2)/N_R:.4f}")


if __name__ == '__main__':
    main()
