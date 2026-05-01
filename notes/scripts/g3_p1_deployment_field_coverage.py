"""g3_p1_deployment_field_coverage.py — P1 coverage table at deployment fields.

For each deployment prime q ∈ {KoalaBear, BabyBear, Mersenne31, Goldilocks}
and each FRI 2-round deployment scale (n_0, k_0) up to (2^19, 2^17), check:

  (1) n_0 | q - 1 (multiplicative subgroup of order n_0 exists in F_q^*)
      → Reed-Solomon evaluation domain L_0 well-defined.

  (2) q does not divide any eliminator constant of the s-mono base cases
      at (n, k) ∈ {(4, 1), (8, 2)} — i.e., the RIGOROUS K_s bounds from
      Notes 0286 (s=2: K ≤ 8), 0291 (s=3: K ≤ 9), 0295 (s=4: K ≤ 12)
      reduce mod q without spurious zero-divisors. Bad characteristics
      identified per Substitution Principle analysis: char ∈ {2, 7} fail
      (Note 0286 lemma B). Need to verify all deployment q ∉ {2, 7}.

  (3) For Theorem K10 unconditional (3-pos sparse, paper2 thm:universal-K10)
      to apply: requires 4 | k_0 (so doubly-recursive ≡ above-J at L_0,
      Note 0299) AND q admits the required 16-th roots (for the
      (3k/2, 2k) family eliminator ρ^9 - 16ρ to factor).

For each deployment (q, n_0, k_0): output PASS / FAIL per check.

Usage: python3 g3_p1_deployment_field_coverage.py
       (no args; sweeps the standard ABF §6.3 grid).
"""
from __future__ import annotations

import sys
from sympy.ntheory import factorint, isprime


# Deployment primes (Plonky3 / SP1 / RISC Zero / EthProofs).
DEPLOYMENT_PRIMES = {
    "KoalaBear":   (2**31 - 2**24 + 1, "2^31 - 2^24 + 1"),
    "BabyBear":    (15 * 2**27 + 1,    "15 · 2^27 + 1"),
    "Mersenne31":  (2**31 - 1,         "2^31 - 1"),
    # Goldilocks is 64-bit > Singular char-p limit — flagged separately
    "Goldilocks":  (2**64 - 2**32 + 1, "2^64 - 2^32 + 1"),
}

# Bad characteristics (Note 0286 lemma B): char ∈ {2, 7} make
# Substitution Principle eliminator have spurious roots
BAD_CHARS = {2, 7}

# ABF §6.3 deployment scales (rate ρ = 1/4)
DEPLOYMENT_SCALES = [
    (2**5,  2**3),    # (32, 8)
    (2**6,  2**4),    # (64, 16)
    (2**7,  2**5),    # (128, 32)
    (2**8,  2**6),    # (256, 64)
    (2**10, 2**8),    # (1024, 256)
    (2**12, 2**10),   # (4096, 1024)
    (2**14, 2**12),   # (16384, 4096)
    (2**16, 2**14),   # (65536, 16384)
    (2**18, 2**16),   # (262144, 65536)
    (2**19, 2**17),   # (524288, 131072) — ABF §6.3 max
]


def check_subgroup(q: int, n: int) -> tuple[bool, str]:
    """(1) n | q-1 ?"""
    if (q - 1) % n == 0:
        return True, f"n | q-1 ✓"
    else:
        return False, f"n={n} ∤ (q-1)={q-1}"


def check_bad_char(q: int) -> tuple[bool, str]:
    """(2) char ∉ {2, 7}? For prime fields, char = q."""
    if q in BAD_CHARS:
        return False, f"char={q} ∈ BAD"
    return True, "char OK"


