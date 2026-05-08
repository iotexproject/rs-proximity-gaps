# paper2 L3 deployment-scale local closure — verification scripts

Companion to **paper2** §`ssec:deployment-local-closure` (Boundary-Lift
Closure + Common-Zero Stratification theorems).

These scripts verify the **L3 deployment-scale** local closure of the
Q2 LOCAL conjecture at $L_2 = (32, 8)$ (the base of the dyadic deployment
ladder $(32, 8) \to (64, 16) \to (128, 32)$ used by ABF §6.3 / KoalaBear).

Stdlib-only Python; no external dependencies. Drop-in self-contained
(see `_l3_helpers.py` for the shared mod-$p$ linear algebra and subgroup
utilities).

## Theorem coverage

| Theorem (paper2.tex label) | Script | Verifies |
|---|---|---|
| `thm:boundary-lift-closure` | `issue419_boundary_lift_universal.py` | Empirical spot check (not a universal proof): hard-coded at $(p, n_2, k_2) = (257, 32, 8)$, samples 500 random no-full configurations and the first 50 of them per $K$ parity. Verifies $\lvert \mathrm{Zeros}_{L_0}(f^{(0)}) \rvert \ge n_0/2 = \sqrt{n_0 k_0}$ for $K \in \{12, 14, 16\}$ (38 cases checked, 0 violations). The "ANY no-full" universality is established in the paper proof; this script is the sanity check. |
| `thm:boundary-lift-closure` (scale-uniform check) | `issue419_boundary_lift_L64.py` | Same theorem at $L_2 = (64, 16)$ (i.e., $L_0 = (256, 64)$). |
| `thm:common-zero-stratification` (residual stratum B) | `issue419_K16_canonical_lift.py` | Direct canonical lift verification $f^{(0)}(w) := f(w^4)$ at $K = 16$ deployment cases. |
| `thm:common-zero-stratification` (residual stratum B) | `issue419_K16_K_count.py` | Direct $K$-count via 0-codeword agreement at deployment. |
| `thm:common-zero-stratification` (stratum split) | `issue419_decouple_check.py` | Split $Z(f_u) = Z(f_v)$ vs. $\neq$ at $L_2$. |
| Empirical: $K_{\mathrm{BW}} \le 2$ across 72 K=16 stratum (B) cases at 4 primes | `issue419_case3_BW_total_K.py`, `issue419_stratum_B_empirical_K.py`, `issue419_large_K_sweep.py` | Berlekamp–Welch unique-decoding: at most 2 $\alpha$ per case admit a codeword within agreement $\ge 80$ ($n_0 = 128$). Multi-prime sweep at $\{257, 641, 769, 1153\}$. |
| Action-orbit non-stabilization (admissibility (i)) | `issue419_action_orbit_check.py` | 0/10 K=16 cases action-stabilized. |
| **GS m=2 list decode** (residual upgrade) | `issue419_GS_m2_list_decode.py` | Guruswami–Sudan multiplicity-2 list decoder at agreement $\tau \ge 71$, replacing the BW-only bound. Upgrades the empirical residue from "unique decoding" to "list decoding within $\tau \ge 71$". |

## Reproducing

Each script self-contains its main; just run:

```
cd scripts/paper2-deployment-l3
python3 issue419_boundary_lift_universal.py
python3 issue419_K16_K_count.py
python3 issue419_GS_m2_list_decode.py
# etc.
```

Outputs are saved to `../../outputs/paper2-deployment-l3/` for the
canonical scripts; or printed to stdout for the verification utilities.

## Cross-references to project notes

These scripts underpin Notes 0457–0464 in the project's `notes/`
directory:

- 0457: paper2 scope analysis resolving the K=16 residual.
- 0458: K=16 residual at Johnson boundary (revised after canonical lift check).
- 0459: K=16 residual RESOLVED via direct K-count.
- 0460: Unified L3 Boundary-Lift Closure Theorem.
- 0461: Common-Zero Stratification.
- 0462: L3 status post empirical K-survey.
- 0463: Multi-prime empirical confirmation (4 primes, 72 cases).
- 0464: HANDOFF after paper2 v22 integration.

## Honest scope

- **Stratum (A), (C)**: structurally excluded by paper2 admissibility (ii)
  and joint-boundary respectively — no script needed.
- **Stratum (B)**: closure has $K_{\mathrm{lb}} \le 6$ structural via
  the ratio-function bound (Note 0461 §2). The remaining "5% empirical
  upgrade" is the GS list-decoding bound for agreement range
  $[64, 79]$, of which the agreement $\ge 71$ part is now reachable
  via the `issue419_GS_m2_list_decode.py` script.
