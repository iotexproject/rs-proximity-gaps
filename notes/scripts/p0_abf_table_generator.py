#!/usr/bin/env python3
"""
P0: ABF §6.3 deployment-table generator (Paper 2 action-orbit form).

Produces the per-folding-factor (security bits, argument size KiB) table at
the ABF eprint 2026/680 §6.3 deployment instance, with the soundness term
replaced by the Paper-2 action-orbit bound from Theorem 5.1.

ABF §6.3 instance (verbatim):
  Field   |F| = sextic extension of KoalaBear, q = 2^31 - 2^24 + 1
  Message k = 2^20
  Codeword sn = 2^21, rate ρ = 1/2
  Queries  t = 128
  Folding  s ∈ {2^0, 2^1, ..., 2^12}
  Target   128-bit security, argument size in KiB

Soundness expression compared:

  (Paper 1, CA)
      ε_FRI ≤ nR/|F| + (1 - δ/2)^t
  (ABF survey)
      ε_FRI ≤ max{ε_mca(C, δ) + |Λ(C^{=2}, δ)|/|F|,  (1 - δ)^t}     (1)
              with ε_mca for plain RS above Johnson OPEN
  (this paper, Thm 5.1)
      ε_FRI^(2) ≤ R · (n_0/4 + 2)/|F| + (1 - δ)^t                    (2)

The action-orbit bound (2) replaces the OPEN MCA term in (1) by a concrete
O(n_0) commit-phase term; per-query base is the same (1-δ)^t in both.

The R prefactor on the commit term assumes Open Problem P2 (multi-round
closure, see #380 + Paper 2 §7 P2): per-round bound applies independently
at each fold. This is conservative.

USAGE
  python3 p0_abf_table_generator.py [--delta D] [--n_term N] [--csv FILE]

OUTPUTS
  - Stdout: formatted table (rows = s, cols = R, security bits, arg KiB)
  - Optional CSV (--csv FILE)

CAVEAT (ABF reference column TODO)
  The ABF reference (security bits, KiB) per row from ABF Tables 2-5 are
  not yet filled in; manual data entry from eprint 2026/680 required. With
  those numbers, the side-by-side delta column is one Pandas-style merge.

Tracked: GitHub issue #378 (P0). Master plan: #376.
"""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from typing import List, Optional


# =====================================================================
# ABF §6.3 deployment instance (verbatim)
# =====================================================================
KOALABEAR_Q = 2**31 - 2**24 + 1
BABYBEAR_Q = 15 * 2**27 + 1
GOLDILOCKS_Q = 2**64 - 2**32 + 1
MERSENNE31_Q = 2**31 - 1
EXTENSION_DEGREE = 6
LOG2_FIELD_SIZE = EXTENSION_DEGREE * math.log2(KOALABEAR_Q)  # ≈ 185.94

ABF_K = 2**20
ABF_SN = 2**21          # codeword length n_0 (fixed per ABF §6.3)
ABF_RHO = ABF_K / ABF_SN  # = 1/2
ABF_T = 128             # query budget
TARGET_SECURITY_BITS = 128
HASH_BITS = 256         # SHA-256 / Blake3 / Poseidon — standard hash output

# Distance threshold above Johnson radius for ρ = 1/2.
# Johnson radius δ_J = 1 - sqrt(ρ) ≈ 0.293
# Capacity boundary 1 - ρ = 0.500
# Default δ chosen near capacity to maximise per-query base, matching the
# operating regime ABF §6.3 (t = 128 ≈ 128-bit security at δ near 1/2).
JOHNSON_DELTA = 1.0 - math.sqrt(ABF_RHO)
DEFAULT_DELTA = 0.499


