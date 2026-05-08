#!/usr/bin/env python3
"""
Proximity Gap status diagram — upgraded version of the ABF 2026/680 slide.

Layers:
  Row 1 (Status):       green / ?? / red — the ABF tri-state as drawn in the talk
  Row 2 (Zero-loss CA): BCHKS solid up to Johnson; OPEN beyond (we proved a barrier)
  Row 3 (Our theorem):  halved-threshold CA covers Johnson -> capacity with delta/2 loss

Shared delta-axis at bottom with tick marks at 0, Delta(C)/2, Johnson, Delta(C), 1.
Rendered for rate rho = 1/2 (standard FRI setting).
"""

import numpy as np
import matplotlib.pyplot as plt

rho = 0.5
delta_halfmin = (1 - rho) / 2      # unique decoding radius: 0.25
delta_J       = 1 - np.sqrt(rho)    # Johnson bound: ~0.293
delta_min     = 1 - rho             # capacity: 0.5

fig, ax = plt.subplots(figsize=(13.5, 6.2))

C_GREEN_SOLID = '#6fcf8f'
C_GREEN_HATCH = '#a8e6a8'
C_YELLOW      = '#ffe08a'
C_RED         = '#ef7d7d'
C_GRAY        = '#ececec'

# ---------------------------------------------------------------- Row 1: Status
y1 = 2.80
h1 = 0.36
ax.add_patch(plt.Rectangle((0, y1 - h1/2), delta_J, h1,
                           facecolor=C_GREEN_SOLID, edgecolor='black', lw=0.9))
ax.text(delta_J/2, y1, "PROVEN\nBCIKS'20 + BCHKS'25",
        ha='center', va='center', fontsize=9, fontweight='bold')

ax.add_patch(plt.Rectangle((delta_J, y1 - h1/2), delta_min - delta_J, h1,
                           facecolor=C_YELLOW, edgecolor='black', lw=0.9, hatch='//'))
ax.text((delta_J + delta_min)/2, y1, "OPEN  — Prize zone",
        ha='center', va='center', fontsize=10, fontweight='bold')

ax.add_patch(plt.Rectangle((delta_min, y1 - h1/2), 1 - delta_min, h1,
                           facecolor=C_RED, edgecolor='black', lw=0.9))
ax.text((delta_min + 1)/2, y1, "DISPROVEN\nCS'25, BGHKS'25, DG'25",
        ha='center', va='center', fontsize=9, fontweight='bold')

ax.text(-0.015, y1, "Status:", ha='right', va='center', fontsize=10, fontweight='bold')

# -------------------------------------------------------- Row 2: Zero-loss CA
y2 = 1.95
h2 = 0.30
ax.add_patch(plt.Rectangle((0, y2 - h2/2), delta_J, h2,
                           facecolor=C_GREEN_SOLID, edgecolor='black', lw=0.9))
ax.text(delta_J/2, y2, "BCHKS (zero-loss) — up to Johnson",
        ha='center', va='center', fontsize=9, fontweight='bold')

ax.add_patch(plt.Rectangle((delta_J, y2 - h2/2), delta_min - delta_J, h2,
                           facecolor=C_GRAY, edgecolor='black', lw=0.9, linestyle='--'))
ax.text((delta_J + delta_min)/2, y2,
        "STILL OPEN  (our Prop. 'Borderline Barrier': volume packing cannot cross)",
        ha='center', va='center', fontsize=8.5, style='italic')

ax.text(-0.015, y2, "Zero-loss CA:", ha='right', va='center', fontsize=10, fontweight='bold')

# --------------------------------------------------- Row 3: Our theorem
y3 = 1.10
h3 = 0.32
ax.add_patch(plt.Rectangle((delta_J, y3 - h3/2), delta_min - delta_J, h3,
                           facecolor=C_GREEN_HATCH, edgecolor='darkgreen', lw=1.3, hatch='///'))
ax.text((delta_J + delta_min)/2, y3,
        "OUR WORK — halved-threshold CA  (delta/2 proximity loss)",
        ha='center', va='center', fontsize=9.5, fontweight='bold', color='darkgreen')

# Downstream annotation
ax.annotate("supports FRI soundness above Johnson:\n"
            r"$\varepsilon_{\mathrm{FRI}} \leq 3R/|F| + (1-\delta/2)^q$",
            xy=((delta_J + delta_min)/2, y3 - h3/2),
            xytext=((delta_J + delta_min)/2, 0.40),
            ha='center', va='top', fontsize=8.5, color='darkgreen',
            arrowprops=dict(arrowstyle='-|>', color='darkgreen', lw=0.8))

ax.text(-0.015, y3, "Our theorem:", ha='right', va='center', fontsize=10, fontweight='bold')

# ---------------------------------------------------------------- Delta axis
y_axis = 0.02
ax.plot([0, 1], [y_axis, y_axis], 'k-', lw=1.6)
ticks = [
    (0.0,            "0",                                                       0),
    (delta_halfmin,  rf"$\Delta(C)/2$" + "\n" + f"= {delta_halfmin:.3f}\n(unique dec.)",  0),
    (delta_J,        rf"Johnson $\delta_J$" + "\n" + rf"$=1-\sqrt{{\rho}} = {delta_J:.3f}$", 0),
    (delta_min,      rf"$\Delta(C)=1-\rho$" + "\n" + f"= {delta_min:.3f}\n(capacity)",    0),
    (1.0,            "1",                                                       0),
]
for x, lbl, _ in ticks:
    ax.plot([x, x], [y_axis - 0.05, y_axis + 0.05], 'k-', lw=1.2)
    ax.text(x, y_axis - 0.10, lbl, ha='center', va='top', fontsize=8.2)

# Vertical guide lines aligning rows with axis ticks
for x in [delta_J, delta_min]:
    ax.plot([x, x], [y_axis + 0.05, 3.05], 'k:', lw=0.6, alpha=0.55)

# ------------------------------------------------------------------ Titles
ax.text(0.5, 3.55,
        "Proximity Gap on smooth RS domains  (rate $\\rho = 1/2$): where does our work sit?",
        ha='center', va='center', fontsize=12.5, fontweight='bold')
ax.text(0.5, 3.28,
        "ABF 2026/680 framing on top; BCHKS coverage in middle; our contribution on bottom",
        ha='center', va='center', fontsize=9.8, style='italic')

ax.set_xlim(-0.16, 1.04)
ax.set_ylim(-0.65, 3.75)
ax.axis('off')

plt.tight_layout()
out_png = '/Users/rc/Desktop/2026/ef1m/notes/scripts/proximity_gap_diagram.png'
out_pdf = '/Users/rc/Desktop/2026/ef1m/notes/scripts/proximity_gap_diagram.pdf'
plt.savefig(out_png, dpi=180, bbox_inches='tight')
plt.savefig(out_pdf, bbox_inches='tight')
print(f"Saved: {out_png}")
print(f"Saved: {out_pdf}")
