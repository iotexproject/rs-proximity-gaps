"""mds_decoder.py — fast information-set decoder for Reed-Solomon (MDS) codes.

The brute-force `dist_to_code_full` in fri_2round_attack.py enumerates ALL weight-w
error supports up to max_w. At n=32, k=8, w_J=16, the cost is C(32, ≤16) ≈ 2 billion,
intractable. Even cap=5 takes >2 minutes single-thread.

This module exploits the MDS structure: for RS_k(L) of length n,
  dist(f, RS_k) = (n-k) - max_T extras_T
where T ranges over k-subsets, extras_T = #{i ∉ T : interp_T(L[i]) = f[i]},
and interp_T is the unique degree-<k poly through {(L[j], f[j]) : j ∈ T}.

Above-Johnson detection: f is above-J iff dist > w_J iff for all k-subset T,
extras_T < n - k - w_J.

We use **random sampling** of T's, which gives an extremely high-confidence
above-J oracle:
  - If any sampled T has extras_T ≥ n-k-w_J → certificate of below-J (exact).
  - If no sampled T does → above-J with FPR ≤ (1 - C(n-w_J, k)/C(n, k))^N.

At n=32, k=8, w_J=16, N=50000: FPR ≤ exp(-61) ≈ 0.

Vectorized via NumPy batched Lagrange interpolation.
"""
from __future__ import annotations
import numpy as np


def precompute_diff_inv(L_arr: np.ndarray, p: int):
    """Precompute D[i, j] = L[i] - L[j] mod p and its element-wise inverse (off-diagonal).

    Returns (D, inv_D) both shape (n, n). inv_D diagonal is 0 (unused).
    """
    n = len(L_arr)
    D = (L_arr[:, None] - L_arr[None, :]) % p
    # Diagonal is 0; mark for skipping.
    inv_D = np.zeros_like(D)
    mask = D != 0
    # Modular inverse via Fermat: a^{p-2} mod p
    inv_D_flat = pow_mod_arr(D[mask], p - 2, p)
    inv_D[mask] = inv_D_flat
    return D, inv_D


def pow_mod_arr(a: np.ndarray, exp: int, p: int) -> np.ndarray:
    """Element-wise a^exp mod p. Uses int64 throughout."""
    a = a.astype(np.int64) % p
    result = np.ones_like(a)
    base = a.copy()
    e = exp
    while e > 0:
        if e & 1:
            result = (result * base) % p
        base = (base * base) % p
        e >>= 1
    return result