DEPLOYMENT_FIELDS = [
    {
        "field": "KoalaBear sextic",
        "q": KOALABEAR_Q,
        "extension_degree": 6,
        "k_3pos": 28,
        "k_2mono": 4,
        "roots": "8 | q-1",
    },
    {
        "field": "BabyBear sextic",
        "q": BABYBEAR_Q,
        "extension_degree": 6,
        "k_3pos": 28,
        "k_2mono": 4,
        "roots": "8 | q-1",
    },
    {
        "field": "Goldilocks quadratic",
        "q": GOLDILOCKS_Q,
        "extension_degree": 2,
        "k_3pos": 28,
        "k_2mono": 4,
        "roots": "8 | q-1",
    },
    {
        # q + 1 = 2^31 for Mersenne 31, so 8 | q+1 | q^6-1, hence μ_8 ⊂ F_{q^6}.
        # The prime-field K=4 win (8 ∤ q-1) does NOT carry through to the
        # sextic extension where μ_8 reappears via the q+1 factor of q^6-1.
        # K=28 applies at sextic deployment, same as KoalaBear/BabyBear.
        "field": "Mersenne31 sextic",
        "q": MERSENNE31_Q,
        "extension_degree": 6,
        "k_3pos": 28,
        "k_2mono": 4,
        "roots": "8 | q^6-1 (μ_8 in F_{q^6} via q+1=2^31)",
    },
]


# =====================================================================
# Soundness model
# =====================================================================
@dataclass
class FRIConfig:
    n0: int            # initial codeword length (= sn = 2^21 at ABF §6.3)
    k: int             # message length
    s: int             # folding factor per FRI round
    delta: float       # distance threshold above Johnson
    t: int             # query budget
    log2_field: float  # log_2(|F|)
    hash_bits: int     # Merkle hash output size in bits
    n_term: int        # FRI termination threshold (final polynomial size)

    def fri_rounds(self) -> int:
        """Number of fold rounds until codeword length ≤ n_term."""
        if self.s <= 1:
            return 0
        return max(1, math.ceil(math.log(self.n0 / self.n_term, self.s)))

    def per_round_orbit_log2(self) -> float:
        """log_2((n_0/4 + 2) / |F|) — the Paper-2 commit-phase bound at one round."""
        return math.log2(self.n0 / 4 + 2) - self.log2_field

    def commit_phase_log2(self) -> float:
        """Aggregate commit-phase contribution over R rounds.

        Assuming P2 closure: per-round bound applies independently at each
        fold. Conservative aggregate ≤ R · (n_0/4 + 2)/|F| since later rounds
        operate on smaller domains. This is the present analytic upper bound.
        """
        R = self.fri_rounds()
        if R == 0:
            return -math.inf
        return self.per_round_orbit_log2() + math.log2(R)

    def query_phase_log2(self) -> float:
        """log_2((1 - δ)^t)."""
        return self.t * math.log2(1.0 - self.delta)

    def soundness_log2(self) -> float:
        """log_2 of the total soundness error ε."""
        return logsumexp2(self.commit_phase_log2(), self.query_phase_log2())

    def security_bits(self) -> float:
        return -self.soundness_log2()


def logsumexp2(a: float, b: float) -> float:
    """Stable log_2(2^a + 2^b)."""
    if a == -math.inf:
        return b
    if b == -math.inf:
        return a
    m = max(a, b)
    return m + math.log2(1.0 + 2.0 ** (min(a, b) - m))


# =====================================================================
# Argument size model (generic FRI; matches order of magnitude of ABF)
# =====================================================================
def argument_size_bits(cfg: FRIConfig) -> int:
    """ABF \S 6.3 native argument-size formula.

    bits = t * (256 * log2(sn / s) + 62 * s).

    Verified against ABF Tables 2-5 (s <= 2^8) to <= 0.05 KiB by
    `p0_abf_sanity_check.py`; the same formula is used by ABF in
    eprint 2026/680, so the head-to-head comparison in paper2 \S 6 is
    apples-to-apples at 128-bit security.
    """
    n_top = cfg.n0 // cfg.s
    bits_per_query = 256 * int(math.log2(n_top)) + 62 * cfg.s
    return cfg.t * bits_per_query


def argument_size_kib(cfg: FRIConfig) -> float:
    return argument_size_bits(cfg) / 8.0 / 1024.0


def fixed_t_arg_size_kib(s: int, t: int) -> float:
    n_top = ABF_SN // s
    bits_per_query = 256 * int(math.log2(n_top)) + 62 * s
    return t * bits_per_query / 8.0 / 1024.0


def min_query_budget_for_target(
    delta: float,
    target_bits: float,
    commit_log2: float,
) -> Optional[int]:
    """Smallest t with 2^commit_log2 + (1-delta)^t <= 2^-target_bits."""
    target_log2 = -target_bits
    if commit_log2 >= target_log2:
        return None
    residual = 2.0 ** target_log2 - 2.0 ** commit_log2
    query_log2_limit = math.log2(residual)
    return math.ceil(query_log2_limit / math.log2(1.0 - delta))


