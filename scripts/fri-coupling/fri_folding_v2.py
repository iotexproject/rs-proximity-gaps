"""
FRI Folding List Size Reduction — v2 (fast)

Focus on small n (8, 10, 12) with optimized enumeration.
For each center with M > 0, analyze error pairing and folding survival.
"""

import math
import random
from collections import defaultdict


def find_primitive_root(p):
    for g in range(2, p):
        seen = set()
        x = 1
        for _ in range(p - 1):
            seen.add(x)
            x = (x * g) % p
        if len(seen) == p - 1:
            return g


def find_params(n):
    p = n + 1
    while True:
        if p % n == 1:
            is_prime = all(p % i != 0 for i in range(2, int(p**0.5) + 1))
            if is_prime:
                g = find_primitive_root(p)
                omega = pow(g, (p - 1) // n, p)
                return p, omega
        p += n


def eval_poly(coeffs, x, p):
    v = 0
    xi = 1
    for c in coeffs:
        v = (v + c * xi) % p
        xi = (xi * x) % p
    return v


def rs_encode(coeffs, powers, p):
    """Evaluate polynomial at precomputed powers."""
    return [eval_poly(coeffs, x, p) for x in powers]


def fold_vals(vals, omega, n, p, alpha):
    """FRI fold values from L to L'."""
    n2 = n // 2
    inv2 = pow(2, p - 2, p)
    g = []
    for i in range(n2):
        fi = vals[i]
        fi2 = vals[i + n2]
        f_even = (fi + fi2) * inv2 % p
        omega_i = pow(omega, i, p)
        inv_oi = pow(omega_i, p - 2, p)
        f_odd = (fi - fi2) * inv2 % p * inv_oi % p
        g.append((f_even + alpha * f_odd) % p)
    return g


def fold_coeffs(coeffs, k, p, alpha):
    """Fold polynomial coefficients."""
    k2 = k // 2
    new = []
    for j in range(k2):
        ce = coeffs[2*j] if 2*j < len(coeffs) else 0
        co = coeffs[2*j+1] if 2*j+1 < len(coeffs) else 0
        new.append((ce + alpha * co) % p)
    return new


def hamming(a, b, p):
    return sum(1 for x, y in zip(a, b) if (x - y) % p != 0)


def error_pairing(error_set, n):
    """Return (paired_count, unpaired_count)."""
    n2 = n // 2
    paired = sum(1 for i in error_set if (i + n2) % n in error_set) // 2
    unpaired = len(error_set) - 2 * paired
    return paired, unpaired


def main():
    print("=== FRI Folding List Size Reduction v2 ===\n")

    cases = [
        (8, 4),
        (10, 5),
        (12, 6),
    ]

    for n, k in cases:
        p, omega = find_params(n)
        w = int(math.floor((1 - math.sqrt(k / n)) * n))
        if w < 1:
            w = 1
        n2 = n // 2
        k2 = k // 2
        w2 = int(math.floor((1 - math.sqrt(k2 / n2)) * n2))
        if w2 < 1:
            w2 = 1

        print(f"--- n={n}, k={k}, p={p}, w={w}, n'={n2}, k'={k2}, w'={w2} ---")

        # Precompute powers
        powers = [pow(omega, i, p) for i in range(n)]
        powers2 = [pow(omega, 2*i, p) for i in range(n2)]
        omega2 = pow(omega, 2, p)

        # Total codewords
        total_search = p**k
        print(f"  Search space: {total_search} codewords")
        if total_search > 10_000_000:
            print(f"  TOO LARGE, skipping full search. Using sampling.\n")
            # For n=12: sample random centers and use targeted search
            random.seed(42)
            max_M = 0
            n_trials = 100

            for trial in range(n_trials):
                center = [random.randrange(p) for _ in range(n)]
                M = 0
                close_cws = []

                # Random sample codewords
                for _ in range(50000):
                    coeffs = [random.randrange(p) for _ in range(k)]
                    vals = rs_encode(coeffs, powers, p)
                    d = hamming(vals, center, p)
                    if d <= w:
                        M += 1
                        close_cws.append((coeffs, vals, d))

                if M > max_M:
                    max_M = M
                    best = (center, close_cws)

            # For n=12, use exhaustive search on best center
            center, _ = best
            close_cws = []
            import itertools
            count = 0
            for coeffs_tuple in itertools.product(range(p), repeat=k):
                coeffs = list(coeffs_tuple)
                vals = rs_encode(coeffs, powers, p)
                d = hamming(vals, center, p)
                if d <= w:
                    close_cws.append((coeffs, vals, d))
                count += 1
                if count % 1000000 == 0:
                    print(f"    ... {count}/{total_search}", flush=True)

            max_M = len(close_cws)
            best = (center, close_cws)
            print(f"  Exhaustive on one center: M={max_M}")

            # Analyze
            center, cws = best
            if max_M > 0:
                analyze_folding(n, k, p, omega, omega2, w, w2, n2, k2,
                                center, cws, powers, powers2)
            print()
            continue

        # Exhaustive search for best center
        import itertools
        random.seed(42)
        n_centers = min(500, p**(n-k))
        max_M = 0

        for trial in range(n_centers):
            center = [random.randrange(p) for _ in range(n)]
            cws = []
            for coeffs_tuple in itertools.product(range(p), repeat=k):
                coeffs = list(coeffs_tuple)
                vals = rs_encode(coeffs, powers, p)
                d = hamming(vals, center, p)
                if d <= w:
                    cws.append((coeffs, vals, d))
            if len(cws) > max_M:
                max_M = len(cws)
                best = (center, cws)

        print(f"  Max M = {max_M} (over {n_centers} centers)")

        if max_M == 0:
            print("  No codewords found.\n")
            continue

        center, cws = best

        analyze_folding(n, k, p, omega, omega2, w, w2, n2, k2,
                        center, cws, powers, powers2)
        print()


def analyze_folding(n, k, p, omega, omega2, w, w2, n2, k2,
                    center, cws, powers, powers2):
    """Analyze folding survival for a list of close codewords."""

    print(f"\n  Error pairing analysis (M={len(cws)}):")
    for idx, (coeffs, vals, d) in enumerate(cws):
        eset = {i for i in range(n) if (vals[i] - center[i]) % p != 0}
        pr, unpr = error_pairing(eset, n)
        print(f"    cw {idx}: d={d}, error_set={sorted(eset)}, "
              f"paired={pr}, unpaired={unpr}")

    # Fold with multiple alpha values
    print(f"\n  Folding survival (20 random alpha values):")
    random.seed(999)

    alpha_survive = defaultdict(int)  # cw_idx -> count of alphas where it survives

    for alpha_trial in range(20):
        alpha = random.randrange(1, p)
        g_center = fold_vals(center, omega, n, p, alpha)

        survivors = []
        for idx, (coeffs, vals, d) in enumerate(cws):
            fc = fold_coeffs(coeffs, k, p, alpha)
            fv = rs_encode(fc, powers2, p)
            d_fold = hamming(fv, g_center, p)
            if d_fold <= w2:
                survivors.append(idx)
                alpha_survive[idx] += 1

        if alpha_trial < 5:
            print(f"    alpha={alpha}: {len(survivors)} survive "
                  f"(indices: {survivors})")

    print(f"\n  Per-codeword survival rate (over 20 alphas):")
    for idx, (coeffs, vals, d) in enumerate(cws):
        eset = {i for i in range(n) if (vals[i] - center[i]) % p != 0}
        pr, unpr = error_pairing(eset, n)
        rate = alpha_survive.get(idx, 0)
        print(f"    cw {idx}: d={d}, paired={pr}, unpaired={unpr}, "
              f"survive={rate}/20 ({rate*5}%)")

    # Multi-round folding for best alpha
    print(f"\n  Multi-round folding chain:")
    alpha = random.randrange(1, p)

    cur_center = center
    cur_cws = cws
    cur_n, cur_k, cur_w = n, k, w
    cur_omega = omega

    rnd = 0
    while cur_n >= 4 and cur_k >= 2 and len(cur_cws) > 0:
        cur_w_calc = int(math.floor((1 - math.sqrt(cur_k / cur_n)) * cur_n))
        if cur_w_calc < 1:
            cur_w_calc = 1

        print(f"    Round {rnd}: n={cur_n}, k={cur_k}, w={cur_w_calc}, M={len(cur_cws)}")

        # Fold
        new_n = cur_n // 2
        new_k = cur_k // 2
        if new_k < 1:
            break
        new_w = int(math.floor((1 - math.sqrt(new_k / new_n)) * new_n))
        if new_w < 1:
            new_w = 1

        alpha = random.randrange(1, p)
        new_center = fold_vals(cur_center, cur_omega, cur_n, p, alpha)
        new_omega = pow(cur_omega, 2, p)
        new_powers = [pow(new_omega, i, p) for i in range(new_n)]

        new_cws = []
        for coeffs, vals, d in cur_cws:
            fc = fold_coeffs(coeffs, cur_k, p, alpha)
            fv = rs_encode(fc, new_powers, p)
            d_new = hamming(fv, new_center, p)
            if d_new <= new_w:
                new_cws.append((fc, fv, d_new))

        print(f"      -> n'={new_n}, k'={new_k}, w'={new_w}, "
              f"M'={len(new_cws)} (alpha={alpha})")

        cur_center = new_center
        cur_cws = new_cws
        cur_n = new_n
        cur_k = new_k
        cur_omega = new_omega
        rnd += 1

    # Also: iterate folding many times with different alphas to see distribution
    print(f"\n  Folding reduction statistics (100 independent alpha choices):")
    random.seed(777)

    survive_counts = []
    for _ in range(100):
        alpha = random.randrange(1, p)
        g_c = fold_vals(center, omega, n, p, alpha)

        surv = 0
        for coeffs, vals, d in cws:
            fc = fold_coeffs(coeffs, k, p, alpha)
            fv = rs_encode(fc, powers2, p)
            d_fold = hamming(fv, g_c, p)
            if d_fold <= w2:
                surv += 1
        survive_counts.append(surv)

    from collections import Counter
    dist = Counter(survive_counts)
    print(f"    Original M = {len(cws)}")
    print(f"    Folded M' distribution: {dict(sorted(dist.items()))}")
    print(f"    Mean M' = {sum(survive_counts)/len(survive_counts):.2f}")
    print(f"    Max M' = {max(survive_counts)}")


if __name__ == "__main__":
    main()
