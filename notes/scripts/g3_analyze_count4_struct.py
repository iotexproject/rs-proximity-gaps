"""g3_analyze_count4_struct.py — analyze the structure of bad={748, 898, 1009, 1090}.

This is the first NON-cyclotomic strict-above-J counterexample to Conjecture D.
What structure does bad have?
"""
import sys, os
sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))


def main():
    p = 1153
    bad = [748, 898, 1009, 1090]
    print(f"q = {p}")
    print(f"bad = {bad}")
    print(f"q-1 = {p-1} = 2^7 · 3^2 = {(p-1) // 9} · 9")
    print()

    # Compute elementary symmetric functions of bad
    sigma_1 = sum(bad) % p
    sigma_2 = sum(bad[i]*bad[j] for i in range(4) for j in range(i+1, 4)) % p
    sigma_3 = sum(bad[i]*bad[j]*bad[k] for i in range(4) for j in range(i+1, 4) for k in range(j+1, 4)) % p
    sigma_4 = (bad[0]*bad[1]*bad[2]*bad[3]) % p
    print(f"σ_1 = sum(bad) = {sigma_1}")
    print(f"σ_2 = {sigma_2}")
    print(f"σ_3 = {sigma_3}")
    print(f"σ_4 = product = {sigma_4}")
    print()

    # Polynomial P(z) = z^4 - σ_1 z^3 + σ_2 z^2 - σ_3 z + σ_4
    # This is the minimal polynomial of bad (root set).
    print(f"P(z) = z^4 - {sigma_1}z^3 + {sigma_2}z^2 - {sigma_3}z + {sigma_4}")
    print(f"     = z^4 + {(-sigma_1)%p}z^3 + {sigma_2}z^2 + {(-sigma_3)%p}z + {sigma_4} mod {p}")
    print()

    # Check if P(z) has any algebraic structure
    # E.g., is P(z) = Q(z²) for some quadratic Q? (would mean bad pairs are ±)
    # σ_1 = 0 ⟺ sum of pairs is 0 ⟺ each pair (a, -a)
    # Or σ_3 = 0 with σ_1 = 0?
    print(f"Symmetry checks:")
    print(f"  σ_1 = 0? {sigma_1 == 0}  → pairs (a, -a)?")
    print(f"  σ_3 = 0? {sigma_3 == 0}  → cubic-symmetric?")
    print()

    # Pair sums
    print(f"Pairwise sums (bad[i] + bad[j] mod p):")
    sums = sorted({(bad[i] + bad[j]) % p for i in range(4) for j in range(i+1, 4)})
    print(f"  {sums}")
    # If some sum = 0 mod p, that's an (a, -a) pair.
    zero_sums = [(bad[i], bad[j]) for i in range(4) for j in range(i+1, 4) if (bad[i] + bad[j]) % p == 0]
    print(f"  pairs (a, -a): {zero_sums}")

    # Pairwise products
    print(f"Pairwise products:")
    products = sorted({(bad[i] * bad[j]) % p for i in range(4) for j in range(i+1, 4)})
    print(f"  {products}")
    # Is any product = 1? (would mean a · b = 1, so b = 1/a)
    one_products = [(bad[i], bad[j]) for i in range(4) for j in range(i+1, 4) if (bad[i] * bad[j]) % p == 1]
    print(f"  pairs (a, 1/a): {one_products}")

    # Check if bad = β + α·H for H = roots of some polynomial
    # E.g., quartic of form z^4 - 1 = 0 (μ_4) or z^4 + bz^2 + c = 0 (biquadratic)
    print()
    print(f"Is bad set the roots of a biquadratic polynomial in (z - β)?")
    for beta in range(p):
        translates = sorted([(b - beta) % p for b in bad])
        # σ_1 of translates
        s1 = sum(translates) % p
        s3 = sum(translates[i]*translates[j]*translates[k] for i in range(4) for j in range(i+1, 4) for k in range(j+1, 4)) % p
        if s1 == 0 and s3 == 0:
            print(f"  β = {beta}: σ_1 = σ_3 = 0 (BIQUADRATIC)")
            print(f"    translates = {translates}")
            # Then P(z + β) = z^4 + s_2 z^2 + s_4
            s2 = sum(translates[i]*translates[j] for i in range(4) for j in range(i+1, 4)) % p
            s4 = (translates[0]*translates[1]*translates[2]*translates[3]) % p
            print(f"    P(z) = z^4 + {s2}z^2 + {s4}")
            # Substituting w = z²: P_w(w) = w^2 + s_2 w + s_4. Roots in F_p?
            # discriminant = s_2² - 4·s_4
            disc = (s2 * s2 - 4 * s4) % p
            print(f"    discriminant of w² + s_2 w + s_4 = {disc}")
            sqrt_disc = pow(disc, (p+1)//4, p) if pow(disc, (p-1)//2, p) == 1 else None
            print(f"    sqrt(disc) = {sqrt_disc}")
            if sqrt_disc is not None:
                w1 = (- s2 + sqrt_disc) * pow(2, p-2, p) % p
                w2 = (- s2 - sqrt_disc) * pow(2, p-2, p) % p
                print(f"    w-roots: {w1}, {w2}")
                # Check if w1 and w2 are squares in F_p
                w1_sqrt_test = pow(w1, (p-1)//2, p)
                w2_sqrt_test = pow(w2, (p-1)//2, p)
                print(f"    w1 is QR? {w1_sqrt_test == 1}, w2 is QR? {w2_sqrt_test == 1}")
            break


if __name__ == "__main__":
    main()
