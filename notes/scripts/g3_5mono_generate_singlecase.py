"""g3_5mono_generate_singlecase.py — emit one .sing file per 5-mono case.

For cluster parallel execution: each .sing file independently computes
deg_alpha(Phi) for one (a, b, c, d, e) combination. Submit each as a
separate SLURM job for embarrassingly-parallel s = 5 RIGOROUS sweep.

Output: 5mono_case_<id>.sing in the current directory.
"""
import itertools
from math import gcd
from functools import reduce as freduce


SING_TEMPLATE = """// 5-mono case ({a}, {b}, {c}, {d}, {e}) at (n, k) = (8, 2).
ring R = 0, (z, p0, p1, p2, p3, alpha, rho1, rho2, rho3, rho4), (dp(1), lp(9));
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

poly h = rho1 * zs[{a}] + rho2 * zs[{b}] + rho3 * zs[{c}] + rho4 * zs[{d}] + alpha * zs[{e}];
matrix M = coeffs(h, z);
poly cert2 = M[3, 1];
poly cert3 = M[4, 1];
ideal I = cert2, cert3, div0, div1, div2, div3;
print("CASE: ({a}, {b}, {c}, {d}, {e})");
print("Starting elimination...");
ideal E = eliminate(I, p0*p1*p2*p3);
print("Done. E size:");
print(size(E));
poly phi = E[size(E)];
int deg_a = deg(phi, intvec(0,0,0,0,0,1,0,0,0,0));
print("CASE_RESULT ({a}, {b}, {c}, {d}, {e}): deg_alpha = " + string(deg_a));
print("FACTORIZE:");
print(factorize(phi));
exit;
"""


def main():
    cases = []
    for combo in itertools.combinations(range(1, 8), 5):
        if freduce(gcd, list(combo) + [8]) == 1:
            cases.append(combo)

    print(f"# {len(cases)} 5-mono irreducible cases at (8, 2)")
    print("# Generates 5mono_case_<id>.sing per case.")
    print()

    for i, (a, b, c, d, e) in enumerate(cases, start=1):
        filename = f"5mono_case_{i:02d}.sing"
        content = SING_TEMPLATE.format(a=a, b=b, c=c, d=d, e=e)
        with open(filename, "w") as f:
            f.write(content)
        print(f"  {filename}: ({a}, {b}, {c}, {d}, {e})")

    print()
    print(f"# Cluster submission (SLURM example):")
    print(f"# for i in $(seq 1 {len(cases)}); do")
    print(f"#     sbatch --time=01:00:00 --mem=16G \\")
    print(f"#         --output=5mono_case_$(printf '%02d' $i).out \\")
    print(f"#         --wrap=\"Singular -q 5mono_case_$(printf '%02d' $i).sing\"")
    print(f"# done")
    print()
    print(f"# Harvest:")
    print(f"# grep 'CASE_RESULT' 5mono_case_*.out | sort -t= -k2 -n")


if __name__ == "__main__":
    main()
