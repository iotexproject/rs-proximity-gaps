"""
Debug FRI folding for n=14, k=7, p=29.
Check why cw with |E'|=4 and w'=3 don't survive with 1 cancellation.
"""
import math

n, k, p = 14, 7, 29

# Find omega (primitive 14th root)
for g in range(2, p):
    x, seen = 1, set()
    for _ in range(p-1): seen.add(x); x = x*g%p
    if len(seen) == p-1:
        omega = pow(g, (p-1)//n, p)
        break

print(f"p={p}, omega={omega}")
pw = [pow(omega, i, p) for i in range(n)]
print(f"Powers: {pw}")
print(f"Check: omega^14 = {pow(omega, 14, p)}")
print(f"-1 = omega^7 = {pow(omega, 7, p)} (should be {p-1})")

n2, k2 = 7, 3
inv2 = pow(2, p-2, p)
pw2 = [pow(omega, 2*i, p) for i in range(n2)]
print(f"L' powers: {pw2}")

# Build a simple test case:
# Take a known codeword (constant function = 1)
# and center that differs at positions E = {0,3,10,11,12}
c_vals = [1] * n  # constant codeword
center = list(c_vals)  # start from codeword
E = [0, 3, 10, 11, 12]
for i in E:
    center[i] = (center[i] + 1) % p  # change value at error positions

print(f"\nCenter: {center}")
print(f"Codeword: {c_vals}")
print(f"Error set: {E}")
print(f"Distance: {sum(1 for i in range(n) if (center[i]-c_vals[i])%p)}")

# Coefficients of codeword: f(x) = 1, so co = [1, 0, 0, ..., 0]
co = [1] + [0]*(k-1)

# Verify evaluation
for i in range(n):
    v = sum(co[j] * pow(pw[i], j, p) for j in range(k)) % p
    assert v == 1, f"Eval at {i}: {v} != 1"

# Fold center and codeword for each alpha
print(f"\nFolding analysis:")
print(f"Johnson w' for RS[{n2},{k2}]: {int(math.floor(n2 - math.sqrt(n2*(k2-1))))}")

w_prime = int(math.floor(n2 - math.sqrt(n2*(k2-1))))

for alpha in [1, 5, 9, 24, 28]:
    # Fold center
    gc = []
    for i in range(n2):
        fi, fi2 = center[i], center[i + n2]
        fe = (fi + fi2) * inv2 % p
        inv_oi = pow(pw[i], p-2, p)
        fo = (fi - fi2) * inv2 % p * inv_oi % p
        gc.append((fe + alpha * fo) % p)

    # Fold codeword coefficients
    fc = []
    for j in range(k2):
        ce = co[2*j] if 2*j < k else 0
        co2_val = co[2*j+1] if 2*j+1 < k else 0
        fc.append((ce + alpha * co2_val) % p)

    # Evaluate folded codeword
    fv = []
    for i in range(n2):
        v = 0
        xi = 1
        for c_coeff in fc:
            v = (v + c_coeff * xi) % p
            xi = xi * pw2[i] % p
        fv.append(v)

    # Distance
    df = sum(1 for i in range(n2) if (fv[i] - gc[i]) % p)

    print(f"\n  alpha={alpha}:")
    print(f"    gc  = {gc}")
    print(f"    fv  = {fv}")
    print(f"    diff= {[(fv[i]-gc[i])%p for i in range(n2)]}")
    print(f"    dist= {df}, w'={w_prime}, survive={'YES' if df <= w_prime else 'NO'}")

    # Show which positions have nonzero folded error
    for i in range(n2):
        diff = (fv[i] - gc[i]) % p
        if diff:
            # Which original positions map here?
            orig = [j for j in range(n) if j % n2 == i]
            in_E = [j for j in orig if j in E]
            print(f"      pos {i}: diff={diff}, originals={orig}, in_E={in_E}")

# Also: check the "theoretical" canceling alpha for each position
print(f"\n\nTheoretical canceling alphas:")
for i_pos in E:
    i_mod = i_pos % n2
    partner = (i_pos + n2) % n
    if partner in E:
        # Paired: compute e_E and e_O
        ei = (center[i_pos] - c_vals[i_pos]) % p
        ep = (center[partner] - c_vals[partner]) % p
        e_E = (ei + ep) * inv2 % p
        inv_oi = pow(pw[i_pos], p-2, p)
        e_O = (ei - ep) * inv2 % p * inv_oi % p
        if e_O != 0:
            cancel_alpha = (p - e_E) * pow(e_O, p-2, p) % p
            print(f"  pos {i_pos} (paired with {partner}): "
                  f"e_E={e_E}, e_O={e_O}, cancel_alpha={cancel_alpha}")
        else:
            print(f"  pos {i_pos} (paired with {partner}): "
                  f"e_E={e_E}, e_O=0, NO cancellation")
    else:
        # Unpaired
        ei = (center[i_pos] - c_vals[i_pos]) % p
        # e_fold = ei/2 + alpha * ei/(2*omega^i)
        # = ei * (1 + alpha * omega^{-i}) / 2
        # Cancel: alpha = -omega^i
        cancel_alpha = (p - pw[i_pos]) % p
        print(f"  pos {i_pos} (unpaired): cancel_alpha=-omega^{i_pos}={cancel_alpha}")
