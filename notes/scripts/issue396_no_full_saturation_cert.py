"""Singular saturation certificate for issue #396 no-full rank collapse.

The symbolic-alpha scan reduces a fixed support and no-full subset S to

    C(S) + alpha M(S) = 0.

After quotienting away the alpha=0 zero-row family, the remaining legal panel
cases should have no point with both residual rows nonzero.  This driver
enumerates those remaining cases and asks Singular to verify

    sat(sat(sat(<C+alpha M>, <alpha>), <u_alpha coefficients>),
        <v_alpha coefficients>) = <1>.

That is the finite-field GB form of "no solution remains after quotienting the
alpha=0 branch and saturating away u=0 and v=0".
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from issue396_component_family_scan import precompute_component_tests
from issue396_component_polynomial_audit import subgroup
from issue396_no_full_symbolic_cert import (
    candidate_rows,
    occupancy,
    split_residual_linear_parts,
)
from issue396_saturated_witness_general_k import stable_coefs


def linear_poly(c: int, s: int, p: int) -> str:
    c %= p
    s %= p
    if s == 0:
        return str(c)
    if c == 0:
        return "a" if s == 1 else f"{s}*a"
    return f"{s}*a+{c}"


def ideal_expr(polys: list[str]) -> str:
    keep = [poly for poly in polys if poly != "0"]
    if not keep:
        return "ideal(0)"
    return "ideal(" + ",".join(keep) + ")"


def collect_cases(args):
    import issue396_no_full_symbolic_cert as cert

    cert.init_worker(args.q, args.n2, args.k2)

    p = args.q
    L2 = subgroup(args.n2, p)
    tests = precompute_component_tests(L2, p)
    keep = [i for i, S in enumerate(tests["subsets"]) if max(occupancy(S)) < args.k2]
    tails = tests["tails"][keep]
    subsets = tuple(tests["subsets"][i] for i in keep)

    support_stop = args.support_start + args.support_count
    supports = combinations(range(args.support_start, support_stop), 3)

    cases = []
    hist = Counter()
    for support in supports:
        coefs = stable_coefs(support, p)
        u0, u1, v0, v1 = split_residual_linear_parts(support, coefs)
        cu = np.tensordot(tails, u0, axes=([1], [0])) % p
        su = np.tensordot(tails, u1, axes=([1], [0])) % p
        cv = np.tensordot(tails, v0, axes=([1], [0])) % p
        sv = np.tensordot(tails, v1, axes=([1], [0])) % p
        constants = np.concatenate([cu, cv], axis=1)
        slopes = np.concatenate([su, sv], axis=1)
        idx, alpha, all_alpha = candidate_rows(constants, slopes)

        hist["supports"] += 1
        hist["candidate_subsets"] += int(len(idx))
        hist["all_alpha_subsets"] += int(len(all_alpha))

        for subset_idx, alpha1 in zip(idx, alpha):
            alpha1 = int(alpha1)
            if args.skip_alpha_zero and alpha1 == 0:
                hist["skipped_alpha_zero"] += 1
                continue

            subset_idx = int(subset_idx)
            eqs = [
                linear_poly(int(c), int(s), p)
                for c, s in zip(constants[subset_idx], slopes[subset_idx])
            ]
            u_polys = [
                linear_poly(int(c), int(s), p) for c, s in zip(u0, u1)
            ]
            v_polys = [
                linear_poly(int(c), int(s), p) for c, s in zip(v0, v1)
            ]
            cases.append(
                {
                    "id": len(cases) + 1,
                    "support": tuple(int(x) for x in support),
                    "coefs": tuple(int(x % p) for x in coefs),
                    "S": tuple(int(x) for x in subsets[subset_idx]),
                    "occupancy": occupancy(subsets[subset_idx]),
                    "alpha1": alpha1,
                    "I": ideal_expr(eqs),
                    "U": ideal_expr(u_polys),
                    "V": ideal_expr(v_polys),
                }
            )
            hist["saturation_cases"] += 1
            if args.limit and len(cases) >= args.limit:
                return cases, hist

        for subset_idx in all_alpha:
            subset_idx = int(subset_idx)
            u_polys = [
                linear_poly(int(c), int(s), p) for c, s in zip(u0, u1)
            ]
            v_polys = [
                linear_poly(int(c), int(s), p) for c, s in zip(v0, v1)
            ]
            cases.append(
                {
                    "id": len(cases) + 1,
                    "support": tuple(int(x) for x in support),
                    "coefs": tuple(int(x % p) for x in coefs),
                    "S": tuple(int(x) for x in subsets[subset_idx]),
                    "occupancy": occupancy(subsets[subset_idx]),
                    "alpha1": "all",
                    "I": "ideal(0)",
                    "U": ideal_expr(u_polys),
                    "V": ideal_expr(v_polys),
                }
            )
            hist["saturation_cases"] += 1
            hist["saturation_all_alpha_cases"] += 1
            if args.limit and len(cases) >= args.limit:
                return cases, hist

    return cases, hist


def singular_script(p: int, cases: list[dict]) -> str:
    lines = [
        'LIB "elim.lib";',
        f"ring r={p},(a),lp;",
        "int bad=0;",
        "int good=0;",
    ]
    for case in cases:
        cid = case["id"]
        lines.extend(
            [
                f"ideal I{cid}={case['I']};",
                f"ideal A{cid}=ideal(a);",
                f"ideal U{cid}={case['U']};",
                f"ideal V{cid}={case['V']};",
                f"ideal J{cid}=sat(I{cid},A{cid});",
                f"J{cid}=sat(J{cid},U{cid});",
                f"J{cid}=sat(J{cid},V{cid});",
                f"ideal G{cid}=std(J{cid});",
                (
                    f"if (size(G{cid})==1 && G{cid}[1]==1) "
                    "{ good=good+1; } "
                    f"else {{ bad=bad+1; \"BAD case={cid} dim=\"+string(dim(G{cid})); G{cid}; }}"
                ),
            ]
        )
    lines.extend(['"GOOD="+string(good);', '"BAD="+string(bad);', "quit;"])
    return "\n".join(lines) + "\n"


def run_singular_chunk(p: int, chunk: list[dict], keep_scripts: Path | None):
    script = singular_script(p, chunk)
    with tempfile.NamedTemporaryFile("w", suffix=".sing", delete=False) as f:
        f.write(script)
        script_path = Path(f.name)
    try:
        result = subprocess.run(
            ["Singular", "-q", str(script_path)],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    finally:
        if keep_scripts is not None:
            keep_scripts.mkdir(parents=True, exist_ok=True)
            target = keep_scripts / script_path.name
            script_path.replace(target)
        else:
            script_path.unlink(missing_ok=True)
    return result.returncode, result.stdout


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, default=193)
    parser.add_argument("--n2", type=int, default=16)
    parser.add_argument("--k2", type=int, default=4)
    parser.add_argument("--support-start", type=int, default=16)
    parser.add_argument("--support-count", type=int, default=48)
    parser.add_argument("--chunk-size", type=int, default=256)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--skip-alpha-zero", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--keep-scripts", type=Path)
    return parser.parse_args()


def main():
    args = parse_args()
    cases, hist = collect_cases(args)
    print("Issue #396 no-full Singular saturation certificate")
    print(
        f"q={args.q}, L2=({args.n2},{args.k2}), "
        f"support_window=[{args.support_start},{args.support_start + args.support_count}), "
        f"skip_alpha_zero={args.skip_alpha_zero}"
    )
    print(f"hist={dict(sorted(hist.items()))}")
    print(f"saturation_cases={len(cases)}")
    if cases:
        print(f"first_case={{{', '.join(f'{k}: {cases[0][k]}' for k in ['support', 'alpha1', 'S', 'occupancy'])}}}")
        print(f"last_case={{{', '.join(f'{k}: {cases[-1][k]}' for k in ['support', 'alpha1', 'S', 'occupancy'])}}}")
    print()

    total_good = 0
    total_bad = 0
    for start in range(0, len(cases), args.chunk_size):
        chunk = cases[start : start + args.chunk_size]
        rc, out = run_singular_chunk(args.q, chunk, args.keep_scripts)
        good = 0
        bad = 0
        for line in out.splitlines():
            if line.startswith("GOOD="):
                good = int(line.split("=", 1)[1])
            elif line.startswith("BAD="):
                bad = int(line.split("=", 1)[1])
            elif line.startswith("BAD case="):
                print(line)
        total_good += good
        total_bad += bad
        print(
            f"chunk {start // args.chunk_size + 1}: "
            f"cases={len(chunk)}, returncode={rc}, good={good}, bad={bad}",
            flush=True,
        )
        if rc != 0 or bad:
            print(out)
            raise SystemExit(1)

    print()
    print(f"total_good={total_good}")
    print(f"total_bad={total_bad}")
    if total_good != len(cases) or total_bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
