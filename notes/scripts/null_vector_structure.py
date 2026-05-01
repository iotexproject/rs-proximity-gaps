#!/usr/bin/env python3
"""
Analyze the polynomial structure of the null vector v.

v = eval(g) for g ∈ F_p[x], deg(g) < n.
The syndrome of v consists of coefficients g_k, ..., g_{n-1}.

For v to have M codewords at distance w: g must have specific structure.
Question: what is g? What pattern do g's follow?

Also: check ALL worst-case syndromes (not just one) to see if the pattern holds.
"""

from itertools import combinations
from collections import defaultdict


def find_primitive_root(p):
    factors = set()
    temp = p - 1
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            factors.add(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.add(temp)
    for g in range(2, p):
        if all(pow(g, (p - 1) // q, p) != 1 for q in factors):
            return g


def find_omega(n, p):
    g = find_primitive_root(p)
    return pow(g, (p - 1) // n, p)


def dft(v, omega, n, p):
    """Compute DFT: g_j = sum_i v_i * omega^{-ij} mod p."""
    omega_inv = pow(omega, p - 2, p)
    n_inv = pow(n, p - 2, p)
    g = [0] * n
    for j in range(n):
        s = 0
        for i in range(n):
            s = (s + v[i] * pow(omega_inv, i * j, p)) % p
        g[j] = s * n_inv % p  # normalize
    return g


def idft(g, omega, n, p):
    """Compute inverse DFT: v_i = sum_j g_j * omega^{ij}."""
    v = [0] * n
    for i in range(n):
        s = 0
        for j in range(n):
            s = (s + g[j] * pow(omega, i * j, p)) % p
        v[i] = s % p
    return v


def rank_mod_p(mat, p):
    if not mat or not mat[0]:
        return 0
    m = len(mat)
    nn = len(mat[0])
    M_mat = [row[:] for row in mat]
    for i in range(m):
        for j in range(nn):
            M_mat[i][j] %= p
    rank = 0
    for col in range(nn):
        pivot = -1
        for row in range(rank, m):
            if M_mat[row][col] % p != 0:
                pivot = row
                break
        if pivot == -1:
            continue
        M_mat[rank], M_mat[pivot] = M_mat[pivot], M_mat[rank]
        inv_pivot = pow(M_mat[rank][col], p - 2, p)
        for row in range(m):
            if row != rank and M_mat[row][col] % p != 0:
                factor = M_mat[row][col] * inv_pivot % p
                for j in range(nn):
                    M_mat[row][j] = (M_mat[row][j] - factor * M_mat[rank][j]) % p
        rank += 1
    return rank


def analyze_polynomial_structure(n, k, p, w):
    """Find ALL worst-case syndromes and analyze their polynomial structure."""
    omega = find_omega(n, p)
    L = [pow(omega, i, p) for i in range(n)]

    print(f"\n{'='*70}")
    print(f"n={n}, k={k}, p={p}, w={w}")
    print(f"ω = {omega}, L = {L}")

    # Parity check matrix
    H = [[pow(L[i], k + r, p) for i in range(n)] for r in range(n - k)]

    # Enumerate all error vectors with weight ≤ w and compute syndrome
    syndrome_count = defaultdict(int)

    for wt in range(1, w + 1):
        for positions in combinations(range(n), wt):
            def enum_nonzero(wt, p):
                if wt == 0:
                    yield ()
                    return
                for v in range(1, p):
                    for rest in enum_nonzero(wt - 1, p):
                        yield (v,) + rest
            for vals in enum_nonzero(wt, p):
                s = [0] * (n - k)
                for j, pos in enumerate(positions):
                    for r in range(n - k):
                        s[r] = (s[r] + vals[j] * H[r][pos]) % p
                syndrome_count[tuple(s)] += 1

    # Find max M syndromes
    max_M = max(syndrome_count.values())
    worst_syndromes = [s for s, m in syndrome_count.items() if m == max_M]

    print(f"  Max M = {max_M}, achieved by {len(worst_syndromes)} syndromes")

    # For each worst-case syndrome: find the polynomial g
    for idx, s in enumerate(worst_syndromes[:5]):  # show at most 5
        # The syndrome s = (g_k, g_{k+1}, ..., g_{n-1}) (up to normalization)
        # Actually: s[r] = sum_i c_i * L[i]^{k+r} = sum_i c_i * ω^{i(k+r)}
        # The DFT of c gives: ĉ[j] = (1/n) sum_i c_i * ω^{-ij}
        # And s[r] = sum_i c_i * ω^{i(k+r)} = n * ĉ[-(k+r)]  (unnormalized DFT at index -(k+r))
        # So ĉ[n-(k+r)] = s[r] / n.

        # But we don't know c, only its syndrome. Let me construct a canonical c:
        # c = (0, ..., 0, syndrome part, 0, ..., 0) such that Hc = s.
        # Or: the coset representative with c ∈ RS_k^⊥.

        # The canonical coset representative: c ∈ RS_k^⊥ with Hc = s.
        # RS_k^⊥ = {c : ĉ[0] = ... = ĉ[k-1] = 0}.
        # So the polynomial g of the canonical c has g_0 = ... = g_{k-1} = 0.
        # And g_k, ..., g_{n-1} are determined by s.

        # From s[r] = n * ĉ[n-(k+r)]:
        # Wait, let me redo. s = Hc where H[r][i] = L[i]^{k+r} = ω^{i(k+r)}.
        # s[r] = sum_i c_i ω^{i(k+r)} for r = 0, ..., n-k-1.

        # The DFT of c: ĉ[j] = (1/n) sum_i c_i ω^{-ij}. Unnormalized: Ĉ[j] = sum_i c_i ω^{-ij}.
        # So s[r] = sum_i c_i ω^{i(k+r)} = Ĉ[-(k+r)] = Ĉ[n-k-r].

        # So s[r] = Ĉ[n-k-r]. The syndrome gives Ĉ[n-k], Ĉ[n-k-1], ..., Ĉ[1].
        # (For r=0: Ĉ[n-k], for r=n-k-1: Ĉ[1].)

        # The canonical coset representative has Ĉ[0] = Ĉ[n-1] = ... = Ĉ[n-k+1] = 0.
        # Wait, which indices? For c ∈ RS_k^⊥: the DFT coefficients ĉ[0], ..., ĉ[k-1] are 0
        # (in the "polynomial coefficient" convention).
        # But wait, RS_k = {eval(f) : deg(f) < k}. The DFT of eval(f) = (f(L[0]),...,f(L[n-1]))
        # gives: Ĉ[j] = sum_i f(L[i]) ω^{-ij} = sum_i sum_l a_l L[i]^l ω^{-ij}
        # = sum_l a_l sum_i ω^{il} ω^{-ij} = sum_l a_l n δ_{l,j} = n a_j.
        # So Ĉ[j] = n*a_j for j = 0,...,k-1, and Ĉ[j] = 0 for j = k,...,n-1.
        # So RS_k = {c : Ĉ[j] = 0 for j ≥ k}.
        # And RS_k^⊥ = {c : Ĉ[j] = 0 for j < k}.

        # So for c ∈ RS_k^⊥: Ĉ[0] = ... = Ĉ[k-1] = 0.
        # And s[r] = Ĉ[n-k-r].
        # So Ĉ[n-k] = s[0], Ĉ[n-k-1] = s[1], ..., Ĉ[1] = s[n-k-1].
        # Also Ĉ[0] = 0.

        # Wait, for k ≤ n-k: the free indices are Ĉ[k], ..., Ĉ[n-1].
        # From syndrome: Ĉ[n-k-r] = s[r] for r=0,...,n-k-1.
        # This gives Ĉ[n-k], Ĉ[n-k-1], ..., Ĉ[1].
        # And Ĉ[0] = 0 (from RS_k^⊥ condition).
        # But what about Ĉ[n-1], Ĉ[n-2], ..., Ĉ[n-k]?
        # For r=0: Ĉ[n-k], for r=n-k-1: Ĉ[1].
        # So Ĉ[1], ..., Ĉ[n-k] are determined by s.
        # And Ĉ[0] = 0 (RS_k^⊥).
        # Missing: Ĉ[n-k+1], ..., Ĉ[n-1]. But wait, for c ∈ RS_k^⊥:
        # Ĉ[j] = 0 for j = 0,...,k-1. So Ĉ[n-1] is free if n-1 ≥ k, which it always is.
        # And Ĉ[j] = 0 for j < k.

        # Hmm, I'm confusing polynomial index and DFT index. Let me be careful.

        # Convention: c = (c_0, ..., c_{n-1}) where c_i = g(ω^i) for g(x) = sum_{j=0}^{n-1} g_j x^j.
        # Then g_j = (1/n) sum_i c_i ω^{-ij} (DFT).
        # RS_k = {c : g_j = 0 for j ≥ k}.
        # RS_k^⊥ = {c : g_j = 0 for j < k}.

        # Syndrome: s[r] = sum_i c_i L[i]^{k+r} = sum_i c_i ω^{i(k+r)}.
        # = n * g_{-(k+r) mod n} (by DFT inversion? No...)
        # Actually: sum_i c_i ω^{ij} = n * g_j (from DFT). Wait, check:
        # g_j = (1/n) sum_i c_i ω^{-ij}, so sum_i c_i ω^{-ij} = n g_j.
        # Thus sum_i c_i ω^{ij} = n g_{-j mod n} = n g_{n-j}.

        # So s[r] = sum_i c_i ω^{i(k+r)} = n * g_{n-(k+r)} = n * g_{n-k-r}.

        # For c ∈ RS_k^⊥: g_j = 0 for j < k. So g_k, g_{k+1}, ..., g_{n-1} are the free
        # coefficients. And s[r] = n * g_{n-k-r}.
        # So g_{n-k-r} = s[r] / n = s[r] * n^{-1} mod p.

        # For r=0: g_{n-k} = s[0]/n. For r=n-k-1: g_1 = s[n-k-1]/n.
        # So g_1, g_2, ..., g_{n-k} are determined by s (in reverse order).
        # And g_0 = 0, g_{n-k+1} = s[-1]??

        # Wait, r ranges from 0 to n-k-1. g_{n-k-r} for r=0,...,n-k-1 gives
        # g_{n-k}, g_{n-k-1}, ..., g_1. These are ALL the syndrome coefficients!
        # And g_0 = 0 (since 0 < k). And g_j = 0 for j < k... but g_1, ..., g_{k-1}
        # are determined by s! Contradiction with g_j = 0 for j < k.

        # Oh, I think I've been confused about RS_k^⊥. Let me reconsider.
        # RS_k is the code with evaluation polynomials of degree < k.
        # RS_k^⊥ (dual code) is generated by polynomials of degree k, k+1, ..., n-k-1?
        # Actually, the dual of RS[n,k] is RS[n, n-k] (for MDS codes).
        # So RS_k^⊥ = RS_{n-k} = {eval(h) : deg(h) < n-k}.

        # That means: c ∈ RS_k^⊥ iff c = eval(h) for h of degree < n-k.
        # In terms of DFT coefficients: g_j = 0 for j ≥ n-k.
        # So the FREE coefficients are g_0, ..., g_{n-k-1}.

        # And from s[r] = n * g_{n-k-r}: g_{n-k-r} = s[r]/n.
        # For r = 0: g_{n-k} = s[0]/n. But g_{n-k} should be 0 (since n-k ≥ n-k,
        # and we need g_j = 0 for j ≥ n-k). Wait, n-k is not in the range {0,...,n-k-1}.
        # So g_{n-k} = 0, which means s[0] = 0??

        # Hmm, that can't be right. For s = (3, 0, 5) (n=6): s[0] = 3 ≠ 0.

        # I think the confusion is about the dual code. Let me recompute.

        # RS[n,k] has generator matrix G[j][i] = L[i]^j for j=0,...,k-1.
        # The parity check matrix H has H[r][i] = L[i]^{k+r} for r=0,...,n-k-1.
        # H*G^T = 0 (orthogonality): sum_i L[i]^{k+r} * L[i]^j = sum_i ω^{i(k+r+j)}.
        # For k+r+j ≠ 0 mod n: this sum is 0 (geometric sum over n-th roots).
        # For k+r+j = 0 mod n: sum = n.
        # k+r+j = 0 mod n iff j = -k-r mod n = n-k-r.
        # For r=0,...,n-k-1 and j=0,...,k-1: n-k-r ranges from n-k to 1.
        # j ranges from 0 to k-1.
        # n-k-r ∈ {1,...,n-k}, j ∈ {0,...,k-1}.
        # Intersection: n-k-r ≤ k-1, i.e., r ≥ n-2k+1. For rate 1/2: n-2k+1 = 1.
        # So for r ≥ 1 and j = n-k-r ≤ k-1: the sum is n.
        # And for r=0: j = n-k ≥ k (since n ≥ 2k). So j ∉ {0,...,k-1}. Sum = 0. ✓

        # OK so H*G^T is not quite zero. The (r, j) entry is n * δ_{j, n-k-r}.
        # For r=0: j=n-k ≥ k, so δ = 0. ✓
        # For r=1: j=n-k-1. If n-k-1 ≤ k-1, i.e., n ≤ 2k, i.e., rate ≥ 1/2: δ = 1. Not ✓!

        # So H*G^T ≠ 0 when rate ≥ 1/2! The standard parity check only works when
        # the exponents k+r and j don't collide mod n.

        # For rate 1/2 (k = n/2): the exponents in H are n/2, n/2+1, ..., n-1.
        # The exponents in G are 0, 1, ..., n/2-1.
        # H[r][i] * G[j][i] summed over i: sum_i ω^{i(k+r+j)}.
        # k+r+j mod n: for r ∈ {0,...,n/2-1}, j ∈ {0,...,n/2-1}:
        # k+r+j ∈ {n/2, ..., n/2 + (n/2-1) + (n/2-1)} = {n/2, ..., 3n/2-2}.
        # Modulo n: {n/2, ..., n-1, 0, 1, ..., n/2-2}.
        # So k+r+j ≡ 0 mod n iff r+j = n/2. This happens for (r,j) with r+j = n/2.
        # For r=1, j=n/2-1: sum = n. But j = n/2-1 < k = n/2. So this IS a nonzero entry.

        # Conclusion: H*G^T ≠ 0 for rate 1/2! The standard H is NOT a valid parity check!

        # Wait, that can't be. Let me reconsider.

        # Actually, the standard RS parity check IS H*G^T = 0 when we use
        # evaluation at L = {α, α^2, ..., α^n} (not {α^0, α^1, ..., α^{n-1}}).
        # For our convention L = {ω^0, ..., ω^{n-1}} = {1, ω, ..., ω^{n-1}}:
        # G[j][i] = L[i]^j = ω^{ij}. H[r][i] = L[i]^{k+r} = ω^{i(k+r)}.
        # (G^T H^T)_{j,r} = sum_i ω^{ij} * ω^{i(k+r)} = sum_i ω^{i(j+k+r)}.
        # For j+k+r ≡ 0 mod n: sum = n. Otherwise: 0.
        # j+k+r ≡ 0 mod n iff j ≡ -(k+r) ≡ n-k-r mod n.
        # For j ∈ {0,...,k-1}, r ∈ {0,...,n-k-1}: j = n-k-r.
        # n-k-r ∈ {n-k-(n-k-1), ..., n-k-0} = {1, ..., n-k}.
        # j ∈ {0,...,k-1}: intersection when n-k-r ≤ k-1, i.e., r ≥ n-2k+1.

        # For rate 1/2 (k = n/2): r ≥ 1. So for r ≥ 1, j = n-k-r = n/2-r ∈ {0,...,n/2-1} ✓.
        # So (G H^T)_{j,r} = n for (j,r) with j = n/2-r, r ≥ 1. NOT zero!

        # This means our H is NOT a valid parity check matrix for this code!
        # The standard parity check for RS on {1, ω, ..., ω^{n-1}} uses
        # different exponents to avoid this collision.

        # CRITICAL BUG: the H matrix I've been using is WRONG.

        # The correct parity check for RS[n,k] on L = {1, ω, ..., ω^{n-1}}:
        # H should satisfy HG^T = 0 and have rank n-k.
        # The standard choice: H[r][i] = L[i]^{k+r} does NOT work when n ≤ 2k.

        # Actually wait. Let me double-check with n=6, k=3.
        # H[r][i] = ω^{i(3+r)} for r=0,1,2 and i=0,...,5.
        # G[j][i] = ω^{ij} for j=0,1,2 and i=0,...,5.
        # (G H^T)_{j,r} = sum_{i=0}^5 ω^{ij} ω^{i(3+r)} = sum_i ω^{i(j+3+r)}.
        # For j+3+r ≡ 0 mod 6: sum = 6. Otherwise: 0.
        # j+3+r ∈ {3, ..., 3+2+2} = {3, ..., 7}.
        # j+3+r ≡ 0 mod 6 iff j+3+r = 6, i.e., j+r = 3.
        # (j,r) with j+r = 3: (0,3) — but r ≤ 2! So no. (1,2): ✓. (2,1): ✓.

        # So (G H^T)_{1,2} = 6 ≠ 0 and (G H^T)_{2,1} = 6 ≠ 0.
        # This means H is NOT a parity check for G!

        # But our previous computations seemed to work... Let me re-examine.

        # The conditions we computed are: for each error set B, the left kernel of V_S
        # (the Vandermonde submatrix) applied to c|_S. These conditions are CORRECT
        # (they don't use H). The H matrix was only used for the syndrome representation,
        # which we haven't actually used in the critical computations (v4, v5).

        # So our condition-rank results are CORRECT. But the "syndrome space" interpretation
        # via H is WRONG because H is not a valid parity check.

        # For the polynomial analysis: I should just use the DFT directly, not H.

        n_inv = pow(n, p - 2, p)

        # Just compute the DFT of v (the null vector) directly.
        # v has already been computed in v5 as a vector in F_p^n.
        # Let me compute it here from scratch.
        pass

    # === Simpler approach: just compute the DFT of a canonical worst-case center ===

    # For each worst-case syndrome s:
    # Find an error vector e with He = s and wt(e) ≤ w.
    # The center c = e (taking the all-zero codeword as the list member).
    # Then v = e is a valid center.
    # DFT of e gives the polynomial representation.

    # But this is arbitrary (depends on which error vector we pick).
    # The CANONICAL center is the one in RS_k^⊥... but we've shown H is wrong.

    # Let me just compute DFT of several worst-case error vectors.

    n_inv = pow(n, p - 2, p)

    for idx, s in enumerate(worst_syndromes[:3]):
        print(f"\n  --- Worst-case syndrome #{idx}: s = {s} ---")

        # Find all error vectors with this syndrome
        errors = []
        for wt in range(1, w + 1):
            for positions in combinations(range(n), wt):
                def enum_nonzero(wt, p):
                    if wt == 0:
                        yield ()
                        return
                    for v in range(1, p):
                        for rest in enum_nonzero(wt - 1, p):
                            yield (v,) + rest
                for vals in enum_nonzero(wt, p):
                    ss = [0] * (n - k)
                    for j, pos in enumerate(positions):
                        for r in range(n - k):
                            ss[r] = (ss[r] + vals[j] * H[r][pos]) % p
                    if tuple(ss) == s:
                        e = [0] * n
                        for j, pos in enumerate(positions):
                            e[pos] = vals[j]
                        errors.append(e)

        print(f"  {len(errors)} error vectors, corresponding to {len(set(tuple(sorted(i for i in range(n) if e[i] != 0)) for e in errors))} distinct error sets")

        # Show the first error vector and its DFT
        if errors:
            e = errors[0]
            positions = tuple(i for i in range(n) if e[i] != 0)
            print(f"  Example error: e = {e} (positions {positions})")

            # DFT of e
            g = dft(e, omega, n, p)
            print(f"  DFT(e) = {g}")
            print(f"  Polynomial: g(x) = ", end="")
            terms = []
            for j in range(n):
                if g[j] != 0:
                    if j == 0:
                        terms.append(f"{g[j]}")
                    elif j == 1:
                        terms.append(f"{g[j]}x")
                    else:
                        terms.append(f"{g[j]}x^{j}")
            print(" + ".join(terms) if terms else "0")

            # Which coefficients are nonzero?
            print(f"  Nonzero DFT coefficients: {[(j, g[j]) for j in range(n) if g[j] != 0]}")
            print(f"  Coefficients in range [0,k): {[(j, g[j]) for j in range(k) if g[j] != 0]}")
            print(f"  Coefficients in range [k,n): {[(j, g[j]) for j in range(k, n) if g[j] != 0]}")

            # Verify: idft gives back e
            e_check = idft(g, omega, n, p)
            assert e_check == e, f"IDFT mismatch: {e_check} vs {e}"

            # The "syndrome part" of g is g_k, ..., g_{n-1}
            # The "codeword part" is g_0, ..., g_{k-1}
            # For the coset RS_k^⊥ representative: set g_0 = ... = g_{k-1} = 0.
            g_syn = [0] * k + g[k:]
            v_canonical = idft(g_syn, omega, n, p)
            print(f"\n  Canonical coset representative (g_0=...=g_{{k-1}}=0):")
            print(f"  v = {v_canonical}")
            print(f"  DFT(v) = {g_syn}")
            print(f"  wt(v) = {sum(1 for x in v_canonical if x != 0)}")

            # Now check: how many codewords at distance ≤ w from v_canonical?
            # For each codeword f = eval(h), deg(h) < k: d(v, f) = wt(v - f).
            # v - f = eval(g_syn - h), which has nonzero coefficients only at degrees k,...,n-1.
            # Wait, g_syn has 0 at degrees 0,...,k-1, and same as g at k,...,n-1.
            # So v_canonical - f = eval(g_syn) - eval(h) = eval(g_syn - h).
            # g_syn - h has coefficients: at degrees 0,...,k-1: -h_j; at degrees k,...,n-1: g_j.
            # wt(v-f) = #{i : (g_syn - h)(ω^i) ≠ 0}.

            # For the ZERO codeword (h=0): d(v, 0) = wt(v_canonical).
            # For other codewords: d(v, f) depends on h.

            # Actually the list size at v_canonical is the same as at e
            # (since they differ by a codeword).

    # === Also: for the null vector from v5, compute its DFT ===
    print(f"\n  === DFT of null vectors from v5 ===")


# Run
analyze_polynomial_structure(6, 3, 7, 2)
analyze_polynomial_structure(8, 4, 17, 3)
analyze_polynomial_structure(10, 5, 11, 3)