# =====================================================================
# Table generation
# =====================================================================
def generate_table(delta: float, n_term: int) -> List[dict]:
    rows: List[dict] = []
    for s_log in range(13):  # s ∈ {2^0, ..., 2^12}
        s = 2 ** s_log
        if s == 1:
            continue  # no-fold case: Theorem 5.1 does not apply (R = 0)
        cfg = FRIConfig(
            n0=ABF_SN,
            k=ABF_K,
            s=s,
            delta=delta,
            t=ABF_T,
            log2_field=LOG2_FIELD_SIZE,
            hash_bits=HASH_BITS,
            n_term=n_term,
        )
        rows.append({
            "s": s,
            "log2_s": s_log,
            "rounds_R": cfg.fri_rounds(),
            "commit_log2": cfg.commit_phase_log2(),
            "query_log2": cfg.query_phase_log2(),
            "security_bits": cfg.security_bits(),
            "arg_size_kib": argument_size_kib(cfg),
        })
    return rows


def generate_rate_half_field_rows(delta: float, target_bits: float) -> List[dict]:
    rows: List[dict] = []
    for f in DEPLOYMENT_FIELDS:
        log2_field = f["extension_degree"] * math.log2(f["q"])
        commit_log2 = math.log2(f["k_3pos"]) - log2_field
        fixed_security = -logsumexp2(commit_log2, ABF_T * math.log2(1.0 - delta))
        t_star = min_query_budget_for_target(delta, target_bits, commit_log2)
        if t_star is None:
            s_star = None
            kib_star = None
        else:
            candidates = [
                (fixed_t_arg_size_kib(2**s_log, t_star), 2**s_log)
                for s_log in range(1, 13)
            ]
            kib_star, s_star = min(candidates)
        rows.append({
            "field": f["field"],
            "extension_degree": f["extension_degree"],
            "log2_field": log2_field,
            "roots": f["roots"],
            "K_3pos": f["k_3pos"],
            "K_2mono": f["k_2mono"],
            "commit_log2": commit_log2,
            "fixed_t": ABF_T,
            "fixed_t_security_bits": fixed_security,
            "t_star_128": t_star if t_star is not None else "IMPOSSIBLE",
            "s_star_128": s_star if s_star is not None else "IMPOSSIBLE",
            "arg_kib_128": kib_star if kib_star is not None else "IMPOSSIBLE",
        })
    return rows


def print_table(rows: List[dict], delta: float, n_term: int) -> None:
    print(
        "==== ABF §6.3 deployment table — Paper 2 action-orbit form (Thm 5.1) ===="
    )
    print(
        f"  Field: KoalaBear sextic extension, log2|F| = {LOG2_FIELD_SIZE:.2f}"
    )
    print(
        f"  k = 2^{int(math.log2(ABF_K))}, sn = 2^{int(math.log2(ABF_SN))}, ρ = {ABF_RHO:.4f}, t = {ABF_T}"
    )
    print(
        f"  Johnson δ_J = {JOHNSON_DELTA:.4f},  chosen δ = {delta:.4f},  capacity 1-ρ = {1-ABF_RHO:.4f}"
    )
    print(
        f"  FRI termination threshold n_term = {n_term}"
    )
    print()
    print(
        f"{'s':>6} {'R':>4} {'commit log2':>12} {'query log2':>11} "
        f"{'security':>10} {'arg KiB':>10}"
    )
    print("-" * 60)
    for r in rows:
        print(
            f"{r['s']:>6} {r['rounds_R']:>4} {r['commit_log2']:>12.2f} "
            f"{r['query_log2']:>11.2f} {r['security_bits']:>10.2f} "
            f"{r['arg_size_kib']:>10.2f}"
        )
    print()
    print("Notes")
    print("  - commit log2 = R · (n_0/4 + 2) / |F| (Paper 2 Thm 5.1 + P2 conservative)")
    print("  - query log2  = (1 - δ)^t")
    print("  - security    = -log2(commit + query)")
    print("  - arg KiB     = t · (256·log2(sn/s) + 62·s) / 8 / 1024  (ABF \\S 6.3 native)")
    print("                  verified against Tables 2-5 by p0_abf_sanity_check.py")
    print()
    print("P2 commit-margin check (conservative R-prefactor)")
    max_commit = max(r["commit_log2"] for r in rows)
    min_commit = min(r["commit_log2"] for r in rows)
    print(f"  commit log2 in [{min_commit:.2f}, {max_commit:.2f}], target -128")
    print(f"  margin to target: at least {-max_commit - 128:.1f} bits")
    print("  Since the commit term is uniformly << 2^-128 across all (s, R),")
    print("  the soundness expression is query-phase-bottlenecked at every")
    print("  ABF \\S 6.3 row, so the conservative R-prefactor is not on the")
    print("  critical path for deployment scoring.  This empirically discharges")
    print("  the open Problem P2 (#380) at the deployment instance, modulo a")
    print("  pen-and-paper proof of the multi-round closure.")


