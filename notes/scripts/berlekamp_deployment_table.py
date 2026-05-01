#!/usr/bin/env python3
"""Berlekamp #322 deployment-grade ε table — D0 + D2 (Note 0115).

Computes the conjectural codim V_bad (Note 0114 sub-tet upper-bound,
empirically tight per Notes 0103/0114) at Ethereum FRI deployment params,
and the resulting per-round ε bound. Subject to Conjecture C
(codim V_bad ≈ 2(D - w'_min - 1)) — see Note 0115.

D0: produces the table.
D2: includes a `sub_tet?` column flagging rows where the sub-tet route
    is empty (w'_min > T); for those rows the conjecture above doesn't
    directly apply and another route must dominate.

ε per round (commit-side, Berlekamp/RS-proximity contribution):
   ε ≤ poly(n_0) · q^{-codim}     [conjectural]
We report -log2(ε) ignoring the poly factor (a few bits at most).
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Field:
    name: str
    q_bits: float    # log2(q) of base field
    ext_deg: int     # extension degree

    @property
    def F_bits(self) -> float:
        return self.q_bits * self.ext_deg


# Ethereum FRI deployment fields (see Issue #376 §2)
FIELDS = [
    Field("KoalaBear",      math.log2(2**31 - 2**24 + 1), 1),
    Field("KoalaBear-ext6", math.log2(2**31 - 2**24 + 1), 6),  # ABF §6.3 baseline
    Field("BabyBear",       math.log2(2**31 - 2**27 + 1), 1),
    Field("BabyBear-ext4",  math.log2(2**31 - 2**27 + 1), 4),
    Field("Mersenne31",     math.log2(2**31 - 1),          1),
    Field("Mersenne31-ext4",math.log2(2**31 - 1),          4),
    Field("Goldilocks",     math.log2(2**64 - 2**32 + 1), 1),
    Field("Goldilocks-ext2",math.log2(2**64 - 2**32 + 1), 2),
]


def w_prime_min(w: int, c: int) -> int:
    """Smallest w' for which sub-tet route is bad-realizing (Note 0110)."""
    return math.ceil((2 * w + c - 1) / (c + 1))


def T_max_bad(D: int, c: int) -> int:
    return (2 * D - 1) // c


def sub_tet_exists(D: int, c: int) -> tuple[bool, int, int]:
    w = D - c
    wpm = w_prime_min(w, c)
    T = T_max_bad(D, c)
    return wpm <= T, wpm, T


def codim_conj_optimistic(D: int, c: int) -> tuple[int | None, int, int]:
    """Optimistic codim V_bad = 2(D - w'_min - 1) [Note 0114, distinct extras case]."""
    exists, wpm, T = sub_tet_exists(D, c)
    if not exists:
        return None, wpm, T
    return 2 * (D - wpm - 1), wpm, T


def codim_worst_case(D: int, c: int) -> int:
    """Worst-case codim V_bad ≤ 2(c-1) [Note 0116, shared-U component].

    Holds when w >= T (deployment-scale always). Independent of n.
    """
    return 2 * (c - 1)


def epsilon_bits_per_round(F_bits: float, codim: int) -> float:
    """-log2(ε_per_round) ≈ codim · log2(q^ext) (poly factor ignored)."""
    return codim * F_bits


def feasibility_label(eps_bits: float, target_bits: int) -> str:
    if eps_bits >= target_bits:
        return f"OK ({eps_bits:.0f}b)"
    else:
        return f"FAIL ({eps_bits:.0f}b)"


