#!/usr/bin/env python3
"""
density_mini.py — Minimal density scaling test.
RS[n,k] rate 1/2, vary p, check M_max at each w in intermediate zone.
"""
import sys
import numpy as np
from math import sqrt, ceil
import time

def run(n, k, p):
    L = list(range(1, n + 1))
    total = p ** k
    if total > 15_000_000:
        return None

    # Generate codewords
    cw = np.zeros((total, n), dtype=np.int16)
    for idx in range(total):
        coeffs = []
        tmp = idx
        for _ in range(k):
            coeffs.append(tmp % p)
            tmp //= p
        for j, x in enumerate(L):
            val = 0
            for c in reversed(coeffs):
                val = (val * x + c) % p
            cw[idx, j] = val

    rho = k / n
    wJ = n * (1 - sqrt(rho))
    cap = n - k
    w_range = list(range(ceil(wJ), cap))

    if not w_range:
        return {}

    M_max = {w: 0 for w in w_range}
    np.random.seed(42)

    # Check centers
    nc = min(300, total)
    indices = np.random.choice(total, nc, replace=False) if total > nc else np.arange(total)
    for idx in indices:
        dists = np.sum(cw[idx].astype(np.int16) != cw, axis=1)
        for w in w_range:
            cnt = int(np.sum(dists <= w))
            if cnt > M_max[w]:
                M_max[w] = cnt

    # Random centers
    for _ in range(min(300, total)):
        u = np.random.randint(0, p, size=n, dtype=np.int16)
        dists = np.sum(u != cw, axis=1)
        for w in w_range:
            cnt = int(np.sum(dists <= w))
            if cnt > M_max[w]:
                M_max[w] = cnt

    return M_max

print("DENSITY SCALING TEST", flush=True)
print("=" * 70, flush=True)

