"""g3_predict_max_count.py — Conjecture D's predicted max bad-α count per q.

Under Conjecture D, |B(f)| divides q-1. Combined with the (single-line)
combinatorial bound |B(f)| ≤ M_aff(f) · (n_1 - s + 1), the max is at most:

  max_count_q = max{d : d | (q-1) AND d ≤ M_aff_max · (n_1 - s + 1)}

where M_aff_max is the empirical or conjectured max affine-cover number.

For our sweep at (n_0,k_0)=(32,8), n_1=16, k_1=4, s=8:
  - n_1 - s + 1 = 9  (single-line cap)
  - empirical M_aff_max so far = 4 (count=8 case)

So predicted max_count_q = max{d | (q-1) : d ≤ 4 · 9 = 36}.

Let's compute for our sweep primes.
"""

def divisors(n):
    out = []
    for i in range(1, n + 1):
        if n % i == 0: out.append(i)
    return sorted(out)


def max_div_below(n, cap):
    return max(d for d in divisors(n) if d <= cap)


def main():
    primes = [97, 193, 449, 769, 1153, 2113]
    n1, k1 = 16, 4
    s = 8
    nsplus1 = n1 - s + 1  # 9
    M_aff_caps = [1, 2, 4, 9]  # try several conjectured values

    print(f"Conjecture D predictions for (n_0,k_0)=(32,8), n_1={n1}, k_1={k1}, s={s}:")
    print(f"Single-line cap = n_1 - s + 1 = {nsplus1}\n")

    for p in primes:
        d = divisors(p - 1)
        print(f"q={p:5d}: q-1={p-1:5d}, divisors = {d}")
        for M in M_aff_caps:
            cap = M * nsplus1
            mx = max_div_below(p - 1, cap)
            print(f"   M_aff_max={M:2d}: predicted max |B| ≤ {mx:4d} (cap = {cap})")
        # Tightest empirical from sweep so far: count=8 at q=97 had M_aff=4
        print()

    print("=== Comparison with combinatorial-only (no Conjecture D) ===")
    for p in primes:
        for M in M_aff_caps:
            cap = M * nsplus1
            print(f"   q={p}, M_aff={M}: combinatorial bound |B| ≤ {cap}")
        print()


if __name__ == "__main__":
    main()
