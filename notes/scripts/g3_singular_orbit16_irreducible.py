"""Use Singular to compute eliminator for ORBIT-16 irreducible (a, b) at (16, 4).

Critical question: do any orbit-16 (gcd(b-a, 16) = 1) irreducible cases have
|B| > 0? If so, |B| ≥ 16, breaking the K ≤ 8 universal claim.

Empirical from prior SymPy sweep: most show Φ = 1 (m = 0). But several
TIMED OUT and remain unverified. Use Singular (faster GB) to close these.
"""
import subprocess
import os
from math import gcd as ggcd

def run_singular(script, timeout=120):
    """Run Singular script with timeout."""
    try:
        result = subprocess.run(
            ['Singular', '-q', '-c', script],
            capture_output=True, text=True, timeout=timeout
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return None, "timeout"
    except FileNotFoundError:
        return None, "Singular not found"


def gb_eliminator(n, k, a, b, timeout=120):
    """Singular GB to compute Φ(ρ)."""
    t = 2 * k
    p_decl = ", ".join(f"p{i}" for i in range(t))
    cert_eqs = []
    sigma_def = f"poly sigma = z^{t}" + "".join(f" + p{i} * z^{i}" for i in range(t)) + ";"
    rem_a_def = f"poly rem_a = reduce(z^{a}, std(sigma));"
    rem_b_def = f"poly rem_b = reduce(z^{b}, std(sigma));"

    script_parts = [
        f"ring R = 0, ({p_decl}, rho, z), (lp({1+t}), dp);",
        sigma_def,
        rem_a_def,
        rem_b_def,
        f"poly h = rho * rem_a + rem_b;",
        # Cert: h mod sigma has deg in z < k. So coef of z^d for d in [k, t-1] = 0.
        # Build cert eqs:
    ]
    # Cert eqs: ideal of high-degree coefficients
    cert_lines = []
    for d in range(k, t):
        cert_lines.append(f"poly cert_{d} = coeffs(h, z)[{d+1}, 1];")

    # Div: σ_S | z^n - 1. So z^n mod σ - 1 = 0. Coefs at all z^d (d < t) = 0 except const = 1 (so z^d coef = 0 for d > 0, and const = 1 means z^0 - 1 = 0).
    # In Singular: rem = reduce(z^n - 1, std(sigma)). All coefs of rem must be 0.
    div_block = [
        f"poly rem_n = reduce(z^{n} - 1, std(sigma));",
    ]

    # Build cert + div equations as ideal in (rho, p_i)
    # Then groebner over Q.
    full = []
    for d in range(k, t):
        full.append(f"coeffs(h, z)[{d+1}, 1]")
    div_coefs = [f"coeffs(rem_n, z)[{d+1}, 1]" for d in range(t)]
    eq_list = full + div_coefs
    eqs_str = ", ".join(eq_list)

    script_parts.extend([
        f"poly rem_n = reduce(z^{n} - 1, std(sigma));",
        f"ideal I = {eqs_str};",
        # Eliminate p_i's, leave rho.
        f"option(redSB);",
        f"ideal J = std(I);",
        # Restrict to rho only:
        f"ring R2 = 0, rho, lp;",
        f"setring R;",
        f"map phi = R2, 0, ..., 0, rho, 0;",
        # Hmm, easier: use eliminate
        f"ideal K = eliminate(J, {' * '.join('p' + str(i) for i in range(t))} * z);",
        f"K;",
        f"$",
    ])
    script = "\n".join(script_parts)
    out, err = run_singular(script, timeout)
    if out is None:
        return None
    return out


# Just enumerate which orbit-16 irreducible cases at (16, 4) need checking
# and use SymPy's GB with larger timeout (Singular setup is complex).

def main():
    n, k = 16, 4
    print(f"Orbit-16 irreducible (gcd(b-a, n) = 1) cases at (n={n}, k={k}):")
    print(f"  These are (a, b) with b - a odd (since 16 = 2^4).")
    print(f"  gcd(a, b, 16) = 1 automatic when b - a odd at deployment.")
    cases = []
    for a in range(k, n - 1):
        for b in range(a + 1, n):
            if (b - a) % 2 == 1:  # b - a odd → gcd(b-a, 16) = 1
                if ggcd(ggcd(a, b), n) == 1:  # also gcd(a, b, n) = 1 for irreducibility
                    cases.append((a, b))
    print(f"  Total: {len(cases)} cases")
    for ab in cases:
        print(f"    {ab}")


if __name__ == "__main__":
    main()