def sweep(target_bits: int = 128) -> list[dict]:
    rows = []
    n_logs = [10, 12, 14, 16, 18, 20, 21]   # n_0 = 2^log
    rates = [(1, 2), (1, 4), (1, 8)]         # ρ = num/den
    cs = [3, 4, 6, 9]
    for field in FIELDS:
        for n_log in n_logs:
            n0 = 1 << n_log
            for num, den in rates:
                k0 = n0 * num // den
                D = n0 - k0
                rho = num / den
                for c in cs:
                    if D <= c + 2:
                        continue
                    codim_opt, wpm, T = codim_conj_optimistic(D, c)
                    codim_worst = codim_worst_case(D, c)
                    if codim_opt is None:
                        # sub-tet empty — flag and skip optimistic ε
                        eps_opt = None
                    else:
                        eps_opt = epsilon_bits_per_round(field.F_bits, codim_opt)
                    eps_worst = epsilon_bits_per_round(field.F_bits, codim_worst)
                    verdict = (feasibility_label(eps_worst, target_bits)
                               + " (worst)")
                    rows.append({
                        'field': field.name,
                        'F_bits': field.F_bits,
                        'n_log2': n_log,
                        'n0': n0,
                        'rho_str': f"1/{den}",
                        'k0': k0, 'D': D, 'c': c,
                        'w': D - c, 'T': T, 'w_min': wpm,
                        'sub_tet': codim_opt is not None,
                        'codim_opt': codim_opt,
                        'codim_worst': codim_worst,
                        'eps_opt': eps_opt,
                        'eps_worst': eps_worst,
                        'verdict': verdict,
                    })
    return rows


def print_table(rows, *, target_bits: int = 128, focus: str | None = None):
    print(f"# Berlekamp #322 deployment ε table (target {target_bits}-bit)\n")
    print("Two codim conjectures:")
    print("  - codim_opt = 2(D - w'_min - 1)  [Note 0114, distinct-extras case]")
    print("  - codim_worst = 2(c - 1)         [Note 0116, shared-extras worst case]")
    print("ε bits = codim · log2(|F|), poly factor ignored.\n")
    if focus:
        rows = [r for r in rows if focus in r['field']]
    headers = ["field", "F_b", "n_log", "ρ", "D", "c", "T", "w'_min",
               "codim_opt", "ε_opt", "codim_w", "ε_worst", "verdict"]
    print("| " + " | ".join(f"{h}" for h in headers) + " |")
    print("|" + "|".join("---" for _ in headers) + "|")
    for r in rows:
        cells = [
            r['field'],
            f"{r['F_bits']:.0f}",
            f"2^{r['n_log2']}",
            r['rho_str'],
            str(r['D']),
            str(r['c']),
            str(r['T']),
            str(r['w_min']),
            str(r['codim_opt']) if r['codim_opt'] is not None else "-",
            f"{r['eps_opt']:.0f}" if r['eps_opt'] is not None else "-",
            str(r['codim_worst']),
            f"{r['eps_worst']:.0f}",
            r['verdict'],
        ]
        print("| " + " | ".join(cells) + " |")


def print_summary(rows, target_bits: int = 128):
    total = len(rows)
    ok_opt = sum(1 for r in rows if r['eps_opt'] is not None
                 and r['eps_opt'] >= target_bits)
    ok_worst = sum(1 for r in rows if r['eps_worst'] >= target_bits)
    sub_empty = sum(1 for r in rows if not r['sub_tet'])
    fail_worst_rows = [r for r in rows if r['eps_worst'] < target_bits]
    print()
    print(f"# Summary at target {target_bits}-bit")
    print(f"  total rows:                          {total}")
    print(f"  OK under optimistic codim (Note 0114): {ok_opt}  ({100*ok_opt/total:.1f}%)")
    print(f"  OK under worst-case codim (Note 0116): {ok_worst}  ({100*ok_worst/total:.1f}%)")
    print(f"  sub-tet empty:                       {sub_empty}")
    if fail_worst_rows:
        print(f"\n# Rows failing under worst-case codim:")
        seen = set()
        for r in fail_worst_rows:
            key = (r['field'], r['c'])
            if key in seen: continue
            seen.add(key)
            print(f"  {r['field']:20s} c={r['c']}: codim_worst={r['codim_worst']}, "
                  f"ε_worst={r['eps_worst']:.0f} bits (target {target_bits})")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--target", type=int, default=128)
    p.add_argument("--field", type=str, default=None,
                   help="Filter to one field name (substring match)")
    p.add_argument("--abf-baseline", action="store_true",
                   help="Show only the ABF §6.3 baseline row "
                        "(KoalaBear-ext6, k=2^20, ρ=1/2, c sweep).")
    args = p.parse_args()
    rows = sweep(target_bits=args.target)
    if args.abf_baseline:
        rows = [r for r in rows if r['field'] == 'KoalaBear-ext6'
                and r['n_log2'] == 21 and r['rho_str'] == '1/2']
    print_table(rows, target_bits=args.target, focus=args.field)
    print_summary(rows, target_bits=args.target)


if __name__ == "__main__":
    main()
