"""K(f_1, f_2) sweep for empirical sparse-worst test.

Definition:
  K(f_1, f_2; δ) := #{ α ∈ F_q^* : ∃ codeword c ∈ RS(n, k)
                                    with d_H(f_1 + α·f_2, c) ≤ δ }

For base (8, 2) with q small (q=17), we use direct enumeration: iterate over
all q^k = 289 messages and compute Hamming distance. Practical at base, not
at deployment.

For deployment (32, 8), need GS list-decoder (next iter).

Goal: validate Note 0313 numbers — 3-mono sparse K=10 algebraic, 4-mono K=12
algebraic — by counting α at small q. Algebraic K is q-INDEPENDENT (deg of
eliminator Φ over Q-bar); empirical K_q ≤ K_alg with equality for large q.
"""
from __future__ import annotations

import itertools

from gs_list_decoder import GF, Poly, RSCode


def hamming(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


_codeword_cache = {}


def get_all_codewords(code: RSCode):
    """Cache the q^k codeword set per (p, n, k)."""
    key = (code.p, code.n, code.k)
    if key in _codeword_cache:
        return _codeword_cache[key]
    p, n, k = code.p, code.n, code.k
    L = code.domain()
    gf = code.gf
    cws = []
    for msg in itertools.product(range(p), repeat=k):
        f = Poly(list(msg), gf)
        cws.append(tuple(f(x) for x in L))
    _codeword_cache[key] = cws
    return cws


def K_via_enumeration(code: RSCode, f1, f2, delta):
    """Count α ∈ F_q^* such that f_1 + α·f_2 has a codeword within distance δ.

    Direct enumeration over all q^k messages. O(q · q^k · n) — only feasible
    at small (n, k, q). Uses cached codeword set.
    """
    p, n, k = code.p, code.n, code.k
    all_codewords = get_all_codewords(code)
    count = 0
    matched_alphas = []
    for alpha in range(1, p):
        h = tuple((f1[i] + alpha * f2[i]) % p for i in range(n))
        for cw in all_codewords:
            if hamming(h, cw) <= delta:
                count += 1
                matched_alphas.append(alpha)
                break
    return count, matched_alphas


def make_sparse_pencil(code: RSCode, supp1, supp2, coeff_choice='unit'):
    """Build (f_1, f_2) where f_i is supported on monomial positions supp_i.

    "Sparse f̂" interpretation: in paper2 framing, f̂ := h has restricted
    monomial support (positions = degrees in F̄ basis of L = ⟨ω⟩). Here we
    encode by treating f_i ∈ F_q^L as evaluation values directly.

    But for Note 0313 sparse-worst, "s-pos sparse" usually means the inverse
    DFT of f has supp ⊆ given positions. So we set:
      f_i[j] := sum_{a ∈ supp_i} c_a · ω^{a*j}    j = 0, ..., n-1
    where c_a are nonzero coefficients (we use 1, 2, 3, ... default).
    """
    p, n = code.p, code.n
    omega = code.omega
    gf = code.gf

    def evaluate(supp, coeffs):
        return [sum(c * pow(omega, a * j, p) for a, c in zip(supp, coeffs)) % p
                for j in range(n)]

    if coeff_choice == 'unit':
        c1 = list(range(1, len(supp1) + 1))
        c2 = list(range(1, len(supp2) + 1))
    else:
        c1, c2 = coeff_choice
    f1 = evaluate(supp1, c1)
    f2 = evaluate(supp2, c2)
    return f1, f2


def test_at_base(p, supp1, supp2, label, n=8, k=2):
    """Run K-sweep at base (n, k) for given prime and supports."""
    print("=" * 64)
    print(f"Base (n={n}, k={k}) at p={p} — {label}")
    print("=" * 64)
    code = RSCode.make(p=p, n=n, k=k)
    f1, f2 = make_sparse_pencil(code, supp1, supp2)
    # Johnson radius J = n - sqrt(n*k); at (8, 2) → 4. Above-J: δ ≥ 4.
    # Berlekamp threshold T_c (c=2 base): T_2 = ⌊(2D-1)/c⌋ = ⌊11/2⌋ = 5.
    for delta in [3, 4, 5]:
        count, alphas = K_via_enumeration(code, f1, f2, delta)
        print(f"  δ ≤ {delta}: K = {count}")
        if count <= 20:
            print(f"    matched α: {alphas}")


def test_battery():
    """Battery test: 3-mono and 4-mono at multiple primes for base (8, 2)."""
    primes = [17, 97, 193]
    print("\n--- 3-MONO ---")
    for p in primes:
        test_at_base(p, [2, 3, 4], [5, 6, 7], f"3-mono [2,3,4] vs [5,6,7]")
    print("\n--- 4-MONO ---")
    for p in primes:
        test_at_base(p, [2, 3, 4, 5], [4, 5, 6, 7], f"4-mono [2,3,4,5] vs [4,5,6,7]")


def systematic_s_sweep(p, n=8, k=2, deltas=(3, 4, 5), n_random=12):
    """For each s ∈ {2, 3, 4, 5} (above-J supports ⊆ [k, n-1]),
    compute MAX Hamming-K over n_random random support choices and coeff
    choices. Returns max-K table.

    For dense baseline: f_1, f_2 random over full [0, n-1].
    """
    import random
    rng = random.Random(123)
    code = RSCode.make(p=p, n=n, k=k)
    above_J_positions = list(range(k, n))  # [2, 3, 4, 5, 6, 7] at (8, 2)

    print(f"\n=== Systematic s-sweep at p={p}, base ({n}, {k}) ===")
    print(f"  above-J position pool: {above_J_positions}")

    results = {}  # results[(label, delta)] = (max_K, {('supp1', 'supp2'): K})

    for s in [2, 3, 4]:  # 5-mono needs |above_J| ≥ 5 — at (8,2), only 6 above-J pos
        if s > len(above_J_positions):
            continue
        max_K = {d: 0 for d in deltas}
        details = {d: None for d in deltas}
        for trial in range(n_random):
            supp1 = rng.sample(above_J_positions, s)
            supp2 = rng.sample(above_J_positions, s)
            coeffs1 = [rng.randint(1, p - 1) for _ in supp1]
            coeffs2 = [rng.randint(1, p - 1) for _ in supp2]
            f1, f2 = make_sparse_pencil(code, supp1, supp2,
                                         coeff_choice=(coeffs1, coeffs2))
            for delta in deltas:
                K, _ = K_via_enumeration(code, f1, f2, delta)
                if K > max_K[delta]:
                    max_K[delta] = K
                    details[delta] = (supp1, supp2, coeffs1, coeffs2)
        results[f's={s}'] = (max_K, details)
        print(f"\n  s={s} sparse (above-J only):")
        for d in deltas:
            if details[d] is not None:
                print(f"    δ ≤ {d}:  max K = {max_K[d]} (supp {details[d][0]} × {details[d][1]})")
            else:
                print(f"    δ ≤ {d}:  max K = {max_K[d]}")

    # 5-mono requires expanding to all 6 positions; check if achievable
    if 5 <= len(above_J_positions):
        max_K_5 = {d: 0 for d in deltas}
        for trial in range(n_random):
            supp1 = rng.sample(above_J_positions, 5)
            supp2 = rng.sample(above_J_positions, 5)
            coeffs1 = [rng.randint(1, p - 1) for _ in supp1]
            coeffs2 = [rng.randint(1, p - 1) for _ in supp2]
            f1, f2 = make_sparse_pencil(code, supp1, supp2,
                                         coeff_choice=(coeffs1, coeffs2))
            for delta in deltas:
                K, _ = K_via_enumeration(code, f1, f2, delta)
                if K > max_K_5[delta]:
                    max_K_5[delta] = K
        results['s=5'] = (max_K_5, None)
        print(f"\n  s=5 sparse (above-J only):")
        for d in deltas:
            print(f"    δ ≤ {d}:  max K = {max_K_5[d]}")

    # Dense baseline (random f_1, f_2 over full F_q^L)
    max_K_dense = {d: 0 for d in deltas}
    for trial in range(n_random):
        f1 = [rng.randint(0, p - 1) for _ in range(n)]
        f2 = [rng.randint(0, p - 1) for _ in range(n)]
        for delta in deltas:
            K, _ = K_via_enumeration(code, f1, f2, delta)
            if K > max_K_dense[delta]:
                max_K_dense[delta] = K
    results['dense'] = (max_K_dense, None)
    print(f"\n  DENSE (random f_1, f_2 over full L):")
    for d in deltas:
        print(f"    δ ≤ {d}:  max K = {max_K_dense[d]}")

    print("\n  Summary table (max K over n_random=" + str(n_random) + " trials):")
    print(f"    {'support':<10} | " + " | ".join(f'δ≤{d}' for d in deltas))
    print(f"    {'-'*10} | " + " | ".join('-' * 4 for _ in deltas))
    for label, (max_K, _) in results.items():
        row = "    " + f"{label:<10} | " + " | ".join(f'{max_K[d]:>4}' for d in deltas)
        print(row)


def exhaustive_support_sweep(p, n=8, k=2, deltas=(3, 4, 5),
                              n_coeff_trials=3, seed=42):
    """Exhaustive sweep over (supp1, supp2) ⊆ above-J positions.

    For each support pair, try n_coeff_trials random coefficient choices,
    record max K per (s_size_pair, delta).
    """
    import random
    rng = random.Random(seed)
    code = RSCode.make(p=p, n=n, k=k)
    above_J = list(range(k, n))  # at (8, 2): [2, 3, 4, 5, 6, 7]
    print(f"\n=== Exhaustive support sweep at p={p}, base ({n}, {k}) ===")
    print(f"  above-J pool: {above_J} (size {len(above_J)})")

    # max K per s-class, per delta
    max_K = {(s1, s2): {d: 0 for d in deltas}
             for s1 in range(2, len(above_J) + 1)
             for s2 in range(2, len(above_J) + 1)}
    best_witnesses = {(s1, s2): {d: None for d in deltas}
                      for s1, s2 in max_K.keys()}

    total_pairs = sum(1 for s1 in range(2, len(above_J) + 1)
                      for s2 in range(2, len(above_J) + 1)
                      for _ in itertools.combinations(above_J, s1)
                      for _ in itertools.combinations(above_J, s2))
    print(f"  total support pairs: {total_pairs}, × {n_coeff_trials} coeffs each")

    counter = 0
    for s1 in range(2, len(above_J) + 1):
        for s2 in range(2, len(above_J) + 1):
            for supp1 in itertools.combinations(above_J, s1):
                for supp2 in itertools.combinations(above_J, s2):
                    for trial in range(n_coeff_trials):
                        c1 = [rng.randint(1, p - 1) for _ in supp1]
                        c2 = [rng.randint(1, p - 1) for _ in supp2]
                        f1, f2 = make_sparse_pencil(code, list(supp1), list(supp2),
                                                     coeff_choice=(c1, c2))
                        for delta in deltas:
                            K, _ = K_via_enumeration(code, f1, f2, delta)
                            if K > max_K[(s1, s2)][delta]:
                                max_K[(s1, s2)][delta] = K
                                best_witnesses[(s1, s2)][delta] = (
                                    list(supp1), list(supp2), c1, c2)
                    counter += 1
                    if counter % 50 == 0:
                        print(f"    [progress] {counter}/{total_pairs} pairs")

    print(f"\n  === MAX K per (s1, s2) ===")
    print(f"    {'(s1,s2)':<8} | " + " | ".join(f'δ≤{d}' for d in deltas))
    for (s1, s2) in sorted(max_K.keys()):
        Ks = max_K[(s1, s2)]
        print(f"    {f'({s1},{s2})':<8} | " + " | ".join(f'{Ks[d]:>4}' for d in deltas))

    print(f"\n  === MAX K per joint support size |S*| ===")
    by_jointsize = {}
    for (s1, s2), Ks in max_K.items():
        for delta in deltas:
            wit = best_witnesses[(s1, s2)][delta]
            if wit is None:
                continue
            joint = len(set(wit[0]) | set(wit[1]))
            key = (joint, delta)
            if key not in by_jointsize or Ks[delta] > by_jointsize[key][0]:
                by_jointsize[key] = (Ks[delta], (s1, s2), wit)
    for delta in deltas:
        print(f"\n  δ ≤ {delta}:")
        for joint in range(2, len(above_J) + 1):
            entry = by_jointsize.get((joint, delta))
            if entry is None:
                continue
            K, (s1, s2), wit = entry
            print(f"    |S*|={joint}: max K = {K} (s1={s1}, s2={s2}, supp1={wit[0]}, supp2={wit[1]})")


def focused_sweep(p, n=8, k=2, delta_J=4, n_random_per_s=20, seed=42):
    """Focused max-K sweep at the Johnson-radius δ_J for s ∈ {2,3,4,5,6}.

    For each s, sample n_random_per_s random (supp1, supp2, coeff) configs.
    Track max-K observed.
    """
    import random
    rng = random.Random(seed)
    code = RSCode.make(p=p, n=n, k=k)
    above_J = list(range(k, n))
    print(f"\n=== Focused max-K sweep at p={p}, base ({n}, {k}), δ ≤ {delta_J} ===")

    rows = []
    for s in range(2, len(above_J) + 1):
        max_K = 0
        best = None
        for trial in range(n_random_per_s):
            supp1 = sorted(rng.sample(above_J, s))
            supp2 = sorted(rng.sample(above_J, s))
            c1 = [rng.randint(1, p - 1) for _ in supp1]
            c2 = [rng.randint(1, p - 1) for _ in supp2]
            f1, f2 = make_sparse_pencil(code, supp1, supp2, coeff_choice=(c1, c2))
            K, _ = K_via_enumeration(code, f1, f2, delta_J)
            if K > max_K:
                max_K = K
                best = (supp1, supp2, c1, c2)
        joint = len(set(best[0]) | set(best[1])) if best else None
        rows.append((s, max_K, joint, best))
        print(f"  s={s}:  max K = {max_K}  (|S*|={joint}, supp1={best[0]}, supp2={best[1]})")

    # Dense baseline
    max_K_dense = 0
    for trial in range(n_random_per_s):
        f1 = [rng.randint(0, p - 1) for _ in range(n)]
        f2 = [rng.randint(0, p - 1) for _ in range(n)]
        K, _ = K_via_enumeration(code, f1, f2, delta_J)
        if K > max_K_dense:
            max_K_dense = K
    print(f"  dense: max K = {max_K_dense}")

    print("\n  Pattern: K_2={}, K_3={}, K_4={}, K_5={}, K_6={}, dense={}".format(
        rows[0][1], rows[1][1] if len(rows)>1 else '-',
        rows[2][1] if len(rows)>2 else '-',
        rows[3][1] if len(rows)>3 else '-',
        rows[4][1] if len(rows)>4 else '-',
        max_K_dense))
    return rows, max_K_dense


if __name__ == "__main__":
    print("--- p=17 ---")
    focused_sweep(p=17, delta_J=4, n_random_per_s=30)
    print("\n--- p=97 ---")
    focused_sweep(p=97, delta_J=4, n_random_per_s=30)
