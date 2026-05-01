"""
Theoretical analysis of per-word list size bound.

For a fixed word w ∈ F_p^n and RS_k code on L (|L|=n), the list size is:
  L_δ(w) = #{h ∈ RS_k : |{i : w(x_i) = h(x_i)}| ≥ (1-δ)n}

We want to bound L_δ(w) for all w.

Key observation: if h₁, h₂ ∈ RS_k both agree with w on sets S₁, S₂ ⊂ L
with |S₁|, |S₂| ≥ t = (1-δ)n, then:
  h₁ - h₂ has degree < k
  h₁ - h₂ vanishes on S₁ ∩ S₂ (where both equal w)
  |S₁ ∩ S₂| ≥ |S₁| + |S₂| - n ≥ 2t - n

If 2t - n > k - 1, then h₁ - h₂ (degree < k) has more roots than its degree,
so h₁ = h₂. This gives:

  UNIQUE DECODING: if t > (n + k - 1) / 2, i.e., δ < (n - k + 1) / (2n) ≈ (1-ρ)/2,
  then L_δ ≤ 1. (This is the classical unique decoding bound.)

For δ in the intermediate zone ((1-ρ)/2 < δ < 1-ρ), L_δ > 1 is possible.
The question is: how large can it be?

JOHNSON BOUND: L_δ ≤ n/k when δ < 1 - √ρ.

For our parameters (n=36, k=2, ρ=1/18):
  Unique decoding: δ < (36-1)/(72) = 35/72 ≈ 0.486
  Johnson: δ < 1 - √(1/18) ≈ 0.764
  CS threshold: δ = 1 - 6/36 = 5/6 ≈ 0.833

So CS operates ABOVE Johnson (δ=0.833 > 0.764). In this zone, the Johnson bound
doesn't apply, and the list size CAN be large.

But empirically: max list size is still small (≤ 9).

Let's compute the theoretical maximum list size by the "Plotkin bound" argument:

If L_δ = M (i.e., M codewords h₁,...,h_M all δ-close to w), then:
  Total agreement = Σ_i |S_i| ≥ Mt
  Total pairwise agreement = Σ_{i<j} |S_i ∩ S_j|

For distinct codewords h_i, h_j: h_i - h_j has degree < k and at most k-1 roots in L.
So h_i and h_j can agree on at most k-1 points of L (where both equal w).
Wait, that's the agreement between h_i and h_j on L, not their agreement with w.

Actually: S_i = {x ∈ L : w(x) = h_i(x)} and S_j = {x ∈ L : w(x) = h_j(x)}.
S_i ∩ S_j = {x ∈ L : w(x) = h_i(x) = h_j(x)}, so on S_i ∩ S_j, h_i = h_j.
h_i - h_j vanishes on S_i ∩ S_j.
Since deg(h_i - h_j) < k, |S_i ∩ S_j| ≤ k - 1 (unless h_i = h_j).

So: for i ≠ j, |S_i ∩ S_j| ≤ k - 1.

Now use counting: Σ_x |{i : x ∈ S_i}|² = Σ_{i,j} |S_i ∩ S_j| = M·t + 2·C(M,2)·(k-1) max
  (Actually: Σ_{i,j} |S_i ∩ S_j| = Σ_i |S_i| + 2·Σ_{i<j} |S_i ∩ S_j| ≤ Mt + M(M-1)(k-1))

Also: Σ_x |{i : x ∈ S_i}|² ≥ (Σ_x |{i : x ∈ S_i}|)² / n = (Mt)² / n
  (by Cauchy-Schwarz)

So: (Mt)² / n ≤ Mt + M(M-1)(k-1)
    M²t² / n ≤ Mt + M(M-1)(k-1)
    Mt/n ≤ 1 + (M-1)(k-1)/t

If M is large: Mt/n ~ (M-1)(k-1)/t, so M ~ t²/(n(k-1)) = ((1-δ)n)² / (n(k-1)) = (1-δ)²n/(k-1).

For our parameters: n=36, k=2, (1-δ)=6/36=1/6:
  M_max ~ (1/6)² · 36 / 1 = 36/36 = 1. Not useful for small parameters!

For LARGER n: (1-δ) = rm/n = r·m/(s·m) = r/s.
  M_max ~ (r/s)² · n / (k-1) = (r/s)² · sm / ((r-2)m - 1) ≈ r²s / (s²(r-2)) = r²/(s(r-2))

For CS with r=3, s=n/m: M_max ≈ 9/(s · 1) = 9·m/n. For m=2, n=36: 9·2/36 = 0.5 < 1.

So the Plotkin-type argument gives M ≤ O(1) for CS parameters!

Let me verify and sharpen this.
"""

