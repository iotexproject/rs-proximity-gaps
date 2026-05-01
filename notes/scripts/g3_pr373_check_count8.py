"""g3_pr373_check_count8.py — verify PR #373 framework on the count=8 witness.

Witness: q=97, positions=[18,19,30], coeffs=[10,92,63] (DFT representation on L_0).
Bad α set: {21,22,32,47,54,69,79,80}, all with d_1=8 (boundary single-defect).

Goal:
  1. For each bad α, find ALL closest c_α ∈ C_1 (and the agreement sets).
  2. Check: do these c_α lie on a single affine line c_e + α c_o ∈ C_1?
     (i.e. M_aff(f) = 1?)
  3. Compute L_sym(f) = number of g ∈ RS_{2k}(L_0) with |K_g|=s-1.
  4. Compute L_sym^alpha(f) = number of distinct α realizing single-defect bad witnesses.
"""
import sys, os, math
from itertools import combinations
import numpy as np

sys.path.insert(0, os.path.expanduser('~/Desktop/2026/ef1m/notes/scripts'))
from fri_2round_attack import setup_chain, even_odd_parts
from mds_decoder import precompute_diff_inv, batched_extras


def evaluate_dft(fhat, L, p):
    n = len(L)
    f = [0] * n
    for i, x in enumerate(L):
        v = 0
        for j in range(len(fhat)):
            if fhat[j] != 0:
                v = (v + fhat[j] * pow(x, j, p)) % p
        f[i] = v
    return f


def interpolate(xs, ys, p):
    """Lagrange interpolate degree-(len-1) polynomial at given points; return coefs (low to high)."""
    n = len(xs)
    poly = [0] * n
    for i in range(n):
        # L_i(x) = prod_{j!=i}(x-xs[j]) / prod_{j!=i}(xs[i]-xs[j])
        num = [1]
        denom = 1
        for j in range(n):
            if i == j: continue
            new_num = [0] * (len(num) + 1)
            for t, c in enumerate(num):
                new_num[t] = (new_num[t] + c * (-xs[j])) % p
                new_num[t+1] = (new_num[t+1] + c) % p
            num = new_num
            denom = (denom * (xs[i] - xs[j])) % p
        denom_inv = pow(denom, p-2, p)
        scale = (ys[i] * denom_inv) % p
        for t in range(len(num)):
            poly[t] = (poly[t] + scale * num[t]) % p
    return poly


def evalpoly(coefs, x, p):
    v = 0
    for c in reversed(coefs):
        v = (v * x + c) % p
    return v


