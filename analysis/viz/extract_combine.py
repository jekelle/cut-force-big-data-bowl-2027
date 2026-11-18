"""Viz data for the Cut Force replay and explorer: the same two Figure 1 reps and player-level Combine scores.
Mirrors notebook sections 1 to 3 (cells 3, 5, 7 and the Figure 1 selection in cell 23)."""
import os, sys
import numpy as np, pandas as pd
DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
G = 9.80665 / 0.9144
SEED = 2027

def smooth(x, k=3):
    return pd.Series(x).rolling(k, center=True, min_periods=1).mean().to_numpy()

def cut_force(s, d, hz=10, frac=1.0, min_speed=3.0):
    s = np.asarray(s, float); n = len(s)
    if n < 15:
        return None
    head = smooth(np.degrees(np.unwrap(np.radians(np.asarray(d, float)))))
    spd = smooth(s)
    lat = spd * np.radians(np.abs(np.gradient(head) * hz))
    ok = (spd > min_speed) & (np.arange(n) > 8)
    if ok.sum() < 4:
        return None
    L = np.where(ok, lat, 0.0)
    if frac >= 1.0:
        k = int(np.argmax(L))
    else:
        thr = frac * L.max()
        peaks = [i for i in range(1, n - 1) if L[i] >= thr and L[i] >= L[i - 1] and L[i] >= L[i + 1]]
        k = peaks[0] if peaks else int(np.argmax(L))
    win = lat[max(0, k - 3):k + 4]
    return dict(cut_force=float(np.mean(np.sort(win)[-3:])), entry=float(spd[max(0, k - 8):k + 1].max()), k=k)

def eb_shrink(df, col, by='nfl_id'):
    g = df.groupby(by)[col].agg(['mean', 'count', 'var'])
    wv = np.nanmean(g['var']); t2 = max(1e-9, g['mean'].var() - wv / g['count'].mean())
    return (t2 / (t2 + wv / g['count'])) * g['mean']

players = pd.read_csv(f'{DATA}/players.csv')
WR = set(players.loc[players.nfl_position == 'WR', 'nfl_id'])
DRILLS = ['COMEBACK_ROUTE_RIGHT', 'CURL_ROUTE_RIGHT', 'DAGGER_ROUTE_LEFT', 'POST_CORNER_ROUTE_LEFT', 'POST_CORNER_ROUTE_RIGHT',
          'SLANT_ROUTE_LEFT', 'SLOT_SAIL_ROUTE_RIGHT', 'SLOT_STRIKE_ROUTE_LEFT', 'SPEED_OUT_ROUTE_LEFT', 'SPEED_OUT_LEFT']
ct = pd.read_csv(f'{DATA}/combine_tracking.csv',
                 usecols=['nfl_id', 'event_id', 'entity_type', 'time', 'drill_name', 'attempt', 'x', 'y', 's', 'dir'])
ct = ct[(ct.entity_type == 'PLAYER') & ct.drill_name.isin(DRILLS)].copy()
ct['drill_name'] = ct.drill_name.replace({'SPEED_OUT_LEFT': 'SPEED_OUT_ROUTE_LEFT'})
REPS = {k: d.sort_values('time') for k, d in ct.groupby(['nfl_id', 'event_id', 'attempt', 'drill_name'])}
out = []
for (pid, ev, att, dr), d in REPS.items():
    f = cut_force(d.s.values, d.dir.values)
    if f:
        out.append(dict(nfl_id=pid, event_id=ev, attempt=att, drill=dr, g=f['cut_force'] / G))
reps = pd.DataFrame(out).merge(players[['nfl_id', 'draft_year']], on='nfl_id')
grp = reps.groupby(['drill', 'draft_year']).g
reps['res'] = (reps.g - grp.transform('mean')) / grp.transform('std')
print(len(reps), 'reps', reps.nfl_id.nunique(), 'receivers')

# Figure 1 selection, exactly as in the notebook
so = reps[reps.drill == 'SPEED_OUT_ROUTE_LEFT'].sort_values('g').reset_index(drop=True)
def clean(r):
    d = REPS[(r.nfl_id, r.event_id, r.attempt, 'SPEED_OUT_ROUTE_LEFT')]
    a, b = cut_force(d.s.values, d.dir.values, frac=1.0), cut_force(d.s.values, d.dir.values, frac=0.6)
    return a is not None and b is not None and a['k'] == b['k']
so = so[[clean(r) for r in so.itertuples()]].reset_index(drop=True)
rows = []
for role, r in [('high', so.iloc[int(len(so) * .9)]), ('low', so.iloc[int(len(so) * .1)])]:
    d = REPS[(r.nfl_id, r.event_id, r.attempt, 'SPEED_OUT_ROUTE_LEFT')]
    rows.append(d.assign(role=role, g_rep=r.g, frame=np.arange(len(d)))[['role', 'nfl_id', 'event_id', 'attempt', 'frame', 'time', 'x', 'y', 's', 'dir', 'g_rep']])
    print(role, r.nfl_id, round(r.g, 3), len(d), 'frames')
pd.concat(rows).to_csv('replay_reps.csv', index=False)

P = players[players.nfl_id.isin(reps.nfl_id)][['nfl_id', 'display_name', 'draft_year', 'draft_overall_pick']].copy()
P = P.merge(eb_shrink(reps, 'res').rename('combine_cf'), left_on='nfl_id', right_index=True)
P['cf_z'] = (P.combine_cf - P.combine_cf.mean()) / P.combine_cf.std()
P = P.merge(reps.groupby('nfl_id').agg(cf_g=('g', 'mean'), n_reps=('g', 'size')), left_on='nfl_id', right_index=True)
cr = pd.read_csv(f'{DATA}/combine_results.csv').drop_duplicates('nfl_id')
P = P.merge(cr[['nfl_id', 'forty', 'combine_weight']], on='nfl_id', how='left')
P['pick'] = P.draft_overall_pick.fillna(262)
P.to_csv('combine_players.csv', index=False)
print(P.sort_values('cf_z', ascending=False).head(6)[['display_name', 'draft_year', 'pick', 'cf_z', 'forty']].to_string())