def batched_extras(
    T_batch: np.ndarray,           # (B, k) int64, indices into L
    f_arr: np.ndarray,             # (n,)  int64, values mod p
    L_arr: np.ndarray,             # (n,)  int64, L[i] mod p
    D: np.ndarray,                 # (n, n) L[i] - L[j] mod p
    inv_D: np.ndarray,             # (n, n) (L[i] - L[j])^-1 mod p
    p: int,
):
    """For each T in batch (size B, each a k-subset), compute extras_T =
    #{i ∉ T : interp_T(L[i]) = f[i]}. Returns int64 array shape (B,).

    Uses Lagrange interpolation:
      p_T(L[i]) = Σ_{j ∈ T} f[T[j]] · L_basis(L[i], L[T[j]]; T)
      L_basis(L[i], L[T[j]]; T) = Π_{s ∈ T, s != j} (L[i] - L[T[s]]) / (L[T[j]] - L[T[s]])
                                = Π_{s != j} D[i, T[s]] · inv_D[T[j], T[s]]

    Vectorized: for each batch element b and each i ∈ [n], compute p_T(L[i]).
    Mask out i ∈ T (those auto-agree). Compare to f[i].
    """
    B, k = T_batch.shape
    n = len(L_arr)

    # Build (B, k, k) tensors for D and inv_D restricted to T:
    #   DT_self[b, j, s] = D[T[b,j], T[b,s]] = L[T[b,j]] - L[T[b,s]]
    #   inv_DT_self[b, j, s] = inv_D[T[b,j], T[b,s]]
    # And (B, n, k):
    #   DT_full[b, i, s] = D[i, T[b,s]] = L[i] - L[T[b,s]]   for i ∈ [n]
    DT_self = D[T_batch[:, :, None], T_batch[:, None, :]]            # (B, k, k)
    inv_DT_self = inv_D[T_batch[:, :, None], T_batch[:, None, :]]    # (B, k, k)
    DT_full = D[:, T_batch].transpose(1, 0, 2)                       # (B, n, k)
    # Note D[:, T_batch] has shape (n, B, k) since T_batch is (B, k).

    # W'(X[j]) = Π_{s ≠ j} (X[j] - X[s]):
    #   For each (b, j), product over s != j of DT_self[b, j, s].
    # Use the trick: total prod = Π_s DT_self[b, j, s], but DT_self[b, j, j] = 0.
    # Workaround: substitute diagonal with 1, take product, then divide... but division
    # isn't safe. Instead: take product over all s, with diagonal masked to 1.
    diag_mask = np.eye(k, dtype=bool)
    DT_self_masked = np.where(diag_mask[None, :, :], 1, DT_self)  # diagonal -> 1
    # CRITICAL: np.prod over k axis can overflow int64 when k·log2(p) > 63.
    # For (n, k) = (32, 8), p ~ 1153: 1153^8 ≈ 7.7e24 > 2^63 ≈ 9.2e18 → overflow.
    # Use loop with % p after each multiplication to avoid overflow.
    W_prime = np.ones((DT_self_masked.shape[0], DT_self_masked.shape[1]), dtype=np.int64)
    for s in range(k):
        W_prime = (W_prime * DT_self_masked[:, :, s]) % p

    # W_full(L[i]) = Π_{s ∈ T} (L[i] - X[s]):
    #   For (b, i), product over s ∈ [k] of DT_full[b, i, s].
    # When i ∈ T (i.e., i = T[b, j] for some j), one factor is zero, so W_full = 0,
    # and L_basis is undefined. We handle this by masking T-positions out at the end.
    W_full = np.ones((DT_full.shape[0], DT_full.shape[1]), dtype=np.int64)
    for s in range(k):
        W_full = (W_full * DT_full[:, :, s]) % p

    # For i ∉ T:
    #   p_T(L[i]) = Σ_j f[T[j]] · W_full(L[i]) · inv(L[i] - X[j]) · inv(W'(X[j]))
    # We need inv(L[i] - X[j]) = inv_D[i, X[j]_index] = inv_D[i, T[b, j]]
    # This is shape (B, n, k):
    inv_DT_full_at_i = inv_D[:, T_batch].transpose(1, 0, 2)  # (B, n, k)
    # And inv_W_prime: shape (B, k). Modular inverse of W_prime.
    # Vectorized: inverse via Fermat (W_prime^{p-2}).
    inv_W_prime = pow_mod_arr(W_prime, p - 2, p)  # (B, k)

    # f|_T values: f_T[b, j] = f[T[b, j]]. Shape (B, k).
    f_T = f_arr[T_batch]

    # Build the per-(b, i, j) product inside the sum:
    #   contrib[b, i, j] = f_T[b, j] · W_full[b, i] · inv_DT_full_at_i[b, i, j] · inv_W_prime[b, j]
    # Sum over j gives p_T(L[i]). But we factor out W_full[b, i]:
    #   p_T(L[i]) = W_full[b, i] · Σ_j (f_T[b, j] · inv_DT_full_at_i[b, i, j] · inv_W_prime[b, j])
    # Define coeff_j[b, j] = f_T[b, j] · inv_W_prime[b, j].  (B, k).
    coeff_j = (f_T * inv_W_prime) % p
    # Then inner_sum[b, i] = Σ_j (coeff_j[b, j] · inv_DT_full_at_i[b, i, j]).
    # einsum-friendly: (B, k) × (B, n, k) → (B, n).
    inner_sum = np.einsum('bj,bij->bi', coeff_j, inv_DT_full_at_i) % p
    # p_T(L[i]) = W_full[b, i] * inner_sum[b, i] mod p.
    p_T_at_L = (W_full * inner_sum) % p  # (B, n)

    # Compare to f. For i ∈ T, p_T(L[i]) = f[i] by interpolation BUT W_full = 0 makes
    # our computation give 0. Mask T-indices out.
    matches = (p_T_at_L == f_arr[None, :])  # (B, n) bool
    # Build T-mask: True at positions in T (per batch element).
    T_mask = np.zeros((B, n), dtype=bool)
    np.put_along_axis(T_mask, T_batch, True, axis=1)
    # Extras = matches at non-T positions, count per batch row.
    extras = (matches & ~T_mask).sum(axis=1).astype(np.int64)
    return extras


