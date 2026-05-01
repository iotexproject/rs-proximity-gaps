"""g3_stage2_singular_sweep.py — Stage 2 sweep using Singular GB.

Singular is ~1000x faster than sympy for these GBs. Sweeps h from a list,
optionally across multiple primes.
"""
import argparse
import os
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, "notes/scripts")
from g3_stage2_singular_gen import emit_singular
from g3_stage2_multi_prime import find_rho_eps


def run_singular(script: str) -> tuple[float, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".sing", delete=False) as f:
        f.write(script)
        path = f.name
    try:
        t0 = time.time()
        result = subprocess.run(
            ["Singular", "-q"],
            stdin=open(path),
            capture_output=True,
            text=True,
            timeout=3600,
        )
        elapsed = time.time() - t0
        return elapsed, result.stdout
    finally:
        os.unlink(path)


def parse_singular_output(out: str, num_vars: int) -> tuple[bool, int]:
    """Returns (all_zero, gb_size)."""
    lines = out.strip().split("\n")
    gb_size = -1
    zeros = 0
    state = None
    for line in lines:
        line = line.strip()
        if line.startswith("GB size:"):
            state = "gb"
            continue
        if state == "gb":
            try:
                gb_size = int(line)
            except ValueError:
                pass
            state = None
            continue
        if "reduces to:" in line:
            state = "red"
            continue
        if state == "red":
            if line == "0":
                zeros += 1
            state = None
    return zeros == num_vars, gb_size


def test_h(h: int, prime: int, rho_val: int, eps_val: int) -> dict:
    print(f"\n=== h={h}, char={prime}, rho={rho_val}, eps={eps_val} ===")
    script = emit_singular(h, prime, rho_val, eps_val)
    elapsed, out = run_singular(script)
    num_vars = 2 * (h - 1)
    all_zero, gb_size = parse_singular_output(out, num_vars)
    status = "OK" if all_zero else "FAIL"
    print(
        f"  GB size {gb_size}, elapsed {elapsed:.2f}s, "
        f"all p_vars → 0: {all_zero} [{status}]"
    )
    return {
        "h": h,
        "prime": prime,
        "rho": rho_val,
        "eps": eps_val,
        "elapsed_s": elapsed,
        "gb_size": gb_size,
        "all_zero": all_zero,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hs", type=str, default="2,4,8,16,32,64",
        help="Comma-separated list of h values."
    )
    parser.add_argument(
        "--primes", type=str, default="17",
        help="Comma-separated list of primes."
    )
    args = parser.parse_args()

    hs = [int(x) for x in args.hs.split(",")]
    primes = [int(x) for x in args.primes.split(",")]

    results = []
    for h in hs:
        for p in primes:
            re = find_rho_eps(p)
            if re is None:
                print(f"\nh={h}, p={p}: no rho with rho^8 = 16; skip")
                continue
            rho_val, eps_val = re
            try:
                r = test_h(h, p, rho_val, eps_val)
                results.append(r)
            except Exception as exc:
                print(f"  failed: {exc}")

    print("\n========== SUMMARY ==========")
    print(f"{'h':>3} {'k':>4} {'n':>5} {'prime':>5} {'GB':>4} {'time(s)':>8} {'OK?':>5}")
    for r in results:
        print(
            f"{r['h']:>3} {2*r['h']:>4} {8*r['h']:>5} {r['prime']:>5} "
            f"{r['gb_size']:>4} {r['elapsed_s']:>8.2f} "
            f"{'YES' if r['all_zero'] else 'NO':>5}"
        )


if __name__ == "__main__":
    main()
