#!/usr/bin/env python3
"""D3 — Berlekamp #322 × FRI 2-round soundness, ABF §6.3 KiB comparison.

Per-row report:
  commit_cap: the asymptotic NI-bit ceiling from commit alone (independent
              of t). If commit_cap < target, the config is commit-bound.
  query_cap : the asymptotic NI-bit ceiling from query alone (depends on t).
  min_t     : smallest t to reach NI target (when commit_cap ≥ target).
  KiB       : ≈ t × (field_bytes + log2(n)·hash_bytes).

OLD model: ε_round_commit ≤ n/|F|     (BCIKS-generic).
NEW model: ε_round_commit ≤ T/|F| + q^{-2(c-1)}·n  (Note 0117/0119);
           T = ⌊(2D-1)/c⌋. The T/|F| term improves by factor c on commit.

So Berlekamp's contribution: commit_cap_new − commit_cap_old = log2(c) bits.
Small but can flip a borderline-commit-bound config feasible.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class Field:
    name: str
    base_q_bits: float
    ext_deg: int
    @property
    def F_bits(self) -> float:
        return self.base_q_bits * self.ext_deg

FIELDS = [
    Field("KoalaBear",       math.log2(2**31 - 2**24 + 1), 1),
    Field("KoalaBear-ext4",  math.log2(2**31 - 2**24 + 1), 4),
    Field("KoalaBear-ext6",  math.log2(2**31 - 2**24 + 1), 6),
    Field("BabyBear",        math.log2(2**31 - 2**27 + 1), 1),
    Field("BabyBear-ext4",   math.log2(2**31 - 2**27 + 1), 4),
    Field("BabyBear-ext7",   math.log2(2**31 - 2**27 + 1), 7),
    Field("Mersenne31",      math.log2(2**31 - 1),          1),
    Field("Mersenne31-ext4", math.log2(2**31 - 1),          4),
    Field("Goldilocks",      math.log2(2**64 - 2**32 + 1), 1),
    Field("Goldilocks-ext2", math.log2(2**64 - 2**32 + 1), 2),
]


def _neglog_sum(*bits: float) -> float:
    finite = [b for b in bits if not math.isinf(b)]
    if not finite: return math.inf
    m = min(finite)
    return m - math.log2(sum(2 ** -(b - m) for b in finite))


# ---------- Per-round commit (-log2 ε_per_round) ----------

def commit_per_round_old(F_bits: float, n: int) -> float:
    return F_bits - math.log2(n)

def commit_per_round_new(F_bits: float, n: int, D: int, c: int) -> float:
    T = max(1, (2 * D - 1) // c)
    log_main = F_bits - math.log2(T)
    log_tail = 2 * (c - 1) * F_bits - math.log2(n)
    return _neglog_sum(log_main, log_tail)


# ---------- Caps (-log2 of total commit / query / binding contribution) ----------

def commit_cap(commit_pr: float, R: int, q_loss: int) -> float:
    return commit_pr - math.log2(R) - q_loss

def query_bits_per_t(delta: float) -> float:
    return math.log2(1.0 / (1.0 - delta / 2.0))

def query_cap(delta: float, t: int, q_loss: int) -> float:
    return t * query_bits_per_t(delta) - q_loss

def binding_cap(kappa: int, q_loss: int) -> float:
    return kappa - 2 * q_loss - math.log2(3.0)

def total_NI(commit_pr: float, R: int, t: int, delta: float,
             q_loss: int, kappa: int) -> float:
    return _neglog_sum(commit_cap(commit_pr, R, q_loss),
                       query_cap(delta, t, q_loss),
                       binding_cap(kappa, q_loss))

def find_min_t(commit_pr: float, R: int, delta: float,
               target: int, q_loss: int, kappa: int) -> int | None:
    cc = commit_cap(commit_pr, R, q_loss)
    bc = binding_cap(kappa, q_loss)
    if min(cc, bc) < target:
        return None
    qpt = query_bits_per_t(delta)
    if qpt <= 0: return None
    t = math.ceil((target + q_loss) / qpt)
    return max(8, t)


# ---------- KiB ----------

def kib_cost(t: int, F_bits: float, n: int) -> float:
    field_bytes = F_bits / 8
    hash_bytes = 32
    merkle_path = math.log2(n) * hash_bytes
    return t * (field_bytes + merkle_path) / 1024


# ---------- Main row generator ----------

def gen_row(field: Field, n_log: int, num: int, den: int, c: int,
            delta: float, target: int, q_loss: int, kappa: int) -> dict:
    n = 1 << n_log
    R = n_log
    k = n * num // den
    D = n - k
    w = D - c
    cpr_old = commit_per_round_old(field.F_bits, n)
    cpr_new = commit_per_round_new(field.F_bits, n, D, c)
    cap_old = commit_cap(cpr_old, R, q_loss)
    cap_new = commit_cap(cpr_new, R, q_loss)
    cap_bind = binding_cap(kappa, q_loss)
    t_old = find_min_t(cpr_old, R, delta, target, q_loss, kappa)
    t_new = find_min_t(cpr_new, R, delta, target, q_loss, kappa)
    return {
        'field': field.name, 'F_bits': field.F_bits, 'n_log': n_log,
        'rho_str': f"1/{den}", 'D': D, 'c': c, 'w': w, 'delta': delta, 'R': R,
        'cap_old': cap_old, 'cap_new': cap_new, 'cap_bind': cap_bind,
        't_old': t_old, 't_new': t_new,
        'kib_old': kib_cost(t_old, field.F_bits, n) if t_old else None,
        'kib_new': kib_cost(t_new, field.F_bits, n) if t_new else None,
    }


def sweep(target: int, q_loss: int, kappa: int, delta: float,
          n_logs=(20, 21), rates=((1, 2),), cs=(3, 4, 6, 9)) -> list[dict]:
    rows = []
    for field in FIELDS:
        for n_log in n_logs:
            for num, den in rates:
                k = (1 << n_log) * num // den
                D = (1 << n_log) - k
                for c in cs:
                    if D <= c + 2: continue
                    if delta >= (D - c) / (1 << n_log):
                        continue
                    rows.append(gen_row(field, n_log, num, den, c,
                                        delta, target, q_loss, kappa))
    return rows


def print_table(rows, *, target: int):
    print(f"# D3 NI {target}-bit, KoalaBear-ext6 etc. — Berlekamp commit gain")
    print("OLD: commit ≤ n/|F| (BCIKS-generic, c-independent).")
    print("NEW: commit ≤ T/|F| + q^{-2(c-1)}·n (Note 0117/0119).  Δgain = log2(c).\n")
    headers = ["field", "F_b", "n_log", "ρ", "c",
               "cap_old", "cap_new", "Δcap",
               "t_old", "t_new", "KiB_old", "KiB_new"]
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join("---" for _ in headers) + "|")
    for r in rows:
        d = r['cap_new'] - r['cap_old']
        cells = [
            r['field'], f"{r['F_bits']:.0f}", f"2^{r['n_log']}",
            r['rho_str'], str(r['c']),
            f"{r['cap_old']:.1f}", f"{r['cap_new']:.1f}", f"{d:+.2f}",
            str(r['t_old']) if r['t_old'] else "—",
            str(r['t_new']) if r['t_new'] else "—",
            f"{r['kib_old']:.1f}" if r['kib_old'] else "—",
            f"{r['kib_new']:.1f}" if r['kib_new'] else "—",
        ]
        print("| " + " | ".join(cells) + " |")


def print_summary(rows, target: int):
    if not rows:
        print("\n# (no rows)"); return
    feas_old = [r for r in rows if r['t_old'] is not None]
    feas_new = [r for r in rows if r['t_new'] is not None]
    flip = [r for r in rows if r['t_new'] and not r['t_old']]
    print()
    print(f"# Summary at NI {target}-bit (q_loss=64, κ=384, δ given per row)")
    print(f"  total rows: {len(rows)}")
    print(f"  feasible OLD: {len(feas_old)}")
    print(f"  feasible NEW: {len(feas_new)}")
    print(f"  flipped infeasible→feasible by Berlekamp: {len(flip)}")
    if flip:
        print("  flipped:")
        for r in flip:
            print(f"    {r['field']:18s} n=2^{r['n_log']} ρ={r['rho_str']} c={r['c']}: "
                  f"cap_old={r['cap_old']:.1f} → cap_new={r['cap_new']:.1f}, "
                  f"t_new={r['t_new']}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--target", type=int, default=128)
    p.add_argument("--q-loss", type=int, default=64)
    p.add_argument("--kappa", type=int, default=384)
    p.add_argument("--delta", type=float, default=0.40)
    p.add_argument("--field", type=str, default=None)
    p.add_argument("--cs", type=str, default="3,4,6,9")
    args = p.parse_args()
    cs = tuple(int(x) for x in args.cs.split(","))
    rows = sweep(args.target, args.q_loss, args.kappa, args.delta, cs=cs)
    if args.field:
        rows = [r for r in rows if args.field in r['field']]
    print_table(rows, target=args.target)
    print_summary(rows, args.target)


if __name__ == '__main__':
    main()
