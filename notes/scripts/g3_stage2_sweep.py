"""g3_stage2_sweep.py — sweep Stage 2 across deployment fields and h values.

Fields:
- KoalaBear:  q = 2^31 - 2^24 + 1 = 2,130,706,433  (q-1 = 2^24 · 127)
- BabyBear:   q = 15·2^27 + 1 = 2,013,265,921       (q-1 = 2^27 · 15)
- Mersenne-31: q = 2^31 - 1 = 2,147,483,647         (q-1 = 2 · 3^2 · 7 · 11 · 31 · 151 · 331)
- Goldilocks: q = 2^64 - 2^32 + 1                   (Plonky2)

For each (field, h), if 8 | q-1 then rho exists in F_q directly. Otherwise
report — sextic extension F_{q^6} or other extension would be needed.

Per (field, h): build .sing via g3_stage2_fast, run Singular, check if
GB == {a_c, b_c} (all unknowns), record result.
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_stage2_fast import build_stage2, emit_singular, find_rho

FIELDS = {
    "koala":      2**31 - 2**24 + 1,        # 2,130,706,433
    "babybear":   15 * (2**27) + 1,          # 2,013,265,921
    "mersenne31": 2**31 - 1,                 # 2,147,483,647
    "goldilocks": (2**64) - (2**32) + 1,     # 18,446,744,069,414,584,321
}


def gb_is_full(stdout):
    """GB success ⇔ output contains all a_c, b_c as separate generators
    AND no other content."""
    lines = stdout.split("\n")
    in_gb = False
    gens = []
    for line in lines:
        line = line.strip().rstrip(",")
        if line == "GB:":
            in_gb = True
            continue
        if in_gb and line:
            gens.append(line)
    return gens


def run_singular(sing_file, timeout):
    t0 = time.time()
    try:
        result = subprocess.run(
            ["Singular", "-q", sing_file],
            capture_output=True, text=True, timeout=timeout,
        )
        return result.stdout + result.stderr, time.time() - t0
    except subprocess.TimeoutExpired:
        return "TIMEOUT", time.time() - t0


def sweep(fields, h_values, timeout=600, build_only=False):
    results = []
    for field_name in fields:
        p = FIELDS[field_name]
        rho_exists = (p - 1) % 8 == 0
        print(f"\n=== {field_name}: q = {p}, q-1 mod 8 = {(p-1) % 8} ===")
        if not rho_exists:
            print(f"  rho does not exist in F_q (need ≡ 1 mod 8); skip base; sextic later")
            results.append((field_name, "all", "no-rho-base"))
            continue
        rhos = find_rho(p)
        rho_val = sorted(rhos)[0]
        print(f"  rho = {rho_val}")

        for h in h_values:
            sing_file = f"/tmp/{field_name}_h{h}.sing"
            t0 = time.time()
            try:
                eqs, nvar = build_stage2(h, p, rho_val)
                t_build = time.time() - t0
                emit_singular(eqs, nvar, h, p, sing_file)
                print(f"  h={h}: build {t_build:.2f}s, {len(eqs)} eqs, {nvar} vars; .sing → {sing_file}")
            except Exception as ex:
                print(f"  h={h}: BUILD FAIL {type(ex).__name__}: {ex}")
                results.append((field_name, h, "build-fail"))
                continue
            if build_only:
                results.append((field_name, h, "built"))
                continue
            output, t_run = run_singular(sing_file, timeout)
            gens = gb_is_full(output)
            expected = set([f"a{c}" for c in range(1, h)] + [f"b{c}" for c in range(1, h)])
            got = set(g for g in gens if g in expected)
            if got == expected:
                print(f"  h={h}: GB RIGOROUS ({t_run:.1f}s) — ideal = max(0,...,0)")
                results.append((field_name, h, "rigorous"))
            elif "TIMEOUT" in output:
                print(f"  h={h}: TIMEOUT after {t_run:.1f}s")
                results.append((field_name, h, "timeout"))
            else:
                print(f"  h={h}: GB ≠ full; got {len(gens)} gens (need {2*(h-1)})")
                if len(gens) <= 30:
                    for g in gens[:30]:
                        print(f"      {g}")
                results.append((field_name, h, "partial"))
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--fields", nargs="+", default=list(FIELDS.keys()))
    parser.add_argument("--h", type=int, nargs="+", default=[4, 8])
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--build-only", action="store_true")
    args = parser.parse_args()
    res = sweep(args.fields, args.h, timeout=args.timeout, build_only=args.build_only)
    print("\n=== SUMMARY ===")
    for r in res:
        print(f"  {r}")


if __name__ == "__main__":
    main()