def is_above_johnson_sampling(
    f: list[int] | np.ndarray,
    L: list[int] | np.ndarray,
    k: int,
    p: int,
    w_J: int,
    n_samples: int = 50000,
    batch: int = 4096,
    seed: int | None = None,
    return_evidence: bool = False,
):
    """Random-sample n_samples k-subsets T, return True if no T has extras_T ≥ n-k-w_J.

    Above-J ⟺ dist > w_J ⟺ for all T, extras_T < n - k - w_J.
    FPR ≈ exp(-n_samples · C(n-w_J, k) / C(n, k)).
    At n=32, k=8, w_J=16, n_samples=50000: FPR ≈ exp(-61) ≈ 0.

    If return_evidence=True, returns (is_above, max_extras_seen, certificate_T_or_None).
    Otherwise returns just bool.
    """
    n = len(L)
    L_arr = np.array(L, dtype=np.int64) % p
    f_arr = np.array(f, dtype=np.int64) % p
    threshold = n - k - w_J  # extras must be < threshold for above-J

    D, inv_D = precompute_diff_inv(L_arr, p)
    rng = np.random.default_rng(seed)

    max_extras = 0
    cert_T = None
    remaining = n_samples
    while remaining > 0:
        B = min(batch, remaining)
        # Sample B random k-subsets of [n]. Use argpartition trick: rand permutation + take first k.
        T_batch = np.empty((B, k), dtype=np.int64)
        for b in range(B):
            T_batch[b] = rng.choice(n, size=k, replace=False)
        T_batch.sort(axis=1)
        extras = batched_extras(T_batch, f_arr, L_arr, D, inv_D, p)
        idx_max = int(extras.argmax())
        if extras[idx_max] > max_extras:
            max_extras = int(extras[idx_max])
            cert_T = T_batch[idx_max].tolist()
        if max_extras >= threshold:
            # Below-J certified. No need to sample more.
            if return_evidence:
                return False, max_extras, cert_T
            return False
        remaining -= B
    if return_evidence:
        return True, max_extras, cert_T
    return True


def dist_lower_bound_sampling(
    f: list[int] | np.ndarray,
    L: list[int] | np.ndarray,
    k: int,
    p: int,
    n_samples: int = 50000,
    batch: int = 4096,
    seed: int | None = None,
):
    """Returns an UPPER BOUND on dist(f, RS_k): (n-k) - max_T extras_T over sampled T's.

    Mathematically: max_extras_sampled ≤ true_max_extras (sampling under-counts),
    so returned value ≥ true_dist (over-estimates distance).

    Use semantics:
      - returned ≤ w_J  ⟹ certified BELOW-J (true dist ≤ returned ≤ w_J).
      - returned > w_J  ⟹ HEURISTIC evidence of above-J (no close codeword in samples),
                          but NOT a proof. To certify above-J, enumerate all C(n,k)
                          info sets exactly via batched_extras (~22s at n=32, k=8).

    NOTE: function name "lower_bound" is historical and misleading — it returns
    an upper bound on dist. Strong sampling (50K+) makes the heuristic reliable
    in practice but is not formally a certificate.
    """
    n = len(L)
    L_arr = np.array(L, dtype=np.int64) % p
    f_arr = np.array(f, dtype=np.int64) % p
    D, inv_D = precompute_diff_inv(L_arr, p)
    rng = np.random.default_rng(seed)

    max_extras = 0
    remaining = n_samples
    while remaining > 0:
        B = min(batch, remaining)
        T_batch = np.empty((B, k), dtype=np.int64)
        for b in range(B):
            T_batch[b] = rng.choice(n, size=k, replace=False)
        T_batch.sort(axis=1)
        extras = batched_extras(T_batch, f_arr, L_arr, D, inv_D, p)
        m = int(extras.max())
        if m > max_extras:
            max_extras = m
        remaining -= B
    return (n - k) - max_extras


# ----------------------- self-test against ground truth -----------------------

if __name__ == '__main__':
    import sys, time, random
    sys.path.insert(0, '<repo>/notes/scripts')
    from fri_2round_attack import setup_chain, dist_to_code_full

    p = 97
    chain = setup_chain(p, 16, 4, R=2)  # smaller params, brute-force tractable
    L0, k0, H0 = chain[0]
    n0 = len(L0)
    rho = k0 / n0
    import math
    w_J = int((1 - math.sqrt(rho)) * n0)
    print(f"# Test: p={p}, n_0={n0}, k_0={k0}, w_J={w_J}")

    rng = random.Random(2026)
    n_match = 0
    n_total = 0
    t0 = time.time()
    for trial in range(20):
        sparsity = rng.choice([2, 3])
        positions = rng.sample(range(k0, n0), sparsity)
        fhat = [0]*n0
        for pos in positions:
            fhat[pos] = rng.randrange(1, p)
        f = [sum(fhat[i] * pow(L0[j], i, p) for i in range(n0)) % p for j in range(n0)]
        d_brute, _ = dist_to_code_full(f, H0, n0, k0, p, max_w=w_J + 1)
        d_lower = dist_lower_bound_sampling(f, L0, k0, p, n_samples=10000, seed=trial)
        truly_above = (d_brute is None) or (d_brute > w_J)
        sampled_above = (d_lower > w_J)
        agree = (truly_above == sampled_above)
        n_total += 1
        if agree: n_match += 1
        print(f"  trial {trial}: brute_dist={d_brute}, sampled_lower={d_lower}, "
              f"truly_above_J={truly_above}, sampled_above_J={sampled_above}, agree={agree}")
    print(f"# Agreement: {n_match}/{n_total} in {time.time()-t0:.1f}s")