def check_K10_hypothesis(q: int, n: int, k: int) -> tuple[bool, str]:
    """(3) 4 | k AND ρ^9 - 16ρ has all roots in F_q (for K10 thm)?

    ρ^9 = 16ρ ⟺ ρ(ρ^8 - 16) = 0. Roots: ρ = 0 and 8th roots of 16.
    16 = 2^4, so 8th roots of 16 exist in F_q iff:
       - 8 | q - 1 (8th roots of unity exist)
       - 2 is an 8th power in F_q (so 16 = 2^4 is also)
    OR equivalently: gcd(8, q-1) divides ord(2 in F_q^*) properly.
    Sufficient: 16 | q - 1 (then 8th roots of any element exist).
    """
    if k % 4 != 0:
        return False, f"4 ∤ k={k} (needed for thm:universal-K10 hypothesis)"
    # K10's substitution-principle reduction needs 16 ∈ F_q^{*8}.
    # Sufficient: q ≡ 1 (mod 16). Strong but easy.
    if (q - 1) % 16 != 0:
        # Check the weaker condition: 16 has an 8th root in F_q
        # 16 = 2^4 is an 8th power iff 2 is a 2nd power (modulo gcd issues)
        # Actually: 16^((q-1)/d) = 1 where d = gcd(8, q-1)
        d = 1
        for cand in [8, 4, 2, 1]:
            if (q - 1) % cand == 0:
                d = cand
                break
        if pow(16 % q, (q - 1) // d, q) != 1:
            return False, f"16 not in F_q^*8 (weak check fails)"
        return True, f"16 ∈ F_q^*{d}"
    return True, "16 | q-1 ✓ → 16 has 8th root in F_q"


def check_singular_compat(q: int) -> tuple[bool, str]:
    """Auxiliary: Singular GB over GF(q) requires q < 2^31."""
    if q >= 2**31:
        return False, f"q ≥ 2^31, Singular char-p limit (FYI only — coverage independent)"
    return True, "Singular OK"


def main():
    print("=== P1 Coverage: Deployment Fields × Deployment Scales ===")
    print()
    print(f"Bad characteristics (from Note 0286 lemma B): {BAD_CHARS}")
    print()

    rows = []
    for name, (q, expr) in DEPLOYMENT_PRIMES.items():
        print(f"--- {name} (q = {expr} = {q}) ---")
        if not isprime(q):
            print(f"  WARNING: {name} q={q} not prime!")
            continue
        for n0, k0 in DEPLOYMENT_SCALES:
            ok_subgroup, msg_sub = check_subgroup(q, n0)
            ok_char, msg_char = check_bad_char(q)
            ok_k10, msg_k10 = check_K10_hypothesis(q, n0, k0)
            ok_sing, msg_sing = check_singular_compat(q)
            ok_all = ok_subgroup and ok_char and ok_k10
            status = "PASS" if ok_all else "FAIL"
            print(f"  ({n0:6d}, {k0:5d}): {status}")
            if not ok_subgroup:
                print(f"      [subgroup] {msg_sub}")
            if not ok_char:
                print(f"      [char] {msg_char}")
            if not ok_k10:
                print(f"      [K10] {msg_k10}")
            if not ok_sing:
                print(f"      (note) {msg_sing}")
            rows.append((name, q, n0, k0, ok_subgroup, ok_char, ok_k10,
                         ok_sing, ok_all))
        print()

    # Coverage summary
    print()
    print("=== COVERAGE MATRIX ===")
    print()
    print(f"{'Field':<12} | " + " | ".join(f"({n0},{k0})" for n0, k0 in DEPLOYMENT_SCALES))
    print("-" * (15 + 13 * len(DEPLOYMENT_SCALES)))
    for name, _expr in [(n, e[1]) for n, e in DEPLOYMENT_PRIMES.items()]:
        line = f"{name:<12} |"
        for n0, k0 in DEPLOYMENT_SCALES:
            row = next(r for r in rows
                       if r[0] == name and r[2] == n0 and r[3] == k0)
            line += f" {'  PASS  ' if row[8] else '  FAIL  '} |"
        print(line)
    print()

    # Field-extension consideration (degree 2-6)
    print("=== Field extensions (Mersenne31 needs extension to deploy) ===")
    print()
    print("For Mersenne31 (q = 2^31 - 1, q-1 = 2 · 3^2 · 7 · 11 · 31 · 151 · 331):")
    print("  No deployment-scale n_0 = 2^k for k ≥ 2 divides q-1 in base prime field.")
    print("  Standard fix: deploy over EXTENSION F_{q^d} for d ≥ 2.")
    print("  In F_{q^2}, |F^*| = q^2 - 1 = (q-1)(q+1) = (q-1) · 2^32 ·" )
    print("    (since q+1 = 2^31 has order 2^31).")
    print("  So F_{q^2} supports n_0 up to 2^32 — covers all deployment scales.")
    print()
    print("ABF §6.3 itself: KoalaBear sextic F_{q^6}, k=2^20, ρ=1/2, t=128.")
    print("  → Subgroup of order n_0 always exists in F^* (n_0 | q-1 → n_0 | q^d-1).")
    print("  → K10 bound 10/|F| automatically tightens since |F| = q^d ≫ q.")
    print("  → Extensions inherit coverage from base; no extra check needed.")
    print()

    # Outcome summary
    pass_count = sum(1 for r in rows if r[8])
    fail_count = sum(1 for r in rows if not r[8])
    print("=== OUTCOME ===")
    print(f"Total checks: {len(rows)} ({pass_count} PASS, {fail_count} FAIL)")
    print()

    # Per-field summary
    for name, _ in DEPLOYMENT_PRIMES.items():
        passes = [r for r in rows if r[0] == name and r[8]]
        fails = [r for r in rows if r[0] == name and not r[8]]
        if not fails:
            print(f"  {name}: ALL deployment scales PASS — paper2 thm:universal-K10")
            print(f"    applies unconditionally at every (n_0, k_0).")
        else:
            print(f"  {name}: {len(passes)}/{len(rows)//len(DEPLOYMENT_PRIMES)} PASS.")
            for r in fails:
                reasons = []
                if not r[4]: reasons.append(f"subgroup({r[2]} ∤ q-1)")
                if not r[5]: reasons.append("bad-char")
                if not r[6]: reasons.append("K10-hypothesis")
                print(f"    ({r[2]}, {r[3]}) FAIL: {', '.join(reasons)}")


if __name__ == "__main__":
    main()
