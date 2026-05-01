"""Trace companion matrix step by step for RS[10,5] over F_11."""

sigma = [6, 1, 4, 10]
p = 11
n = 10
w = 4

state = [0] * w
state[w-1] = 1

print(f"sigma = {sigma}, p = {p}, n = {n}, w = {w}")
print(f"Initial state (x^0): {state}")

for step in range(n):
    top = state[0]
    new_state = [0] * w
    for j in range(w - 1):
        new_state[j] = state[j + 1]

    for i in range(w):
        sign = (-1) ** (i + 1)
        new_state[i] = (new_state[i] + top * sign * sigma[i]) % p

    state = new_state
    print(f"Step {step+1} (x^{step+1}): {state}")

print(f"\nFinal: R(x) = {state[0]}*x^3 + {state[1]}*x^2 + {state[2]}*x + {state[3]}")

# Verify: evaluate R at each root
L = [pow(2, i, 11) for i in range(10)]
roots = [L[4], L[5], L[7], L[9]]  # = [5, 10, 7, 6]
print(f"\nRoots: {roots}")
for r in roots:
    val = (state[0]*r**3 + state[1]*r**2 + state[2]*r + state[3]) % p
    print(f"R({r}) = {val}, ζ^{n} = {pow(r, n, p)}")
