"""Historical context check: are the 2023 to 2025 Kaggle WR classes typical
of the 2000 to 2026 WR Combine population?

Data: analysis/nflverse_combine_2000_2026.csv (nflverse-data 'combine' release,
built from Pro Football Reference; 8,968 rows, one per participant-year).
2021 excluded (no Combine held; PFR backfilled pro-day numbers).
Columns added over the raw nflverse file: pos_group, ht_in.
"""
import pandas as pd

k = pd.read_csv('combine_results.csv')
nv = pd.read_csv('analysis/nflverse_combine_2000_2026.csv')

kw = k[k.combine_position == 'WR']
hist = nv[(nv.pos == 'WR') & (nv.season < 2023) & (nv.season != 2021)]

pairs = [('forty', 'forty'), ('vertical', 'vertical'),
         ('broad_jump', 'broad_jump'), ('combine_weight', 'wt')]
for kcol, ncol in pairs:
    a, b = kw[kcol].dropna(), hist[ncol].dropna()
    pct = (b < a.mean()).mean() * 100
    print(f"{kcol:15s} Kaggle 2023-25 mean {a.mean():7.2f} (n={len(a)}) | "
          f"WR 2000-22 mean {b.mean():7.2f} sd {b.std():5.2f} (n={len(b)}) | "
          f"Kaggle mean at {pct:.0f}th pct of historical pool")
