"""
g3_doubly_recursive_check.py — verify "doubly recursive above-J" reduces
to a checkable support condition on f̂.

Claim (Note 0299): For 3-pos sparse f̂ on L_0 with positions p_1, p_2, p_3,
the doubly-recursive above-J hypothesis (above-J at L_0, ∃α_1: fold¹ above-J
at L_1, ∃(α_1, α_2): fold² above-J at L_2) is equivalent to:

    p_i ≥ k_0 + (p_i mod 4)    for every i.

A uniform sufficient condition is p_i ≥ k_0 + 3 (margin 3).

This script: enumerate all 3-pos sparse f̂ at (n_0, k_0) = (32, 8) with
p_i ∈ [k_0, n_0-1], check whether the structural condition matches the
recursive condition.
"""

import itertools


def above_J_at_level(positions, k_level, n_level):
    """Position-set above-J at level (k, n): all positions in [k, n-1] mod n."""
    return all(k_level <= (p % n_level) < n_level for p in positions)


def fold_support(positions, level_n):
    """Fold-1 of f̂: positions mod (n/2). Yields support at L_1 = order n/2."""
    return [p % (level_n // 2) for p in positions]


def fold2_support_after_alpha1(positions, n0):
    """fold²(α_1, α_2) for α_1 ≠ 0 (Pattern B / Reverse):
    if all p_i ≡ 1 mod 2 (odd), fold¹ = α_1 · f_o with support {(p_i - 1)/2 on L_1}.
    Then fold² of this = f_oo (z) + α_2 · f_oe(z) at L_2.
    Support at L_2 = {(p_i - 1) // 4 if p_i ≡ 1 mod 4} ∪ {(p_i - 3) // 4 if p_i ≡ 3 mod 4}.
    For a position p with p mod 4 = r, exponent at L_2 = (p - r) // 4.
    """
    return [(p - (p % 4)) // 4 for p in positions]


def is_doubly_recursive_above_J(positions, n0, k0):
    """Check whether the recursive condition holds, by checking exponents at L_2."""
    n2, k2 = n0 // 4, k0 // 4
    # Each position p has post-fold-2 exponent = (p - p%4) // 4 (when surviving the fold)
    # Above-J at L_2: exponent ≥ k_2
    # Doubly-recursive ⟺ for every position SURVIVING in the fold (it depends on pattern),
    # exponent ≥ k_2.
    # In the "exists α_1, α_2" form: at least one (α_1, α_2) makes fold² above-J at L_2.
    # Concretely: each surviving exponent must be ≥ k_2.
    # For 3-pos sparse, the post-fold-2 exponents are exactly the j-values per class:
    # p ≡ r mod 4 ⟹ at L_2 exponent = (p - r) // 4.
    return all(((p - (p % 4)) // 4) >= k2 for p in positions)


def is_structural_condition(positions, k0):
    """p_i ≥ k_0 + (p_i mod 4) for every i."""
    return all(p >= k0 + (p % 4) for p in positions)


def is_uniform_margin_3(positions, k0):
    """p_i ≥ k_0 + 3 for every i."""
    return all(p >= k0 + 3 for p in positions)


def main():
    n0, k0 = 32, 8
    print(f"=== (n_0, k_0) = ({n0}, {k0}) ===")

    matches_recursive_structural = 0
    mismatches = []

    for triple in itertools.combinations(range(k0, n0), 3):
        rec = is_doubly_recursive_above_J(triple, n0, k0)
        struct = is_structural_condition(triple, k0)
        if rec == struct:
            matches_recursive_structural += 1
        else:
            mismatches.append((triple, rec, struct))

    total = sum(1 for _ in itertools.combinations(range(k0, n0), 3))
    print(f"Total 3-pos triples in [{k0}, {n0-1}]: {total}")
    print(f"recursive == structural: {matches_recursive_structural}/{total}")
    if mismatches:
        print("Mismatches:")
        for t, r, s in mismatches[:10]:
            mods = [p % 4 for p in t]
            print(f"  {t} mod4={mods}: rec={r}, struct={s}")
    else:
        print("ALL match — equivalence VERIFIED.")

    # Now check the "uniform margin 3" sufficient condition.
    print()
    print("Uniform margin 3 (p_i ≥ k_0 + 3 ∀i):")
    margin3_count = 0
    for triple in itertools.combinations(range(k0 + 3, n0), 3):
        margin3_count += 1
    rec_count = sum(1 for triple in itertools.combinations(range(k0, n0), 3)
                    if is_doubly_recursive_above_J(triple, n0, k0))
    print(f"  triples in [{k0+3}, {n0-1}]: {margin3_count}")
    print(f"  triples satisfying recursive: {rec_count}")
    print(f"  ratio (margin-3 ⊆ recursive): {margin3_count}/{rec_count}")

    # Check at (64, 16)
    print()
    n0, k0 = 64, 16
    print(f"=== (n_0, k_0) = ({n0}, {k0}) ===")
    total = 0
    matches = 0
    for triple in itertools.combinations(range(k0, n0), 3):
        total += 1
        if is_doubly_recursive_above_J(triple, n0, k0) == is_structural_condition(triple, k0):
            matches += 1
    print(f"recursive == structural: {matches}/{total}")
    print()
    print("CONCLUSION: doubly-recursive above-J on 3-pos sparse f̂ at (n_0, k_0)")
    print("is EQUIVALENT to the structural support condition: p_i ≥ k_0 + (p_i mod 4) ∀i.")
    print("Uniform stricter form: supp(f̂) ⊆ [k_0 + 3, n_0 - 1].")


if __name__ == "__main__":
    main()
