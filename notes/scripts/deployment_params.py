#!/usr/bin/env python3
"""Reproduce deployment security tables for the paper.

The script uses the bounds stated in Appendix D:

  interactive:     eps <= nR/|F| + (1 - delta/2)^q
  non-interactive: eps <= Q * eps_interactive + 3(Q^2 + 1)/2^kappa

All arithmetic is done in log2 bits.  The output is intentionally plain text so
it can be pasted into paper.tex or compared in review.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    name: str
    field_bits: float
    n_log2: float
    rounds: int
    delta: float
    q_now: int
    q_bits: int
    kappa: int


CONFIGS = [
    Config("BabyBear base", 31, 20, 20, 0.40, 128, 64, 256),
    Config("BabyBear4", 124, 20, 20, 0.40, 128, 64, 256),
    Config("BabyBear5", 155, 20, 20, 0.40, 128, 64, 256),
    Config("BabyBear7", 217, 20, 20, 0.40, 128, 64, 384),
    Config("Mersenne31-4", 124, 20, 20, 0.40, 128, 64, 256),
    Config("Goldilocks2", 128, 20, 20, 0.40, 128, 64, 256),
    Config("Binary tower 128", 128, 20, 20, 0.40, 128, 64, 256),
]


def neglog2_sum_from_bits(bits: list[float]) -> float:
    """Return -log2(sum_i 2^-bits_i), stably."""
    finite = [b for b in bits if not math.isinf(b)]
    if not finite:
        return math.inf
    m = min(finite)
    return m - math.log2(sum(2 ** (-(b - m)) for b in finite))


def query_bits(delta: float, q: int) -> float:
    return q * math.log2(1.0 / (1.0 - delta / 2.0))


def commit_bits(cfg: Config, *, per_round_max: bool) -> float:
    round_factor = 0.0 if per_round_max else math.log2(cfg.rounds)
    return cfg.field_bits - cfg.n_log2 - round_factor


def binding_bits(q_bits: int, kappa: int) -> float:
    # 3(Q^2 + 1)/2^kappa ~= 2^-(kappa - 2q_bits - log2(3)).
    return kappa - 2 * q_bits - math.log2(3.0)


def interactive_bits(cfg: Config, q: int, *, per_round_max: bool = False) -> float:
    return neglog2_sum_from_bits(
        [commit_bits(cfg, per_round_max=per_round_max), query_bits(cfg.delta, q)]
    )


def noninteractive_bits(cfg: Config, q: int, *, per_round_max: bool = False) -> float:
    fs_loss = cfg.q_bits
    return neglog2_sum_from_bits(
        [
            commit_bits(cfg, per_round_max=per_round_max) - fs_loss,
            query_bits(cfg.delta, q) - fs_loss,
            binding_bits(cfg.q_bits, cfg.kappa),
        ]
    )


def required_q_for_query(delta: float, target_bits: int, q_bits: int) -> int:
    """Queries needed for the query term alone after Q-loss."""
    return math.ceil((target_bits + q_bits) / math.log2(1.0 / (1.0 - delta / 2.0)))


def feasibility(cfg: Config, target_bits: int, *, per_round_max: bool = False) -> str:
    q_req = required_q_for_query(cfg.delta, target_bits, cfg.q_bits)
    commit_after_q = commit_bits(cfg, per_round_max=per_round_max) - cfg.q_bits
    bind = binding_bits(cfg.q_bits, cfg.kappa)
    if commit_after_q < target_bits:
        return "commit"
    if bind < target_bits:
        return "hash"
    return str(q_req)


def q_targets(cfg: Config, targets: list[int], *, per_round_max: bool) -> list[str]:
    return [feasibility(cfg, t, per_round_max=per_round_max) for t in targets]


def print_markdown(target_bits: int, *, per_round_max: bool) -> None:
    title = "tighter per-round-max FS accounting" if per_round_max else "loose theorem accounting"
    print(f"# Non-interactive parameters ({title})\n")
    print(
        "| Config | |F| bits | q now | interactive bits | NI bits now | "
        f"{target_bits}-bit NI target |"
    )
    print("|---|---:|---:|---:|---:|---|")
    for cfg in CONFIGS:
        print(
            f"| {cfg.name} | {cfg.field_bits:.0f} | {cfg.q_now} | "
            f"{interactive_bits(cfg, cfg.q_now, per_round_max=per_round_max):.1f} | "
            f"{noninteractive_bits(cfg, cfg.q_now, per_round_max=per_round_max):.1f} | "
            f"{feasibility(cfg, target_bits, per_round_max=per_round_max)} |"
        )
    targets = [64, 100, 128]
    print("\n# Required q by non-interactive target\n")
    print("| Config | 64-bit NI | 100-bit NI | 128-bit NI |")
    print("|---|---:|---:|---:|")
    for cfg in CONFIGS:
        q64, q100, q128 = q_targets(cfg, targets, per_round_max=per_round_max)
        print(f"| {cfg.name} | {q64} | {q100} | {q128} |")


def print_latex(target_bits: int, *, per_round_max: bool) -> None:
    print(r"\begin{tabular}{lrrrrrrr}")
    print(r"\toprule")
    print(
        r"Config & $|F|$ bits & $q$ now & Interactive & NI now & "
        r"$q_{64}$ & $q_{100}$ & $q_{128}$ \\"
    )
    print(r"\midrule")
    for cfg in CONFIGS:
        q64, q100, q128 = q_targets(cfg, [64, 100, 128], per_round_max=per_round_max)
        print(
            f"{cfg.name} & {cfg.field_bits:.0f} & {cfg.q_now} & "
            f"{interactive_bits(cfg, cfg.q_now, per_round_max=per_round_max):.1f} & "
            f"{noninteractive_bits(cfg, cfg.q_now, per_round_max=per_round_max):.1f} & "
            f"{q64} & {q100} & {q128} \\\\"
        )
    print(r"\bottomrule")
    print(r"\end{tabular}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=128)
    parser.add_argument("--latex", action="store_true")
    parser.add_argument(
        "--per-round-max",
        action="store_true",
        help="Use the tighter FS accounting from Remark D.2.",
    )
    args = parser.parse_args()
    if args.latex:
        print_latex(args.target, per_round_max=args.per_round_max)
    else:
        print_markdown(args.target, per_round_max=args.per_round_max)


if __name__ == "__main__":
    main()
