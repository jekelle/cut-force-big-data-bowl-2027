import json, numpy as np, matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
R = json.load(open('out/phase_results.json'))
NAVY, GOLD, GRAY = '#13294B', '#B08400', '#6B7280'
plt.rcParams.update({'font.size': 13, 'savefig.dpi': 220, 'axes.titleweight': 'bold', 'axes.titlelocation': 'left', 'axes.titlesize': 15})
rows = [('decel', 'Deceleration into the break'), ('cut', 'Cut Force (at the break)'), ('accel', 'Acceleration out of the break'),
        ('kept', 'Speed kept through the break')]
cols = ['Combine\nreliability', 'NFL game\nreliability', 'Combine to\nNFL r', 'Overlap with\nstopwatch, max |r|\n(lower = newer)', 'Separation at\nthrow, yd per SD\n(p)']
M, T = [], []
for k, _ in rows:
    r = R[k]; sw = max(abs(r['r_forty']), abs(r['r_ten_yd_split']), abs(r['r_three_cone']), abs(r['r_short_shuttle']))
    M.append([r['combine_rel'], r['game_rel'], r['transfer_r'], 1 - sw, None])
    T.append([f"{r['combine_rel']:.2f}", f"{r['game_rel']:.2f}", f"{r['transfer_r']:+.2f}", f"{sw:.2f}", f"{r['sep_b']:+.03f} ({r['sep_p']:.2f})"])
rows.append(('db', 'Defensive back Cut Force'))
M.append([0.28, 0.13, -0.05, None, None]); T.append(['0.28', '0.13', '-0.05', 'not tested', '-0.05 (0.42)'])
cmap = LinearSegmentedColormap.from_list('c', ['#F3F4F6', '#C9D3E3', NAVY])
fig, ax = plt.subplots(figsize=(12.5, 5.3))
ax.set_xlim(-0.5, len(cols) - 0.5); ax.set_ylim(len(rows) - 0.5, -0.5); ax.axis('off')
scale = [(0, 0.7), (0, 0.8), (-0.1, 0.35), (0.4, 1.0)]
for i, (k, lab) in enumerate(rows):
    for j in range(len(cols)):
        v = M[i][j]
        if v is None or j == 4:
            fc = '#FFFFFF'; tc = GRAY if (j < 4) else '#1A1A1A'
        else:
            lo, hi = scale[j]; x = min(1, max(0, (v - lo) / (hi - lo))); fc = cmap(x); tc = 'white' if x > 0.6 else '#1A1A1A'
        ax.add_patch(plt.Rectangle((j - 0.48, i - 0.42), 0.96, 0.84, color=fc, ec='#E5E7EB', lw=1))
        ax.text(j, i, T[i][j], ha='center', va='center', fontsize=14 if j < 4 else 12.5, color=tc, fontweight='bold' if k == 'cut' and j < 4 else 'normal')
    ax.text(-0.56, i, lab, ha='right', va='center', fontsize=13, fontweight='bold' if k == 'cut' else 'normal', color=NAVY if k == 'cut' else '#1A1A1A')
for j, c in enumerate(cols): ax.text(j, -0.75, c, ha='center', va='bottom', fontsize=11.5, color=GRAY)
ax.add_patch(plt.Rectangle((-3.55, 0.56), len(cols) + 3.05, 0.88, fill=False, ec=GOLD, lw=2.2, clip_on=False))
ax.text(-3.5, -1.85, 'Only the cut itself is a Combine trait that carries to NFL routes', fontsize=15.5, fontweight='bold', ha='left', va='bottom')
ax.text(-3.5, 4.75, 'Darker = better. Overlap is shaded so that less overlap with the 40, 10-yard split, 3-cone, and shuttle reads darker (more new information).\n'
        'Separation is regressed on each Combine measure with weight and slot share controlled (DB row: man-coverage matchups, route and snap distance controlled).',
        fontsize=10.5, color=GRAY, ha='left', va='top')
fig.subplots_adjust(left=0.27, right=0.99, top=0.80, bottom=0.12)
fig.savefig('out/fig2_phases.png', bbox_inches='tight')
print('saved')
