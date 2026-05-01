"""g3_singular_run.py — generate Singular input for cert+div Groebner.

Singular handles GB much faster than Sympy. This script:
1. Generates cert+div polynomial equations in Singular syntax.
2. Invokes Singular to compute lex GB.
3. Parses the output.
"""
import subprocess
import sympy as sp
import sys
import time


def gen_singular_input(n, k, a, b, order="lp"):
    """Generate Singular input for sign-paired cert+div at (n, k, a, b)."""
    x = sp.Symbol("x")
    p = sp.symbols("p0:" + str(2 * k))
    rho = sp.Symbol("rho")
    t = 2 * k

    P = x**t + sum(p[i] * x**i for i in range(t))
    rem_a = sp.Poly(sp.rem(x**a, P, x), x)
    rem_b = sp.Poly(sp.rem(x**b, P, x), x)

    cert_eqs = [
        sp.expand(rho * rem_a.coeff_monomial(x**d) + rem_b.coeff_monomial(x**d))
        for d in range(k, t)
    ]
    rem_n = sp.Poly(sp.rem(x**n - 1, P, x), x)
    div_eqs = [sp.expand(c) for c in rem_n.all_coeffs()]

    eqs = [e for e in cert_eqs + div_eqs if e != 0]

    # Convert to Singular syntax
    var_list = ", ".join([f"p{i}" for i in range(t)] + ["rho"])

    eqs_str = ",\n".join([
        str(e).replace("**", "^") for e in eqs
    ])

    src = f"""// Auto-generated for (n={n}, k={k}, a={a}, b={b}) — sign-paired
ring R = 0, ({var_list}), {order};
ideal I =
{eqs_str};
ideal G = std(I);
"size GB:";
size(G);
"GB elements:";
G;
quit;
"""
    return src


def run_singular(src, timeout=1800):
    t0 = time.time()
    proc = subprocess.run(
        ["Singular", "-q"],
        input=src,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    t1 = time.time()
    return proc.stdout, proc.stderr, t1 - t0


def main():
    cases = [
        (8, 2, 2, 6),
        (16, 4, 4, 12),
        (32, 8, 8, 24),
    ]
    for n, k, a, b in cases:
        print(f"\n=== (n={n}, k={k}, a={a}, b={b}) sign-paired ===")
        src = gen_singular_input(n, k, a, b, order="lp")
        try:
            out, err, dt = run_singular(src, timeout=1800)
            print(f"Singular completed in {dt:.1f}s")
            print(out)
            if err.strip():
                print(f"STDERR: {err}", file=sys.stderr)
        except subprocess.TimeoutExpired:
            print(f"Singular TIMEOUT (1800s)")


if __name__ == "__main__":
    main()
