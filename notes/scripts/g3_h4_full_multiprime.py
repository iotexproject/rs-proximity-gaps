"""g3_h4_full_multiprime.py — verify FULL Stage 2 system at h=4 across multiple primes,
including primes where 6 is a QR (which the y^5-only system incorrectly admitted).

Approach: for each p ≡ 1 mod 8, find rho_val with rho_val^8 ≡ 16 mod p, build full
system with eps = rho_val^4/4, emit Singular script, run.

Output: which (p, rho) pairs produce GB = {a_c, b_c} (all unknowns reduced to 0)
vs which produce non-trivial GB.
"""
import sys
import os
import subprocess
import sympy as sp
from sympy import isprime

sys.path.insert(0, "notes/scripts")
from g3_stage2_full_correct import stage2_system


def find_rho(p):
    """Return list of rho values in F_p with rho^8 = 16 mod p."""
    return [r for r in range(p) if pow(r, 8, p) == 16 % p]


def build_singular(h, p, rho_val):
    eqs, alpha, beta, rho_sym, eps_sym = stage2_system(h)
    eps_val = rho_sym**4 / 4
    # Substitute and mod-out: convert each Poly's coefs to F_p first.
    eqs_sub = []
    a_vars = list(alpha) + list(beta)
    for c, k, e in eqs:
        e1 = sp.expand(e.subs(eps_sym, eps_val).subs(rho_sym, rho_val))
        # Convert to Poly with rational coefs, then reduce coefs mod p
        poly = sp.Poly(e1, *a_vars)
        new_terms = []
        for monom, coef in poly.terms():
            num, den = sp.fraction(sp.Rational(coef))
            den_inv = pow(int(den) % p, p-2, p) if int(den) % p != 0 else 0
            c_mod = (int(num) * den_inv) % p
            if c_mod != 0:
                term_parts = [f"{c_mod}"]
                for v, ex in zip(a_vars, monom):
                    if ex > 0:
                        term_parts.append(f"{v.name}" + (f"^{ex}" if ex > 1 else ""))
                new_terms.append("*".join(term_parts))
        eqs_sub.append((c, k, " + ".join(new_terms) if new_terms else "0"))

    var_list = ", ".join(f"a{c}" for c in range(1, h)) + ", " + ", ".join(f"b{c}" for c in range(1, h))
    out = []
    out.append("short=0;")
    out.append("printlevel=0;")
    out.append("option(redSB);")
    out.append("option(redTail);")
    out.append(f"ring R = {p}, ({var_list}), dp;")
    out.append("ideal I =")
    eq_strs = [s for c, k, s in eqs_sub]
    out.append(",\n".join("  " + s for s in eq_strs) + ";")
    out.append("ideal G = groebner(I);")
    out.append('print("GB-SIZE:");')
    out.append("print(size(G));")
    out.append('print("GB-CONTENT:");')
    out.append("print(G);")
    out.append("quit;")
    return "\n".join(out)


def main():
    h = 4
    # Primes ≡ 1 mod 8 in [17, 600] from previous sweep — focus on the p ≡ 1 mod 24 (where 6 is QR)
    target_primes = [73, 97, 193, 241, 313, 337, 409, 433, 457, 577]  # p ≡ 1 mod 24
    print(f"Testing FULL Stage 2 system at h={h} for {len(target_primes)} primes (all p ≡ 1 mod 24)")
    print()
    print(f"{'p':>5} {'rho':>5} {'GB size':>8}  result")
    print("-"*60)

    for p in target_primes:
        rhos = find_rho(p)
        if not rhos:
            print(f"{p:>5} —  no rho with rho^8=16")
            continue
        # Pick the smallest rho > 0
        rho_val = sorted(r for r in rhos if r != 0)[0]
        sing_text = build_singular(h, p, rho_val)
        sing_file = f"/tmp/h4_p{p}_full.sing"
        with open(sing_file, "w") as f:
            f.write(sing_text)
        try:
            res = subprocess.run(
                ["Singular", "-q"],
                stdin=open(sing_file),
                capture_output=True,
                text=True,
                timeout=300,
            )
            output = res.stdout
            # Parse GB size
            lines = output.split("\n")
            gb_size = None
            for i, line in enumerate(lines):
                if "GB-SIZE" in line:
                    gb_size = lines[i+1].strip() if i+1 < len(lines) else "?"
                    break
            # Heuristic: if GB has 6 elements that look like {a1, ..., b3}, it's all-zero.
            content_idx = next((i for i, line in enumerate(lines) if "GB-CONTENT" in line), -1)
            content = lines[content_idx+1:content_idx+8] if content_idx >= 0 else []
            content_str = " ".join(content).strip()
            simple = all(item.strip() in {"a1", "a2", "a3", "b1", "b2", "b3", "a1,", "a2,", "a3,", "b1,", "b2,", "b3,"} for item in content)
            verdict = "ALL ZERO" if (gb_size == "6" and simple) else f"non-trivial: {content_str[:60]}"
            print(f"{p:>5} {rho_val:>5} {gb_size:>8}  {verdict}")
        except Exception as exc:
            print(f"{p:>5} {rho_val:>5}  EXCEPTION: {exc}")


if __name__ == "__main__":
    main()
