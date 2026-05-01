"""
FRI Folding for n=12, k=6, p=13.
Step 1: Find a center with high M_actual using exhaustive search on a few centers.
Step 2: Analyze folding structure.
"""
import math, random
from itertools import product as iprod
from collections import Counter

n, k = 12, 6
p = 13  # smallest prime = 1 mod 12

# Find primitive 12th root of unity
def find_omega():
    for g in range(2, p):
        seen, x = set(), 1
        for _ in range(p-1): seen.add(x); x = x*g%p
        if len(seen) == p-1:
            return pow(g, (p-1)//n, p)
    return None

omega = find_omega()
w = int(math.floor((1 - math.sqrt(k/n)) * n))  # Johnson radius
n2, k2 = n//2, k//2
w2 = int(math.floor((1 - math.sqrt(k2/n2)) * n2))
if w2 < 1: w2 = 1
inv2 = pow(2, p-2, p)

print(f"n={n} k={k} p={p} omega={omega} w={w}")
print(f"n'={n2} k'={k2} w'={w2}")
print(f"Search space: {p}^{k} = {p**k}")

# Precompute powers
pw = [pow(omega, i, p) for i in range(n)]
pw2 = [pow(omega, 2*i, p) for i in range(n2)]

def eval_poly(co, points):
    vals = []
    for x in points:
        v, xi = 0, 1
        for c in co:
            v = (v + c*xi) % p
            xi = xi * x % p
        vals.append(v)
    return vals

def hdist(a, b):
    return sum(1 for x, y in zip(a, b) if (x-y)%p)

# Build all codewords (4826809 — takes a few minutes)
print("Building all codewords...", flush=True)
all_cws = []
count = 0
for ct in iprod(range(p), repeat=k):
    vals = eval_poly(list(ct), pw)
    all_cws.append((list(ct), vals))
    count += 1
    if count % 500000 == 0:
        print(f"  {count}/{p**k}", flush=True)
print(f"  Done: {len(all_cws)} codewords")

# Find center with max M_actual
print("\nSearching for high-M centers...", flush=True)
random.seed(42)
best_M, best_data = 0, None

for trial in range(50):
    center = [random.randrange(p) for _ in range(n)]
    close = []
    for co, vals in all_cws:
        d = hdist(vals, center)
        if d <= w:
            close.append((co, vals, d))
    M = len(close)
    if M > best_M:
        best_M = M
        best_data = (center, close)
    if trial % 10 == 0:
        print(f"  trial {trial}: M={M}, best so far={best_M}", flush=True)

print(f"\nBest M = {best_M}")
center, cws = best_data

# Error pairing analysis
print(f"\nError pairing (M={best_M}):")
for idx, (co, va, d) in enumerate(cws):
    E = {i for i in range(n) if (va[i]-center[i])%p}
    paired = sum(1 for i in E if (i+n//2)%n in E) // 2
    unp = len(E) - 2*paired
    print(f"  cw{idx}: d={d} E={sorted(E)} paired={paired} unp={unp}")

# FRI folding: test ALL alpha values
print(f"\nFRI folding (all {p-1} alpha values):")
omega2 = pow(omega, 2, p)

def fold_center(center, alpha):
    gc = []
    for i in range(n2):
        fi, fi2 = center[i], center[i+n2]
        fe = (fi + fi2) * inv2 % p
        inv_oi = pow(pw[i], p-2, p)
        fo = (fi - fi2) * inv2 % p * inv_oi % p
        gc.append((fe + alpha*fo) % p)
    return gc

def fold_poly(co, alpha, cur_k):
    nk = cur_k // 2
    fc = []
    for j in range(nk):
        ce = co[2*j] if 2*j < len(co) else 0
        co2 = co[2*j+1] if 2*j+1 < len(co) else 0
        fc.append((ce + alpha * co2) % p)
    return fc

# For each alpha, compute M'
survive_by_alpha = {}
for alpha in range(1, p):
    gc = fold_center(center, alpha)
    survs = []
    for idx, (co, va, d) in enumerate(cws):
        fc = fold_poly(co, alpha, k)
        fv = eval_poly(fc, pw2)
        df = hdist(fv, gc)
        if df <= w2:
            survs.append((idx, df))
    survive_by_alpha[alpha] = survs

survive_counts = [len(v) for v in survive_by_alpha.values()]
dist = Counter(survive_counts)
print(f"  Original M = {best_M}")
print(f"  M' distribution: {dict(sorted(dist.items()))}")
print(f"  Mean M' = {sum(survive_counts)/len(survive_counts):.3f}")
print(f"  Max M' = {max(survive_counts)}")

# Per-codeword survival
print(f"\nPer-codeword survival:")
for idx, (co, va, d) in enumerate(cws):
    E = {i for i in range(n) if (va[i]-center[i])%p}
    paired = sum(1 for i in E if (i+n//2)%n in E) // 2
    unp = len(E) - 2*paired
    cnt = sum(1 for alpha in range(1, p)
              if any(i == idx for i, _ in survive_by_alpha[alpha]))
    print(f"  cw{idx}: d={d} paired={paired} unp={unp} "
          f"survive={cnt}/{p-1} ({100*cnt/(p-1):.1f}%)")

# Multi-round folding
print(f"\nMulti-round folding (20 trials):")
random.seed(777)
for trial in range(20):
    cur_c = center[:]
    cur_list = [(co[:], va[:], d) for co, va, d in cws]
    cur_n, cur_k = n, k
    cur_om = omega
    chain = [len(cur_list)]

    while cur_n >= 4 and cur_k >= 2 and len(cur_list) > 0:
        al = random.randrange(1, p)
        nn, nk = cur_n//2, cur_k//2
        if nk < 1: break
        nw = max(1, int(math.floor((1-math.sqrt(nk/nn))*nn)))
        nom = pow(cur_om, 2, p)
        npw = [pow(nom, i, p) for i in range(nn)]

        nc = []
        for i in range(nn):
            fi, fi2 = cur_c[i], cur_c[i+nn]
            fe = (fi+fi2)*inv2%p
            inv_oi = pow(pow(cur_om,i,p), p-2, p)
            fo = (fi-fi2)*inv2%p * inv_oi%p
            nc.append((fe+al*fo)%p)

        nl = []
        for co, va, d in cur_list:
            fc = fold_poly(co, al, cur_k)
            fv = eval_poly(fc, npw)
            df = hdist(fv, nc)
            if df <= nw:
                nl.append((fc, fv, df))

        cur_c, cur_list = nc, nl
        cur_n, cur_k, cur_om = nn, nk, nom
        chain.append(len(cur_list))

    print(f"  trial {trial}: M chain = {chain}")

# Also look at the folded list size on L' independently
# (find codewords of RS[6,3] close to g_alpha on L')
print(f"\nIndependent folded list size (RS[{n2},{k2}] on L'):")
print(f"Building all RS[{n2},{k2}] codewords ({p}^{k2}={p**k2})...")
all_cws2 = []
for ct in iprod(range(p), repeat=k2):
    vals = eval_poly(list(ct), pw2)
    all_cws2.append(vals)
print(f"  Done: {len(all_cws2)}")

# For a few alpha values, compute full folded list size
for alpha in [1, 2, 5, 7, 11]:
    gc = fold_center(center, alpha)
    M_fold = sum(1 for v in all_cws2 if hdist(v, gc) <= w2)
    # Also count survivors from original list
    survs = len(survive_by_alpha.get(alpha, []))
    print(f"  alpha={alpha}: M_fold(independent)={M_fold}, survivors={survs}")