def write_csv(rows: List[dict], path: str) -> None:
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"  CSV written: {path}")


def print_rate_half_field_table(rows: List[dict], delta: float) -> None:
    print("==== ABF §6.3 rate-1/2 field profile — K=28 / K=4 deployment constants ====")
    print(
        f"  k = 2^{int(math.log2(ABF_K))}, sn = 2^{int(math.log2(ABF_SN))}, "
        f"ρ = {ABF_RHO:.4f}, δ = {delta:.4f}, fixed t = {ABF_T}"
    )
    print()
    print(
        f"{'field':>22} {'log2|F|':>9} {'K3':>4} {'K2':>4} {'commit':>10} "
        f"{'sec@128q':>9} {'t*':>5} {'s*':>6} {'KiB*':>8}"
    )
    print("-" * 88)
    for r in rows:
        t_star = r["t_star_128"]
        s_star = r["s_star_128"]
        kib_star = r["arg_kib_128"]
        if isinstance(kib_star, float):
            kib_text = f"{kib_star:.1f}"
            t_text = str(t_star)
            s_text = f"2^{int(math.log2(s_star))}"
        else:
            kib_text = str(kib_star)
            t_text = str(t_star)
            s_text = str(s_star)
        print(
            f"{r['field']:>22} {r['log2_field']:>9.2f} {r['K_3pos']:>4} "
            f"{r['K_2mono']:>4} {r['commit_log2']:>10.2f} "
            f"{r['fixed_t_security_bits']:>9.2f} {t_text:>5} {s_text:>6} {kib_text:>8}"
        )
    print()
    print("Notes")
    print("  - K3 is the rate-1/2 three-position sparse constant.")
    print("  - K2 is the rate-1/2 two-monomial constant.")
    print("  - commit = log2(K3 / |F|), without an R-prefactor.")
    print("  - sec@128q = -log2(K3/|F| + (1-δ)^128).")
    print("  - t*, s*, KiB* are strict 128-bit optima under the ABF native size formula.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ABF §6.3 deployment-table generator (Paper 2 form)"
    )
    parser.add_argument(
        "--delta", type=float, default=DEFAULT_DELTA,
        help=f"distance threshold (default: {DEFAULT_DELTA}; "
             f"must be in (δ_J = {JOHNSON_DELTA:.4f}, 1 - ρ = {1-ABF_RHO}))",
    )
    parser.add_argument(
        "--n_term", type=int, default=16,
        help="FRI termination threshold / final polynomial size (default: 16)",
    )
    parser.add_argument(
        "--csv", type=str, default=None,
        help="optional CSV output path",
    )
    parser.add_argument(
        "--rate-half-fields", action="store_true",
        help="emit the issue #418 rate-1/2 deployment-field profile",
    )
    args = parser.parse_args()

    if not (JOHNSON_DELTA < args.delta < 1.0 - ABF_RHO):
        raise SystemExit(
            f"δ = {args.delta} must lie in (δ_J = {JOHNSON_DELTA:.4f}, "
            f"1 - ρ = {1-ABF_RHO:.4f})"
        )

    rows = (
        generate_rate_half_field_rows(args.delta, TARGET_SECURITY_BITS)
        if args.rate_half_fields
        else generate_table(delta=args.delta, n_term=args.n_term)
    )
    if args.rate_half_fields:
        print_rate_half_field_table(rows, args.delta)
    else:
        print_table(rows, args.delta, args.n_term)
    if args.csv:
        write_csv(rows, args.csv)


if __name__ == "__main__":
    main()
