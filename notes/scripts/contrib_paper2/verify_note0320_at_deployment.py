"""Verify Note 0320 theorem at deployment-scale (32, 8) p=257.

Theorem: For RS(n, k) with n even, k ≤ n/4, the s-pos sparse pencil with
supp = {n/2, n/2+1, ..., n/2+s-1} has, for every α ∈ F_q^*, a codeword
within Hamming distance ≤ n/2 = J. Mechanism: ω^{n/2} = -1 forces
e[j] = h_α[j] - cw[j] = 0 on all even j (n/2 positions).

Verification: pick (32, 8) p=257, supp = {16, 17, 18, 19}, compute
candidate codeword msg = c_1 + α c_2, check Hamming dist h_α to cw.
"""
from __future__ import annotations


def primitive_root_of_unity(p, n):
    if (p - 1) % n != 0:
        return None
    for g in range(2, p):
        if pow(g, n, p) == 1:
            ok = True
            for q in range(2, n + 1):
                if n % q == 0 and pow(g, n // q, p) == 1:
                    ok = False
                    break
            if ok:
                return g
    return None


def encode_rs(p, omega, n, k, msg):
    cw = []
    for j in range(n):
        v = 0
        x = pow(omega, j, p)
        xp = 1
        for m in msg:
            v = (v + m * xp) % p
            xp = (xp * x) % p
        cw.append(v)
    return cw


def main():
    cases = [
        (97, 16, 4, 3),    # supp = {8, 9, 10}
        (257, 32, 8, 3),   # supp = {16, 17, 18}
        (257, 32, 8, 4),   # supp = {16, 17, 18, 19}
        (257, 32, 8, 8),   # supp = {16, 17, ..., 23} — full k-pos
    ]
    for p, n, k, s in cases:
        omega = primitive_root_of_unity(p, n)
        if omega is None:
            continue
        J = n - int((n * k) ** 0.5)
        supp = list(range(n // 2, n // 2 + s))
        c1 = list(range(1, s + 1))
        c2 = [(2 * i + 1) for i in range(s)]
        print(f"\n=== p={p}, ({n},{k}), s={s}, supp={supp}, J={J} ===")
        print(f"   c_1={c1}, c_2={c2}")

        # Build h_α and candidate cw_α; check Hamming distance.
        max_dist = 0
        K_count = 0
        for alpha in range(1, p):
            # h_α
            h = [0] * n
            for a, c1a, c2a in zip(supp, c1, c2):
                coef = (c1a + alpha * c2a) % p
                for j in range(n):
                    h[j] = (h[j] + coef * pow(omega, a * j, p)) % p
            # candidate cw with msg = c_1 + α c_2 in first s positions
            msg = [(c1[i] + alpha * c2[i]) % p for i in range(s)] + [0] * (k - s)
            cw = encode_rs(p, omega, n, k, msg)
            dist = sum(1 for x, y in zip(h, cw) if x != y)
            max_dist = max(max_dist, dist)
            if dist <= J:
                K_count += 1

        print(f"   max Hamming distance over α=1..{p-1}: {max_dist}")
        print(f"   K (count α with dist ≤ J={J}): {K_count} (expect q-1={p-1})")
        print(f"   ✓ saturated" if K_count == p - 1 else f"   not saturated")


if __name__ == '__main__':
    main()
