"""
EXACT computation of the character-sum error term R_w for list decoding.

N_w = C(n,w)(p-1)^w / p^{n-k} + R_w

Compute R_w exactly and check |R_w| < 1.

Key identity: R_w = (1/p^{n-k}) * sum_{xi != 0} psi(-<xi,c>) * S_w(|Z(xi)|)

where S_w(z) = (-1)^w * sum_j C(z,j)*C(n-z,w-j)*(1-p)^j
and Z(xi) = {i : q_xi(omega^{-i}) = 0}, q_xi = sum xi_r X^r.

Since S_w depends only on |Z|: group by z.

R_w = (1/p^{n-k}) * sum_z S_w(z) * Phi(z,c)
where Phi(z,c) = sum_{xi: |Z(xi)|=z} psi(-<xi,c>)

Phi(z,c) = "twisted weight enumerator of dual code at weight n-z"
"""
import cmath, math
from itertools import product as iter_product

def find_prim_root(p, n):
    assert (p-1) % n == 0
    for g in range(2, p):
        w = pow(g, (p-1)//n, p)
        if pow(w, n, p) == 1:
            ok = True; tmp = n; d = 2
            while d*d <= tmp:
                while tmp % d == 0:
                    if pow(w, n//d, p) == 1: ok = False
                    tmp //= d
                d += 1
            if tmp > 1 and pow(w, n//tmp, p) == 1: ok = False
            if ok: return w
    return None

def psi(a, p):
    """Additive character psi(a) = exp(2*pi*i*a/p)."""
    return cmath.exp(2j * cmath.pi * (a % p) / p)

def compute_Rw(n, k, p, w_vals, w_target):
    """Compute R_w exactly for weight w_target."""
    omega = find_prim_root(p, n)
    L = [pow(omega, i, p) for i in range(n)]
    omega_inv = pow(omega, p-2, p)

    # Compute syndrome c_r = sum_i w(omega^i) * omega^{-(r+k)*i} for r=0,...,n-k-1
    syndromes = []
    for r in range(n - k):
        s = 0
        for i in range(n):
            s = (s + w_vals[i] * pow(omega_inv, (r+k)*i, p)) % p
        syndromes.append(s)

    # For each xi in F_p^{n-k} \ {0}:
    #   q_xi(X) = sum_r xi_r X^r (degree < n-k)
    #   Z(xi) = {i : q_xi(omega^{-i}) = 0}
    #   <xi, c> = sum_r xi_r * c_r
    #   Contribution: psi(-<xi,c>) * S_w(|Z(xi)|)

    # Precompute S_w(z) for z = 0, ..., n-k-1
    S_w = []
    for z in range(n):
        val = 0
        for j in range(min(w_target, z) + 1):
            val += math.comb(z, j) * math.comb(n-z, w_target-j) * (1-p)**j
        val *= (-1)**w_target
        S_w.append(val)

    # Main term
    main = math.comb(n, w_target) * (p-1)**w_target / p**(n-k)

    # Group by z: compute Phi(z, c) = sum_{xi: |Z(xi)|=z} psi(-<xi,c>)
    # For small n-k: enumerate all xi
    dim = n - k
    if p**dim > 500000:
        print(f"  p^(n-k) = {p}^{dim} too large, skipping")
        return None, main

    R_total = 0j  # complex accumulator

    # Count by z
    z_counts = [0] * n
    z_phi = [0j] * n  # Phi(z, c) as complex

    for xi_tuple in iter_product(range(p), repeat=dim):
        if all(x == 0 for x in xi_tuple):
            continue  # skip zero

        # Compute Z(xi): positions i where q_xi(omega^{-i}) = 0
        z = 0
        for i in range(n):
            val = 0
            omi = pow(omega_inv, i, p)  # omega^{-i}
            power = 1
            for r in range(dim):
                val = (val + xi_tuple[r] * power) % p
                power = power * omi % p
            if val == 0:
                z += 1

        # Compute <xi, c>
        inner = 0
        for r in range(dim):
            inner = (inner + xi_tuple[r] * syndromes[r]) % p

        # Phase
        phase = psi(-inner, p)

        z_counts[z] += 1
        z_phi[z] += phase

    # Compute R_w
    R = 0j
    for z in range(n):
        if z_counts[z] > 0:
            R += S_w[z] * z_phi[z]
    R /= p**(n-k)

    return R, main

def test(n, k, p, delta):
    omega = find_prim_root(p, n)
    if omega is None:
        print(f"n={n}, k={k}, p={p}: no primitive root")
        return

    import random
    random.seed(42)

    print(f"\nn={n}, k={k}, p={p}, delta={delta:.2f}, n-k={n-k}")
    print(f"Johnson={1-math.sqrt(k/n):.3f}, intermediate={'YES' if delta > 1-math.sqrt(k/n) else 'no'}")

    w_max = int(delta * n)
    L = [pow(omega, i, p) for i in range(n)]

    # Random word
    w_vals = [random.randint(0, p-1) for _ in range(n)]

    print(f"Testing weight w = {w_max}:")
    R, main = compute_Rw(n, k, p, w_vals, w_max)
    if R is not None:
        print(f"  Main term = {main:.6f}")
        print(f"  R_w = {R.real:.6f} + {R.imag:.6f}i")
        print(f"  |R_w| = {abs(R):.6f}")
        print(f"  |R_w| < 1? {'YES ✓' if abs(R) < 1 else 'NO ✗'}")
        print(f"  N_w = main + R = {main + R.real:.6f}")
        print(f"  (should be non-negative integer: {round(main + R.real)})")

    # Test multiple words
    print(f"\nTesting 10 random words, weight {w_max}:")
    violations = 0
    for trial in range(10):
        w_vals = [random.randint(0, p-1) for _ in range(n)]
        R, main = compute_Rw(n, k, p, w_vals, w_max)
        if R is not None:
            Nw = round(main + R.real)
            if abs(R) >= 1:
                violations += 1
                print(f"  word {trial}: |R|={abs(R):.4f} ✗, N_w={Nw}")
            else:
                print(f"  word {trial}: |R|={abs(R):.4f} ✓, N_w={Nw}")

    if violations == 0:
        print(f"  ALL |R_w| < 1 ✓")
    else:
        print(f"  {violations}/10 violations")

# Small cases where exact computation is feasible
# n=8, k=4, p=17, delta=0.35 (above Johnson 0.293)
test(8, 4, 17, 0.35)

# n=8, k=4, p=41, delta=0.35
test(8, 4, 41, 0.35)

# n=6, k=3, p=7, delta=0.4 (above Johnson 0.293)
test(6, 3, 7, 0.4)

# n=6, k=3, p=13, delta=0.4
test(6, 3, 13, 0.4)

# n=6, k=3, p=31, delta=0.4
test(6, 3, 31, 0.4)

# Rate 1/4: n=8, k=2, p=17, delta=0.55 (above Johnson 0.5)
test(8, 2, 17, 0.55)