def list_size_bound(n, k, t):
    """
    Plotkin-type upper bound on list size.

    Given: M codewords h_1,...,h_M in RS_k, each agreeing with w on ≥ t points.
    Pairwise: |S_i ∩ S_j| ≤ k-1 for i≠j.
    Cauchy-Schwarz: M²t²/n ≤ Mt + M(M-1)(k-1)
    → M ≤ (n(k-1) + nt - t²) / (t² - n(k-1))  when t² > n(k-1)
    → i.e., M ≤ n(k-1+t) / (t² - n(k-1)) ... let me redo
    """
    # M²t²/n ≤ Mt + M(M-1)(k-1)
    # Divide by M: Mt²/n ≤ t + (M-1)(k-1)
    # Mt²/n - t ≤ (M-1)(k-1)
    # M(t²/n - (k-1)) ≤ t - (k-1)   ... wait
    # Mt²/n - (M-1)(k-1) ≤ t
    # M(t²/n - (k-1)) + (k-1) ≤ t
    # M ≤ (t - (k-1)) / (t²/n - (k-1))  when t²/n > k-1

    if t * t > n * (k - 1):
        M_bound = (t - (k - 1)) / (t * t / n - (k - 1))
        return M_bound
    else:
        return float('inf')  # Cauchy-Schwarz doesn't help

def main():
    print("=== Plotkin-type list size bounds ===\n")

    # CS parameters
    cases = [
        ("CS n=36", 36, 2, 6),
        ("CS n=60", 60, 2, 6),
        ("CS n=72", 72, 2, 6),
        ("CS n=120", 120, 2, 6),
        ("CS n=360", 360, 2, 6),
        ("CS n=1000", 1000, 2, 6),
        ("FRI-like n=2^10", 1024, 2, 6),
        ("FRI-like n=2^20", 2**20, 2, 6),
    ]

    print(f"{'case':>20} {'n':>8} {'k':>4} {'t':>6} {'δ':>8} {'M_bound':>10} {'⌊M⌋':>6}")
    print("-" * 70)
    for label, n, k, t in cases:
        delta = 1 - t/n
        M = list_size_bound(n, k, t)
        M_str = f"{M:.2f}" if M < 1e6 else "∞"
        M_int = str(int(M)) if M < 1e6 else "∞"
        print(f"{label:>20} {n:>8} {k:>4} {t:>6} {delta:>8.4f} {M_str:>10} {M_int:>6}")

    # General: vary t for fixed n=36, k=2
    print(f"\n--- n=36, k=2: list size bound vs agreement threshold t ---")
    print(f"{'t':>4} {'δ':>8} {'M_bound':>10}")
    for t in range(2, 36):
        M = list_size_bound(36, 2, t)
        if M < 100:
            print(f"{t:>4} {1-t/36:>8.3f} {M:>10.2f}")

    # Key question: for what t does M_bound drop below 2?
    print(f"\n--- Threshold for M ≤ 1 (unique decoding boundary) ---")
    for n in [36, 60, 100, 1000, 2**20]:
        k = 2
        for t in range(k, n+1):
            M = list_size_bound(n, k, t)
            if M < 2:
                delta = 1 - t/n
                print(f"  n={n:>8}, k={k}: unique decoding at t≥{t}, δ≤{delta:.4f} (std bound: δ<{(n-k+1)/(2*n):.4f})")
                break

    # The Plotkin bound with k-1 pairwise intersection:
    print(f"\n--- Exact Plotkin formula ---")
    print(f"M ≤ (t - (k-1)) / (t²/n - (k-1)) when t² > n(k-1)")
    print(f"For k=2: M ≤ (t-1) / (t²/n - 1)")
    print(f"This equals 1 when t-1 = t²/n - 1, i.e., t(t-n) = 0, i.e., t=n (trivial) or t=0.")
    print(f"Wait, that means M_bound > 1 for ALL 0 < t < n... ")
    print(f"Let me recheck. M ≤ (t-1)/(t²/n - 1) for t²/n > 1, i.e., t > √n.")
    print(f"At t=√n: M = (√n - 1)/(1 - 1) = ∞. Near t=√n, M is large.")
    print(f"At t=n: M = (n-1)/(n-1) = 1.")
    print(f"The bound decreases from ∞ to 1 as t goes from √n to n.")
    print(f"")
    print(f"For n=36, k=2:")
    for t in [6, 7, 8, 9, 10, 12, 15, 18, 24, 30, 35]:
        if t*t > 36:
            M = (t-1)/(t*t/36.0 - 1)
            print(f"  t={t:>2}: M ≤ {M:.2f}")

if __name__ == "__main__":
    main()
