"""g3_smono_generate.py — emit one .sing file per s-mono case at (n, k) = (8, 2).

Usage: python3 g3_smono_generate.py <s>
       Generates {s}mono_case_NN.sing for each case.
"""
import itertools
import sys
from math import gcd
from functools import reduce as freduce


def make_template(s, positions):
    """Build a Singular .sing file content for given positions tuple."""
    rho_decls = ", ".join(f"rho{i}" for i in range(1, s))
    h_terms = " + ".join(
        [f"rho{i+1} * zs[{positions[i]}]" for i in range(s - 1)] +
        [f"alpha * zs[{positions[s-1]}]"]
    )
    pos_str = ", ".join(map(str, positions))
    return f"""// {s}-mono case ({pos_str}) at (n, k) = (8, 2).
ring R = 0, (z, p0, p1, p2, p3, alpha, {rho_decls}), (dp(1), lp({s + 4}));
poly sigma = z^4 + p3*z^3 + p2*z^2 + p1*z + p0;

poly z_1 = z;
poly z_2 = reduce(z^2, std(sigma));
poly z_3 = reduce(z^3, std(sigma));
poly z_4 = reduce(z^4, std(sigma));
poly z_5 = reduce(z^5, std(sigma));
poly z_6 = reduce(z^6, std(sigma));
poly z_7 = reduce(z^7, std(sigma));
list zs = z_1, z_2, z_3, z_4, z_5, z_6, z_7;

poly z8 = reduce(z^8 - 1, std(sigma));
matrix Mn = coeffs(z8, z);
poly div0 = Mn[1, 1];
poly div1 = Mn[2, 1];
poly div2 = Mn[3, 1];
poly div3 = Mn[4, 1];

poly h = {h_terms};
matrix M = coeffs(h, z);
poly cert2 = M[3, 1];
poly cert3 = M[4, 1];
ideal I = cert2, cert3, div0, div1, div2, div3;
print("CASE: ({pos_str})");
print("Starting elimination...");
ideal E = eliminate(I, p0*p1*p2*p3);
print("Done. E size:");
print(size(E));
poly phi = E[size(E)];
intvec deg_pat = 0,0,0,0,0,1{",0" * (s - 1)};
int deg_a = deg(phi, deg_pat);
print("CASE_RESULT ({pos_str}): deg_alpha = " + string(deg_a));
exit;
"""


def main():
    if len(sys.argv) != 2:
        print("Usage: g3_smono_generate.py <s>")
        sys.exit(1)
    s = int(sys.argv[1])
    if s < 2 or s > 7:
        print("s must be in [2, 7]")
        sys.exit(1)

    cases = []
    for combo in itertools.combinations(range(1, 8), s):
        if freduce(gcd, list(combo) + [8]) == 1:
            cases.append(combo)

    print(f"# {len(cases)} {s}-mono irreducible cases at (8, 2)")
    for i, positions in enumerate(cases, start=1):
        filename = f"{s}mono_case_{i:02d}.sing"
        content = make_template(s, positions)
        with open(filename, "w") as f:
            f.write(content)
        print(f"  {filename}: {positions}")


if __name__ == "__main__":
    main()