# --- RS[8,4] rate 1/2 ---
n, k = 8, 4
primes = [11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
print(f"\nRS[{n},{k}], rate 1/2, wJ={n*(1-sqrt(0.5)):.2f}, cap={n-k}", flush=True)
print(f"{'p':>4} | p^k | M(w=3) | c=n-k-w | (n-w+1)^d/p^c | M*p^c/(n-w+1)^d", flush=True)

for p in primes:
    if p <= n: continue
    t0 = time.time()
    M = run(n, k, p)
    if M is None:
        print(f"{p:4d} | SKIP", flush=True)
        continue
    # w=3 is the only intermediate zone point for n=8,k=4
    w = 3
    m_val = M.get(w, 0)
    c = n - k - w  # =1
    d = w - c  # =2
    bezout = (n - w + 1) ** d  # 5^2=25
    pc = p ** c
    ratio = m_val * pc / bezout if bezout > 0 else 0
    density = bezout / pc
    print(f"{p:4d} | {p**k:>7d} | M={m_val:>3d} | c={c} d={d} | {density:>13.6f} | ratio={ratio:>8.4f}  ({time.time()-t0:.1f}s)", flush=True)

# --- RS[8,3] rate 3/8 ---
n, k = 8, 3
primes = [11,13,17,19,23,29,31,37,41,43,47,53,59,61,67]
print(f"\nRS[{n},{k}], wJ={n*(1-sqrt(k/n)):.2f}, cap={n-k}", flush=True)
w = 4  # intermediate zone
c_cm = n - k - w  # =1
d_cm = w - c_cm  # =3
print(f"w={w}: c={c_cm}, d={d_cm}, Bezout=(n-w+1)^d={(n-w+1)**d_cm}", flush=True)
print(f"{'p':>4} | M(w={w}) | density_pred | ratio=M*p^c/Bez", flush=True)

for p in primes:
    if p <= n: continue
    t0 = time.time()
    M = run(n, k, p)
    if M is None:
        print(f"{p:4d} | SKIP", flush=True)
        continue
    m_val = M.get(w, 0)
    bezout = (n - w + 1) ** d_cm
    pc = p ** c_cm
    ratio = m_val * pc / bezout if bezout > 0 else 0
    density = bezout / pc
    print(f"{p:4d} | M={m_val:>4d} | pred={density:>10.4f} | ratio={ratio:>8.2f}  ({time.time()-t0:.1f}s)", flush=True)

# --- RS[8,2] rate 1/4 ---
n, k = 8, 2
print(f"\nRS[{n},{k}], wJ={n*(1-sqrt(k/n)):.2f}, cap={n-k}", flush=True)
primes = [11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113,127,131]

for w in [4, 5]:
    c_cm = n - k - w
    d_cm = w - c_cm
    if d_cm <= 0: d_cm = max(1, d_cm)  # ensure positive
    bezout = (n - w + 1) ** max(d_cm, 1)
    print(f"\n  w={w}: c={c_cm}, d={d_cm}, Bezout={bezout}", flush=True)
    print(f"  {'p':>4} | M(w={w}) | pred | ratio", flush=True)

    for p in primes:
        if p <= n: continue
        M = run(n, k, p)
        if M is None: continue
        m_val = M.get(w, 0)
        pc = p ** max(c_cm, 1)
        ratio = m_val * pc / bezout if bezout > 0 else 0
        density = bezout / pc
        print(f"  {p:4d} | M={m_val:>3d} | {density:>8.5f} | {ratio:>8.2f}", flush=True)

# --- RS[10,5] rate 1/2 ---
n, k = 10, 5
primes = [11,13,17,19,23,29,31,37,41,43]
print(f"\nRS[{n},{k}], rate 1/2, wJ={n*(1-sqrt(k/n)):.2f}, cap={n-k}", flush=True)

for w in range(ceil(n*(1-sqrt(0.5))), n-k):
    c_cm = n - k - w
    d_cm = w - c_cm
    bezout = (n - w + 1) ** d_cm if d_cm > 0 else 1
    print(f"\n  w={w}: c={c_cm}, d={d_cm}, Bezout={bezout}", flush=True)
    print(f"  {'p':>4} | M | density_pred | ratio", flush=True)

    for p in primes:
        if p <= n: continue
        t0 = time.time()
        M = run(n, k, p)
        if M is None:
            print(f"  {p:4d} | SKIP", flush=True)
            continue
        m_val = M.get(w, 0)
        pc = p ** c_cm if c_cm > 0 else 1
        ratio = m_val * pc / bezout if bezout > 0 else 0
        density = bezout / pc
        print(f"  {p:4d} | M={m_val:>4d} | {density:>12.6f} | {ratio:>8.2f}  ({time.time()-t0:.1f}s)", flush=True)

# --- RS[12,6] rate 1/2 ---
n, k = 12, 6
primes = [13, 17, 19, 23, 29, 31]
print(f"\nRS[{n},{k}], rate 1/2, wJ={n*(1-sqrt(k/n)):.2f}, cap={n-k}", flush=True)

for w in range(ceil(n*(1-sqrt(0.5))), n-k):
    c_cm = n - k - w
    d_cm = w - c_cm
    bezout = (n - w + 1) ** d_cm if d_cm > 0 else 1
    print(f"\n  w={w}: c={c_cm}, d={d_cm}, Bezout={bezout}", flush=True)
    print(f"  {'p':>4} | M | pred | ratio", flush=True)

    for p in primes:
        if p <= n: continue
        t0 = time.time()
        M = run(n, k, p)
        if M is None:
            print(f"  {p:4d} | SKIP (p^k={p**k})", flush=True)
            continue
        m_val = M.get(w, 0)
        pc = p ** c_cm if c_cm > 0 else 1
        ratio = m_val * pc / bezout if bezout > 0 else 0
        density = bezout / pc
        print(f"  {p:4d} | M={m_val:>5d} | {density:>10.4f} | {ratio:>8.2f}  ({time.time()-t0:.1f}s)", flush=True)

print("\nDONE", flush=True)