def analyze(p, positions, coeffs, bad_alphas):
    n0, k0 = 32, 8
    n1, k1 = 16, 4
    s = 8
    w_J = n0 - int(math.isqrt(k0 * n0))

    chain = setup_chain(p, n0, k0, R=2)
    L0 = chain[0][0]
    L1 = chain[1][0]
    L0_arr = np.array(L0, dtype=np.int64)
    L1_arr = np.array(L1, dtype=np.int64)
    fhat = [0] * n0
    for pos, c in zip(positions, coeffs):
        fhat[pos] = c
    f = evaluate_dft(fhat, L0, p)
    f_e, f_o = even_odd_parts(f, L0, p)
    f_arr = np.array(f, dtype=np.int64)
    f_e_arr = np.array(f_e, dtype=np.int64)
    f_o_arr = np.array(f_o, dtype=np.int64)

    print(f"\n\n========== q={p}, pos={positions}, coeffs={coeffs}, bad α={bad_alphas} ==========")
    print(f"L_0 size = {n0}, L_1 size = {n1}, s = {s}, w_J = {w_J}")
    print(f"f_e[L_1] = {f_e}")
    print(f"f_o[L_1] = {f_o}")

    # ----- Step 1: For each bad α, find all closest c_α and agreement sets -----
    info_sets = list(combinations(range(n1), k1))
    info_sets_arr = np.array(info_sets, dtype=np.int64)
    D1, inv_D1 = precompute_diff_inv(L1_arr, p)

    # For each α, we want all 8-agreement codewords. There may be multiple.
    # Approach: for each k1=4 subset T, interpolate u_α|T to a poly p_T;
    # if p_T agrees with u_α on >=s positions, record (T, p_T, agreement_set).
    print("\n=== Step 1: Closest codewords per bad α ===")
    alpha_info = {}
    for alpha in bad_alphas:
        u = [(f_e[i] + alpha * f_o[i]) % p for i in range(n1)]
        # find all info-sets T with extras >= s-k1=4
        u_arr = np.array(u, dtype=np.int64)
        extras = batched_extras(info_sets_arr, u_arr, L1_arr, D1, inv_D1, p)
        # extras[t] = # of i ∉ T where p_T(L_1[i]) == u[i]
        # full agreement = k1 + extras
        max_e = int(extras.max())
        agree_max = k1 + max_e

        # Collect distinct p_T polys from all T achieving max_e
        codewords = {}  # tuple(coefs) -> agreement set
        for ti, T in enumerate(info_sets):
            if int(extras[ti]) != max_e:
                continue
            xs = [L1[i] for i in T]
            ys = [u[i] for i in T]
            poly = interpolate(xs, ys, p)
            poly_t = tuple(poly)
            if poly_t in codewords:
                continue
            agree = [i for i in range(n1) if evalpoly(poly, L1[i], p) == u[i]]
            codewords[poly_t] = (poly, set(agree))
        alpha_info[alpha] = {
            'agree': agree_max,
            'codewords': codewords,
            'u': u,
        }
        print(f"  α={alpha}: agreement={agree_max}, # distinct codewords={len(codewords)}")
        for poly, (cf, ag) in codewords.items():
            print(f"     poly_coeffs={cf}, agree_set={sorted(ag)}")

    # ----- Step 2: Affine-line covering -----
    # Try to find c_e, c_o ∈ RS_{k1}(L_1) such that for each bad α there is a c_α = c_e + α c_o
    # in the candidate codeword list. With 8 alphas and at most 8 codewords each, brute search is feasible.
    print("\n=== Step 2: Affine line c_α = c_e + α c_o ===")
    # Pick c_α candidates per α; try all combos? That's product of |codewords|.
    # First print possibilities, then if all single — easy.
    one_per = all(len(d['codewords']) == 1 for d in alpha_info.values())
    print(f"  All α have unique closest codeword: {one_per}")

    # Even if multiple, we can pick one representative each, fit affine line via
    # least-squares-like exact: for any 2 αs, c_e and c_o are determined.
    # Then check consistency for the rest.
    ref_alphas = bad_alphas
    polys_per_a = {a: list(alpha_info[a]['codewords'].keys()) for a in ref_alphas}

    # For all combinations (one poly per alpha), test affine consistency:
    from itertools import product
    sizes = [len(polys_per_a[a]) for a in ref_alphas]
    total_combos = 1
    for s_ in sizes: total_combos *= s_
    print(f"  Combinations to test: {total_combos}")

    found_lines = []
    for combo in product(*[polys_per_a[a] for a in ref_alphas]):
        # combo[i] is a tuple poly for ref_alphas[i]
        # Use first 2 alphas to derive c_e, c_o: c_e + a1*c_o = combo[0], c_e + a2*c_o = combo[1]
        a1, a2 = ref_alphas[0], ref_alphas[1]
        c1 = list(combo[0])
        c2 = list(combo[1])
        # ensure same length
        L = max(len(c1), len(c2))
        c1 += [0] * (L - len(c1)); c2 += [0] * (L - len(c2))
        diff = [(c1[i] - c2[i]) % p for i in range(L)]
        a_diff_inv = pow((a1 - a2) % p, p-2, p)
        c_o = [(d * a_diff_inv) % p for d in diff]
        c_e = [(c1[i] - a1 * c_o[i]) % p for i in range(L)]
        # check rest
        ok = True
        for j, a in enumerate(ref_alphas):
            ca_pred = [(c_e[i] + a * c_o[i]) % p for i in range(L)]
            actual = list(combo[j]) + [0] * (L - len(combo[j]))
            if ca_pred[:L] != actual[:L]:
                ok = False
                break
        if ok:
            found_lines.append((tuple(c_e), tuple(c_o), combo))

    print(f"  Affine-line solutions found: {len(found_lines)}")
    if found_lines:
        c_e, c_o, _ = found_lines[0]
        print(f"  c_e = {list(c_e)}")
        print(f"  c_o = {list(c_o)}")
        # Compute K = {i : f_e(i) = c_e(i) AND f_o(i) = c_o(i)}
        K = [i for i in range(n1) if (f_e[i] - evalpoly(list(c_e), L1[i], p)) % p == 0
                                  and (f_o[i] - evalpoly(list(c_o), L1[i], p)) % p == 0]
        print(f"  Kernel K = {K}, |K| = {len(K)}, s-1 = {s-1}")
        # Also: g(x) = c_e(x²) + x c_o(x²); compute its agreement with f on L_0
        g_vals = [(evalpoly(list(c_e), (L0[i]*L0[i]) % p, p)
                  + L0[i] * evalpoly(list(c_o), (L0[i]*L0[i]) % p, p)) % p for i in range(n0)]
        agree_g = [i for i in range(n0) if g_vals[i] == f[i]]
        print(f"  Parent g = c_e(x²)+x·c_o(x²) agrees with f on {len(agree_g)} of {n0} L_0 positions")
        print(f"  Strict above-J requires: |g-f| >= dist > w_J=16, i.e. agreement < n0 - w_J = 16")
        print(f"  Agreement count = {len(agree_g)} (must be < 16 for strict above-J)")

    # ----- Step 3: report the M_aff > 1 finding =====
    if found_lines:
        # Found 1 line — but we already showed not all on one line; need MULTI-LINE cover.
        pass
    else:
        # Search smaller groups. Need affine-line cover number M_aff.
        # For any 2 alphas, c_e and c_o are uniquely determined. Check which other
        # alphas lie on the line.
        print("\n  Searching multi-line cover...")
        from itertools import combinations as comb
        # For each pair, derive line, see which alphas fit
        line_assignments = {}  # alpha -> list of lines that contain it
        all_lines = {}  # frozen line -> set of alphas
        for i_a, a1 in enumerate(bad_alphas):
            for j_a in range(i_a + 1, len(bad_alphas)):
                a2 = bad_alphas[j_a]
                c1 = list(alpha_info[a1]['codewords'].keys())[0]
                c2 = list(alpha_info[a2]['codewords'].keys())[0]
                L = max(len(c1), len(c2))
                c1l = list(c1) + [0] * (L - len(c1))
                c2l = list(c2) + [0] * (L - len(c2))
                diff = [(c1l[i] - c2l[i]) % p for i in range(L)]
                a_diff_inv = pow((a1 - a2) % p, p-2, p)
                c_o = tuple((d * a_diff_inv) % p for d in diff)
                c_e = tuple((c1l[i] - a1 * c_o[i]) % p for i in range(L))
                # Find all alphas whose c_α matches c_e + α c_o on this line
                covered = []
                for a in bad_alphas:
                    pred = tuple((c_e[i] + a * c_o[i]) % p for i in range(L))
                    actual_t = list(alpha_info[a]['codewords'].keys())[0]
                    actual = tuple(list(actual_t) + [0] * (L - len(actual_t)))
                    if pred == actual:
                        covered.append(a)
                if len(covered) >= 2:
                    line_key = (c_e, c_o)
                    if line_key not in all_lines:
                        all_lines[line_key] = set(covered)
        loads = sorted([len(als) for als in all_lines.values()], reverse=True)
        print(f"  Distinct affine lines covering ≥2 bad alphas: {len(all_lines)}; loads={loads}")
        # Each line empirically carries exactly 2 alphas → perfect matching = M_aff.
        edges = list(all_lines.items())
        cover = None
        def find_matching(remaining_alphas, used, idx_start):
            nonlocal cover
            if cover is not None:
                return
            if not remaining_alphas:
                cover = list(used)
                return
            pivot = min(remaining_alphas)
            for i in range(idx_start, len(edges)):
                line, als = edges[i]
                if pivot in als and als <= remaining_alphas:
                    find_matching(remaining_alphas - als, used + [(line, als)], 0)
                    if cover is not None:
                        return
        find_matching(set(bad_alphas), [], 0)
        if cover is None:
            cover = []
        print(f"\n  M_aff(f) (perfect matching) = {len(cover)}")
        for line, als in cover:
            if line is None:
                print(f"     SINGLETON α={list(als)[0]}")
            else:
                ce, co = line
                K = [i for i in range(n1)
                     if (f_e[i] - evalpoly(list(ce), L1[i], p)) % p == 0
                     and (f_o[i] - evalpoly(list(co), L1[i], p)) % p == 0]
                print(f"     LINE c_e={list(ce)}, c_o={list(co)}: covers {sorted(als)}, |K|={len(K)}")
                # parent g
                g_vals = [(evalpoly(list(ce), (L0[i]*L0[i]) % p, p)
                          + L0[i] * evalpoly(list(co), (L0[i]*L0[i]) % p, p)) % p
                          for i in range(n0)]
                ag = sum(1 for i in range(n0) if g_vals[i] == f[i])
                print(f"        parent g agrees with f on {ag}/{n0} L_0 positions  (need <16 for strict above-J)")

    # ----- Step 4: L_sym(f) — parents with |K_g| = s-1 = 7 =====
    print("\n  L_sym: (skipped — see PR #373 verify_lsym_toy.py for f-specific)")
    return  # end analyze

def main():
    print("=== Count=8 witness ===")
    analyze(97, [18, 19, 30], [10, 92, 63],
            [21, 22, 32, 47, 54, 69, 79, 80])
    print("=== Count=2 witness ===")
    analyze(97, [9, 20, 22, 24, 25], [93, 93, 22, 45, 69],
            [14, 59])

if __name__ == "__main__":
    main()

# --- Notes on L_sym (not implemented here; see PR #373 verify_lsym_toy.py).
