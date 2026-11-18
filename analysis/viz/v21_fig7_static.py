"""Static writeup Figure 7 (Appendix G): the same two panels as the notebook's interactive version, from the same public file."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
U = '/mnt/user-data/uploads/Desktop/nfl-big-data-bowl-2027/'
NAVY, GOLD, GRAY = '#13294B', '#B08400', '#6B7280'
PG7 = {'QB': 'QB', 'RB': 'RB', 'FB': 'RB', 'WR': 'WR', 'TE': 'TE', 'OT': 'OL', 'OG': 'OL', 'C': 'OL', 'G': 'OL', 'OL': 'OL',
       'DT': 'DL', 'DL': 'DL', 'NT': 'DL', 'DE': 'EDGE', 'EDGE': 'EDGE', 'OLB': 'LB', 'ILB': 'LB', 'LB': 'LB',
       'CB': 'DB', 'S': 'DB', 'SAF': 'DB', 'DB': 'DB', 'CB/WR': 'DB'}
nv = pd.read_csv(U + 'analysis/nflverse_combine_2000_2026.csv')
nv = nv[nv.season != 2021].copy(); nv['grp'] = nv.pos.map(PG7); nv = nv[nv.grp.notna()]
hist_all = nv[(nv.pos == 'WR') & (nv.season < 2023)]
nv = nv.dropna(subset=['forty', 'vertical'])
med = nv.groupby('grp').agg(forty=('forty', 'median'), vertical=('vertical', 'median'), wt=('wt', 'median')).reset_index()
hist = nv[(nv.pos == 'WR') & (nv.season < 2023)]
cr = pd.read_csv(U + 'combine_results.csv').drop_duplicates('nfl_id'); kag_all = cr[cr.combine_position == 'WR']; kag = kag_all.dropna(subset=['forty', 'vertical'])
plt.rcParams.update({'font.family': 'DejaVu Sans', 'axes.spines.top': False, 'axes.spines.right': False, 'axes.titleweight': 'bold', 'axes.titlelocation': 'left',
                     'font.size': 13, 'axes.titlesize': 15, 'axes.labelsize': 13.5, 'xtick.labelsize': 12, 'ytick.labelsize': 12, 'legend.fontsize': 11.5,
                     'axes.grid': True, 'grid.color': '#E5E7EB', 'grid.linewidth': 0.8, 'axes.axisbelow': True})
fig, ax = plt.subplots(1, 2, figsize=(13, 5.3), gridspec_kw={'width_ratios': [1.15, 1]})
a = ax[0]
a.scatter(nv.forty, nv.vertical, s=7, color='#C4CAD3', alpha=0.35, lw=0)
sz = 60 + (med.wt - med.wt.min()) / (med.wt.max() - med.wt.min()) * 420
a.scatter(med.forty, med.vertical, s=sz, color=[GOLD if g == 'WR' else NAVY for g in med.grp], ec='white', lw=1.5, zorder=4)
OFF = {'WR': (-0.17, 3.2), 'DB': (-0.2, -3.6), 'RB': (0.02, 4.4), 'LB': (0.14, 3.8), 'TE': (0.18, 2.6), 'QB': (0.2, 1.0), 'EDGE': (-0.03, -4.4), 'DL': (0.12, 4.0), 'OL': (0.16, 3.2)}
for r in med.itertuples():
    dx, dy = OFF.get(r.grp, (0.1, 3))
    a.annotate(r.grp, (r.forty, r.vertical), (r.forty + dx, r.vertical + dy), fontsize=12.5, fontweight='bold', color=GOLD if r.grp == 'WR' else NAVY,
               ha='center', va='center', arrowprops=dict(arrowstyle='-', color='#9CA3AF', lw=0.9), bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85), zorder=5)
a.set_xlim(4.2, 5.65); a.set_ylim(17, 46.5)
a.set_xlabel('40-yard dash (s), faster to the left'); a.set_ylabel('Vertical jump (in)')
a.set_title('Participants with a 40 and a vertical, by position'); a.text(-0.12, 1.04, 'A', transform=a.transAxes, fontsize=17, fontweight='bold')
a.text(0.99, 0.02, f'n = {len(nv):,}; dot size = median weight (lb)', transform=a.transAxes, ha='right', fontsize=11, color=GRAY)
b = ax[1]
b.scatter(hist.forty, hist.vertical, s=16, color='#B8BEC8', alpha=0.55, lw=0, label=f'Combine receivers, 2000 to 2022 (n = {len(hist)})')
b.scatter(kag.forty, kag.vertical, s=26, color=NAVY, alpha=0.85, ec='white', lw=0.5, label=f"The competition's 2023 to 2025 receivers (n = {len(kag)})", zorder=3)
for d, col, lab, off in [(hist_all, GRAY, '2000 to 2022 mean', (0.075, -4.6)), (kag_all, GOLD, '2023 to 2025 mean', (-0.07, 5.0))]:
    mx, my = d.forty.mean(), d.vertical.mean()
    b.scatter([mx], [my], marker='X', s=230, color=col, ec='white', lw=1.4, zorder=5)
    b.annotate(f'{lab}\n{mx:.2f} s, {my:.1f} in', (mx, my), (mx + off[0], my + off[1]), fontsize=11.5, color='#1A1A1A', ha='center', va='center',
               arrowprops=dict(arrowstyle='-', color='#9CA3AF', lw=0.9), bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=col, lw=1.2), zorder=6)
b.set_xlim(4.2, 4.85); b.set_ylim(25, 46.5); b.set_yticks(range(25, 46, 5))
b.set_xlabel('40-yard dash (s), faster to the left'); b.set_ylabel('Vertical jump (in)')
b.set_title('Receivers: this study against 2000 to 2022'); b.text(-0.12, 1.04, 'B', transform=b.transAxes, fontsize=17, fontweight='bold')
b.legend(frameon=False, loc='upper right', fontsize=11)
plt.tight_layout(); plt.savefig('fig7_combine.png', dpi=220, bbox_inches='tight', facecolor='white')
print('plotted hist', len(hist), 'study', len(kag), '| means hist', round(hist_all.forty.mean(), 3), round(hist_all.vertical.mean(), 2), 'study', round(kag_all.forty.mean(), 3), round(kag_all.vertical.mean(), 2))
