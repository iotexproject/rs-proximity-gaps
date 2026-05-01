"""Theorem 6 verification: M = O(1) for power-of-2 domains."""
import sys
from math import gcd
from multiprocessing import Pool

def is_prime(n):
    if n<2: return False
    if n<4: return True
    if n%2==0 or n%3==0: return False
    d=5
    while d*d<=n:
        if n%d==0 or n%(d+2)==0: return False
        d+=6
    return True

def prime_factors(n):
    out=set(); d=2; nn=n
    while d*d<=nn:
        while nn%d==0: out.add(d); nn//=d
        d+=1
    if nn>1: out.add(nn)
    return list(out)

def find_omega(p,n):
    pf=prime_factors(p-1)
    for g in range(2,p):
        if all(pow(g,(p-1)//q,p)!=1 for q in pf):
            return pow(g,(p-1)//n,p)

def modinv(a,p): return pow(a,p-2,p)

def find_proper_prime(n, min_ratio=3):
    p=n*min_ratio+1
    while True:
        if p%n==1 and is_prime(p): return p
        p+=1

def sweep_lam(args):
    lam, L, n, p, t = args
    c=[(pow(L[i],6,p)+lam*pow(L[i],5,p))%p for i in range(n)]
    seen=set(); M=0
    for i in range(n):
        for j in range(i+1,n):
            dx=(L[j]-L[i])%p; dy=(c[j]-c[i])%p
            h1=(dy*modinv(dx,p))%p; h0=(c[i]-h1*L[i])%p
            key=(h0,h1)
            if key in seen: continue
            seen.add(key)
            ag=sum(1 for idx in range(n) if (h0+h1*L[idx])%p==c[idx])
            if ag>=t: M+=1
    return M

def main():
    t=6
    import random; random.seed(42)

    print(f"Power-of-2 domains: gcd(t-1,n)=gcd(5,2^k)=1")
    print(f"{'n':>6} {'p':>8} {'max_M':>6} {'samples':>8}")
    print("-"*35)

    for k in [5,6,7,8,9]:
        n=2**k; p=find_proper_prime(n,3)
        omega=find_omega(p,n); L=[pow(omega,i,p) for i in range(n)]
        samp=min(p,200) if n>64 else p
        lams=list(range(samp)) if samp==p else random.sample(range(p),samp)
        tasks=[(l,L,n,p,t) for l in lams]
        with Pool(16) as pool:
            results=pool.map(sweep_lam,tasks,chunksize=max(1,len(tasks)//64))
        print(f"{n:>6} {p:>8} {max(results):>6} {samp:>8}",flush=True)

    print(f"\nDivisible-by-5 domains: gcd(5,n)=5")
    print(f"{'n':>6} {'p':>8} {'max_M':>6} {'n/5':>5} {'samples':>8}")
    print("-"*45)

    for n in [40,80,160,320,640]:
        p=find_proper_prime(n,3); omega=find_omega(p,n)
        L=[pow(omega,i,p) for i in range(n)]
        samp=min(p,200)
        lams=random.sample(range(p),samp) if samp<p else list(range(p))
        tasks=[(l,L,n,p,t) for l in lams]
        with Pool(16) as pool:
            results=pool.map(sweep_lam,tasks,chunksize=max(1,len(tasks)//64))
        print(f"{n:>6} {p:>8} {max(results):>6} {n//5:>5} {samp:>8}",flush=True)

if __name__=="__main__":
    main()
