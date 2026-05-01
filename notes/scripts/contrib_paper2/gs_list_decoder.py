"""GS / Wu list decoder for plain Reed-Solomon over multiplicative subgroup.

Implements:
  1. Finite field GF(p) operations (modular arithmetic).
  2. RS encoder/decoder for plain RS(n, k) over evaluation domain L = ⟨ω⟩.
  3. Berlekamp-Welch unique decoder (up to (d-1)/2 errors).
  4. Roth-Ruckenstein GS list decoder (up to Johnson bound n - sqrt(n*k)).

Target use: empirical validation of conj:sparse-worst at deployment scale
(32, 8). For each candidate (f_1, f_2) ∈ F_q^L × F_q^L, compute
  K(f_1, f_2) := #{ α ∈ F_q^* : ∃ c ∈ RS(n, k) with d_H(f_1 + α·f_2, c) ≤ J }
where J is the Johnson radius. Compare K_dense vs K_sparse to test
conj:sparse-worst empirically at (32, 8) and (deployment fields KoalaBear,
BabyBear, Goldilocks at smaller proxies).

Status: scaffold — BW unique decoder first (low-hanging), GS to follow.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Finite field: GF(p) for prime p
# ---------------------------------------------------------------------------

class GF:
    """GF(p) for prime p. Integers mod p. p must be prime; not validated."""

    __slots__ = ('p',)

    def __init__(self, p: int):
        self.p = p

    def add(self, a, b):
        return (a + b) % self.p

    def sub(self, a, b):
        return (a - b) % self.p

    def mul(self, a, b):
        return (a * b) % self.p

    def neg(self, a):
        return (-a) % self.p

    def inv(self, a):
        if a % self.p == 0:
            raise ZeroDivisionError("GF(p) inverse of 0")
        return pow(a, self.p - 2, self.p)

    def div(self, a, b):
        return self.mul(a, self.inv(b))

    def pow(self, a, k):
        return pow(a, k, self.p)

    def primitive_root_of_unity(self, n):
        """Find primitive n-th root of unity in GF(p). Requires n | (p-1)."""
        if (self.p - 1) % n != 0:
            return None
        for g in range(2, self.p):
            if pow(g, n, self.p) == 1:
                # Check it's primitive (no smaller order)
                primitive = True
                for q in range(2, n + 1):
                    if n % q == 0 and pow(g, n // q, self.p) == 1:
                        primitive = False
                        break
                if primitive:
                    return g
        return None


# ---------------------------------------------------------------------------
# Polynomials over GF(p)
# ---------------------------------------------------------------------------

class Poly:
    """Univariate polynomial over GF(p), stored as coefficient list (low-deg first)."""

    __slots__ = ('coeffs', 'gf')

    def __init__(self, coeffs, gf: GF):
        self.gf = gf
        # Strip trailing zeros
        c = [x % gf.p for x in coeffs]
        while len(c) > 1 and c[-1] == 0:
            c.pop()
        self.coeffs = c

    @property
    def degree(self):
        if len(self.coeffs) == 1 and self.coeffs[0] == 0:
            return -1
        return len(self.coeffs) - 1

    def __repr__(self):
        return f"Poly({self.coeffs}, GF({self.gf.p}))"

    def __call__(self, x):
        # Horner
        r = 0
        for c in reversed(self.coeffs):
            r = (r * x + c) % self.gf.p
        return r

    def __add__(self, other):
        n = max(len(self.coeffs), len(other.coeffs))
        c = [0] * n
        for i, x in enumerate(self.coeffs):
            c[i] = (c[i] + x) % self.gf.p
        for i, x in enumerate(other.coeffs):
            c[i] = (c[i] + x) % self.gf.p
        return Poly(c, self.gf)

    def __sub__(self, other):
        n = max(len(self.coeffs), len(other.coeffs))
        c = [0] * n
        for i, x in enumerate(self.coeffs):
            c[i] = (c[i] + x) % self.gf.p
        for i, x in enumerate(other.coeffs):
            c[i] = (c[i] - x) % self.gf.p
        return Poly(c, self.gf)

    def __mul__(self, other):
        if isinstance(other, int):
            return Poly([(c * other) % self.gf.p for c in self.coeffs], self.gf)
        c = [0] * (len(self.coeffs) + len(other.coeffs) - 1)
        for i, a in enumerate(self.coeffs):
            for j, b in enumerate(other.coeffs):
                c[i + j] = (c[i + j] + a * b) % self.gf.p
        return Poly(c, self.gf)

    def divmod_(self, other):
        """Polynomial division: self = q * other + r."""
        if other.degree < 0:
            raise ZeroDivisionError("poly div by zero")
        q = Poly([0], self.gf)
        r = Poly(list(self.coeffs), self.gf)
        d = other.degree
        c = other.coeffs[d]
        c_inv = self.gf.inv(c)
        while r.degree >= d:
            shift = r.degree - d
            t = (r.coeffs[r.degree] * c_inv) % self.gf.p
            # q += t * x^shift
            q_coeffs = list(q.coeffs)
            while len(q_coeffs) <= shift:
                q_coeffs.append(0)
            q_coeffs[shift] = (q_coeffs[shift] + t) % self.gf.p
            q = Poly(q_coeffs, self.gf)
            # r -= t * x^shift * other
            sub = [0] * (shift + d + 1)
            for j, b in enumerate(other.coeffs):
                sub[shift + j] = (t * b) % self.gf.p
            r = r - Poly(sub, self.gf)
        return q, r

    def gcd(self, other):
        a, b = self, other
        while b.degree >= 0:
            _, r = a.divmod_(b)
            a, b = b, r
        return a


# ---------------------------------------------------------------------------
# RS encoder for plain RS(n, k) over multiplicative subgroup L = ⟨ω⟩
# ---------------------------------------------------------------------------

@dataclass
class RSCode:
    p: int          # field char
    n: int          # code length
    k: int          # message length
    omega: int      # primitive n-th root of unity

    @classmethod
    def make(cls, p: int, n: int, k: int):
        gf = GF(p)
        omega = gf.primitive_root_of_unity(n)
        if omega is None:
            raise ValueError(f"No primitive {n}-th root in GF({p})")
        return cls(p, n, k, omega)

    @property
    def gf(self):
        return GF(self.p)

    def domain(self):
        """L = {1, ω, ω², ..., ω^{n-1}}."""
        gf = self.gf
        x = 1
        L = []
        for _ in range(self.n):
            L.append(x)
            x = gf.mul(x, self.omega)
        return L

    def encode(self, message):
        """Encode message ∈ GF(p)^k as RS codeword (n evaluations of m(X))."""
        if len(message) != self.k:
            raise ValueError("message length != k")
        gf = self.gf
        f = Poly(message, gf)
        return [f(x) for x in self.domain()]


# ---------------------------------------------------------------------------
# Berlekamp-Welch unique decoder
# ---------------------------------------------------------------------------

def berlekamp_welch_decode(code: RSCode, received):
    """Decode `received` ∈ GF(p)^n to a codeword within (n-k)/2 errors.

    Returns (message_poly_coeffs, error_locator_zeros) on success, None if no
    codeword exists within the unique-decoding radius.

    Method: solve linear system for E(X), Q(X) such that
      Q(x_i) = r_i · E(x_i)  for all i
    with deg E ≤ t, deg Q ≤ k + t - 1, where t = ⌊(n-k)/2⌋.
    """
    gf = code.gf
    p = code.p
    n, k = code.n, code.k
    t = (n - k) // 2
    L = code.domain()

    # Unknowns: E_0, ..., E_t (t+1 vars), Q_0, ..., Q_{k+t-1} (k+t vars)
    # Total (k + 2t + 1) = (n + 1) unknowns. Constraint: E monic (E_t = 1) — t+k vars.
    # Equations: n constraints (one per i).
    # Solve linear system: Q(x_i) - r_i * E(x_i) = 0 for i=0..n-1.

    # Variables: [Q_0, Q_1, ..., Q_{k+t-1}, E_0, E_1, ..., E_{t-1}]  (E_t = 1 fixed)
    # Number of vars: (k+t) + t = k + 2t
    # Setup matrix M of shape (n, k+2t), RHS vector b of shape (n,)
    nvars = k + 2 * t
    M = [[0] * nvars for _ in range(n)]
    b = [0] * n
    for i in range(n):
        x_i = L[i]
        r_i = received[i]
        # Q(x_i) part: Q_j contributes Q_j * x_i^j  (j = 0 .. k+t-1)
        x_pow = 1
        for j in range(k + t):
            M[i][j] = x_pow
            x_pow = gf.mul(x_pow, x_i)
        # -r_i * E(x_i) part: E_j contributes -r_i * x_i^j  (j = 0 .. t-1, E_t = 1 fixed)
        x_pow = 1
        for j in range(t):
            M[i][k + t + j] = (-r_i * x_pow) % p
            x_pow = gf.mul(x_pow, x_i)
        # E_t = 1 contributes -r_i * x_i^t to RHS
        # i.e., move to RHS: Q(x_i) + (sum E_j ...) = r_i * x_i^t
        b[i] = (r_i * x_pow) % p

    # Solve M @ vars = b mod p (Gaussian elimination)
    sol = solve_linear_mod(M, b, p)
    if sol is None:
        return None

    Q_coeffs = sol[:k + t]
    E_coeffs = sol[k + t:] + [1]  # E_t = 1
    Q = Poly(Q_coeffs, gf)
    E = Poly(E_coeffs, gf)
    # f = Q / E
    f, rem = Q.divmod_(E)
    if rem.degree >= 0:
        return None  # Q not divisible by E
    if f.degree >= k:
        return None
    msg = f.coeffs + [0] * (k - len(f.coeffs))
    return msg


def solve_linear_mod(M, b, p):
    """Solve M @ x = b mod p. M is list of rows (lists). Returns list or None."""
    rows = len(M)
    cols = len(M[0]) if rows else 0
    A = [list(row) + [bv] for row, bv in zip(M, b)]
    r = 0
    pivot_col = []
    for c in range(cols):
        if r >= rows:
            break
        piv = None
        for i in range(r, rows):
            if A[i][c] % p != 0:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv = pow(A[r][c], p - 2, p)
        A[r] = [(x * inv) % p for x in A[r]]
        for i in range(rows):
            if i != r and A[i][c] % p != 0:
                factor = A[i][c]
                A[i] = [(A[i][j] - factor * A[r][j]) % p for j in range(cols + 1)]
        pivot_col.append(c)
        r += 1
    # Check rest of rows for inconsistency
    for i in range(r, rows):
        if A[i][cols] % p != 0:
            return None
    # Back-substitute: free variables set to 0
    sol = [0] * cols
    for ridx, c in enumerate(pivot_col):
        sol[c] = A[ridx][cols] % p
    return sol


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test():
    print("Self-test: BW unique decoder over GF(17), RS(16, 4)")
    code = RSCode.make(p=17, n=16, k=4)
    msg = [1, 2, 3, 4]
    cw = code.encode(msg)
    print(f"  message {msg}")
    print(f"  codeword {cw}")
    # Introduce t = (n-k)/2 = 6 errors at random positions
    import random
    rng = random.Random(42)
    err_positions = rng.sample(range(16), 6)
    rcvd = list(cw)
    for pos in err_positions:
        rcvd[pos] = (rcvd[pos] + rng.randint(1, 16)) % 17
    print(f"  received (with 6 errors at {err_positions}): {rcvd}")
    decoded = berlekamp_welch_decode(code, rcvd)
    print(f"  decoded message: {decoded}")
    if decoded == msg:
        print("  ✓ BW decoder PASSED")
    else:
        print(f"  ✗ BW decoder FAILED (expected {msg}, got {decoded})")


if __name__ == "__main__":
    self_test()
