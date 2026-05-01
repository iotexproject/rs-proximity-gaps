#!/usr/bin/env python3 -u
"""Find a c=3 lemma-failure witness if possible.

At n=12 c=3 small p (p=61, 73), saw max_bad=4 > bound=3.
Get the witness; check if lemma fails or just small-p coincidence.
"""

import sys
import numpy as np
from itertools import combinations
sys.path.insert(0, 'notes/scripts')
from op2_max_bad_phase_diagram import find_omega, elp, precompute_NE
from op2_verify_lemma_at_c2 import find_witness, check_lemma

if __name__ == '__main__':
    # n=12 c=3 — borderline failure
    for n, k, c in [(12, 6, 3), (16, 8, 3)]:
        print(f"\n=== n={n} k={k} c={c} ===")
        D = n - k; w = D - c
        bound = (2*D - 1) // c
        # Try multiple primes
        from op2_max_bad_phase_diagram import primes_dividing_minus1
        primes = primes_dividing_minus1(n, 50, 1000)[:6]
        print(f"  primes: {primes}, bound={bound}")

        for p in primes:
            print(f"\n  --- p={p} ---")
            data = find_witness(n, k, c, p, n_trials=200000)
            if data is None:
                continue
            print(f"  best m at p={p}: {data['m']}")
            if data['m'] > bound:
                print(f"  *** EXCEEDS BOUND {bound} — checking lemma ***")
                check_lemma(data, n, k, c, p)
