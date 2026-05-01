"""g3_stage2_bad_chars.py — extract "bad characteristic" content of Stage 2 GB.

For each h, run modular GB at small primes and detect failure patterns.
This identifies which characteristics (if any) the off-block annihilation
proof has "artifact" obstructions in (vs the real {2, 3} structural ones).
"""
import sympy as sp
import sys

sys.path.insert(0, "notes/scripts")
from g3_stage2_h4_numeric import stage2_eqs


def test_modular(h, primes=None):
    if primes is None:
        primes = [5, 7, 11, 13, 17, 19, 23, 29, 31]
    print(f"\n=== h={h} modular Stage 2 GB ===")
    eqs, p_low_syms, p_high_syms, rho_sym, eps_sym = stage2_eqs(h)
    print(f"  {len(eqs)} eqs over Q[rho, eps, p_low, p_high].")

    e_v = sp.Symbol("e_v")
    p_vars = list(p_low_syms) + list(p_high_syms)

    for p in primes:
        # Substitute rho = small generic value, eps = symbol, work mod p.
        for rho_val in [2, 3, 5]:
            if rho_val % p == 0:
                continue
            subs = {rho_sym: rho_val, eps_sym: e_v}
            eqs_sub = [sp.expand(e.subs(subs)) for e in eqs]
            eqs_sub = [e for e in eqs_sub if e != 0]

            try:
                # Modular GB: use sympy's domain=GF(p)
                G = sp.groebner(
                    eqs_sub,
                    *p_vars,
                    e_v,
                    order="lex",
                    domain=sp.GF(p),
                )
            except Exception as exc:
                print(f"  char={p}, rho={rho_val}: GB failed ({exc})")
                continue
            zeroed = []
            for sym in p_vars:
                rem = G.reduce(sym)[1]
                zeroed.append(rem == 0)
            status = "OK" if all(zeroed) else "FAIL"
            print(f"  char={p}, rho={rho_val}: GB has {len(G)} polys, all p_vars → 0: {all(zeroed)} [{status}]")
            break  # one rho_val per prime


def main():
    for h in [2, 3, 4]:
        test_modular(h)


if __name__ == "__main__":
    main()
