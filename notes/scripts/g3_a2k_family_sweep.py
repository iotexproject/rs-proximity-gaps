"""g3_a2k_family_sweep.py — empirically map B for (a, 2k) family at toy.

For n=8, k=2, deployment scale toy:
- (a, b) = (1, 4), (2, 4), (3, 4), (5, 4) [b=4 == 2k]
  Wait: a < b strictly so (1,4), (2,4), (3,4) only.
- For each, brute force ρ ∈ F_q^* and check whether dist(h_ρ, RS_2(L_8)) ≤ 4 (Johnson radius).

We want to verify: is the (k, 2k) result of Note 0219 special to a=k, or
does it extend to all (a, 2k)?
"""
import itertools


def find_primitive_root(q, n):
    """Find ω ∈ F_q^* with order exactly n."""
    for g in range(2, q):
        if pow(g, n, q) == 1 and all(pow(g, n // p, q) != 1 for p in [2, 3, 5, 7] if n % p == 0):
            return g
    return None


def dist_to_RS(values, k, q):
    """Distance from `values` (list on L) to RS_k(L) over F_q.
    Brute force: enumerate degree-< k polynomials and find min distance.
    """
    n = len(values)
    L = list(range(n))
    min_dist = n
    # Enumerate coefficient tuples
    for coefs in itertools.product(range(q), repeat=k):
        # Polynomial p(x) = sum coefs[i] * x^i
        # We need to evaluate at L_n elements; but here values is indexed by L position.
        # For a generic check we need the actual L points.
        # This brute is too slow; use syndrome approach instead.
        pass
    return min_dist


def bad_rho_via_syndrome(a, b, n, k, q, omega):
    """Compute B = {ρ : dist(h_ρ, RS_k(L_n)) ≤ J} where J = n/2.

    h_ρ(z) = ρ z^a + z^b evaluated at L_n = {ω^i : i ∈ [0, n)}.

    A vector v on L_n is at distance ≤ J from RS_k iff there's a codeword c
    with |support(v - c)| ≤ J. By Reed-Solomon-Berlekamp dual:
    iff projection of v onto syndrome space [k, n-1] has support count ≤ J.

    Wait, that's not quite right. Distance ≤ J means there's a length-J support
    where v restricted to complement is a codeword. Use direct enumeration:
    """
    # Generate L_n points
    L_pts = [pow(omega, i, q) for i in range(n)]
    bad_rhos = []
    for rho in range(1, q):
        h_vals = [(rho * pow(z, a, q) + pow(z, b, q)) % q for z in L_pts]
        # Find min distance to RS_k(L_n) by enumerating codewords?
        # Better: dist ≤ J iff ∃ size-J subset S such that h_vals|_(L_n\S) interpolates
        # to a degree-< k polynomial. Equivalently: ∃ S of size J such that for
        # the (n - J) = n/2 = 2k complement, the values come from a poly of deg < k.
        #
        # For (n, k) = (8, 2), J = 4. Need to check 8C4 = 70 subsets? Plus interpolation.
        from itertools import combinations
        found = False
        J = n // 2
        for S in combinations(range(n), J):
            S_set = set(S)
            # Check if h_vals on L_n \ S agrees with some degree-< k poly
            comp = [(L_pts[i], h_vals[i]) for i in range(n) if i not in S_set]
            # Interpolate any k points to determine candidate poly
            if len(comp) < k:
                continue
            # Use the first k points to determine poly via Lagrange
            x_pts = [comp[j][0] for j in range(k)]
            y_pts = [comp[j][1] for j in range(k)]
            # Compute polynomial coefficients via Lagrange
            # Then check remaining points

            # Lagrange interpolation in F_q
            def evaluate_lagrange(x_query):
                result = 0
                for j in range(k):
                    num = y_pts[j]
                    den = 1
                    for i in range(k):
                        if i != j:
                            num = (num * (x_query - x_pts[i])) % q
                            den = (den * (x_pts[j] - x_pts[i])) % q
                    inv_den = pow(den, q - 2, q)
                    result = (result + num * inv_den) % q
                return result

            # Check all complement points match
            ok = True
            for j in range(k, len(comp)):
                if evaluate_lagrange(comp[j][0]) != comp[j][1]:
                    ok = False
                    break
            if ok:
                found = True
                break
        if found:
            bad_rhos.append(rho)
    return bad_rhos


def main():
    n = 8
    k = 2
    # Need q such that n | q-1 (primitive n-th root exists)
    # q = 17 works (16 = 2*8)
    q = 17
    omega = find_primitive_root(q, n)
    if omega is None:
        print(f"No primitive {n}-th root in F_{q}")
        return
    print(f"q={q}, ω={omega}, ω^{n}={pow(omega, n, q)}")

    print(f"\n=== (a, 2k) family at (n={n}, k={k}, q={q}) ===")
    print(f"Bad-ratio set B = {{ρ : dist(h_ρ, RS_k(L_n)) ≤ {n//2}}}")

    for a in range(1, 2 * k):
        b = 2 * k
        if a >= b:
            continue
        B = bad_rho_via_syndrome(a, b, n, k, q, omega)
        print(f"  (a, b) = ({a}, {b}): |B| = {len(B)}, B = {B}")

    print(f"\n=== sign-paired family (b - a = n/2 = {n//2}) ===")
    for a in range(1, n // 2):
        b = a + n // 2
        if b >= n:
            continue
        B = bad_rho_via_syndrome(a, b, n, k, q, omega)
        print(f"  (a, b) = ({a}, {b}): |B| = {len(B)}, B = {B}")

    print(f"\n=== other (a, b) pairs (sample) ===")
    for a in range(1, n - 1):
        for b in range(a + 1, n):
            if b == 2 * k or b - a == n // 2:
                continue  # already done
            if (a + b) % n == 0:
                continue  # trivial (sum to 0)
            B = bad_rho_via_syndrome(a, b, n, k, q, omega)
            print(f"  (a, b) = ({a}, {b}): |B| = {len(B)}, B = {B}")


if __name__ == "__main__":
    main()
