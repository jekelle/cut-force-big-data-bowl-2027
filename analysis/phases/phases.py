"""Break phases: deceleration into the break, Cut Force at the break, acceleration out of it.
Same rep windows, smoothing and peak rule as the notebook. Writes phase tables and prints the comparison."""
import glob, os, sys, numpy as np, pandas as pd, statsmodels.api as sm, statsmodels.formula.api as smf
from scipy import stats
D = '/home/claude/bdb3/data'; OUT = '/home/claude/bdb3/out'; os.makedirs(OUT, exist_ok=True)
G = 9.80665 / 0.9144; SEED = 2027
def smooth(x, k=3): return pd.Series(x).rolling(k, center=True, min_periods=1).mean().to_numpy()

def phases(s, d, hz=10, min_speed=3.0, win=10):
    s = np.asarray(s, float); n = len(s)
    if n < 15: return None
    head = smooth(np.degrees(np.unwrap(np.radians(np.asarray(d, float)))))
    spd = smooth(s)
    lat = spd * np.radians(np.abs(np.gradient(head) * hz))
    ok = (spd > min_speed) & (np.arange(n) > 8)
    if ok.sum() < 4: return None
    k = int(np.argmax(np.where(ok, lat, 0.0)))
    w = lat[max(0, k - 3):k + 4]
    acc = np.gradient(spd) * hz
    pre = acc[max(0, k - win):k + 1]; post = acc[k:k + win + 1]
    entry = float(spd[max(0, k - 8):k + 1].max()); low = float(spd[max(0, k - 3):k + 4].min())
    return dict(cut=float(np.mean(np.sort(w)[-3:])) / G, decel=max(0.0, -float(pre.min())) / G,
                accel=max(0.0, float(post.max())) / G if len(post) > 2 else np.nan,
                kept=low / entry if entry > 0 else np.nan, entry=entry, k=k, n=n)

players = pd.read_csv(f'{D}/players.csv'); WR = set(players.loc[players.nfl_position == 'WR', 'nfl_id'])
DRILLS = ['COMEBACK_ROUTE_RIGHT', 'CURL_ROUTE_RIGHT', 'DAGGER_ROUTE_LEFT', 'POST_CORNER_ROUTE_LEFT', 'POST_CORNER_ROUTE_RIGHT',
          'SLANT_ROUTE_LEFT', 'SLOT_SAIL_ROUTE_RIGHT', 'SLOT_STRIKE_ROUTE_LEFT', 'SPEED_OUT_ROUTE_LEFT', 'SPEED_OUT_LEFT']
METRICS = ['decel', 'cut', 'accel', 'kept']

if not os.path.exists(f'{OUT}/combine_phases.csv'):
    ct = pd.read_csv(f'{D}/combine_tracking.csv', usecols=['nfl_id', 'event_id', 'entity_type', 'time', 'drill_name', 'attempt', 's', 'dir'])
    ct = ct[(ct.entity_type == 'PLAYER') & ct.drill_name.isin(DRILLS)].copy()
    ct['drill_name'] = ct.drill_name.replace({'SPEED_OUT_LEFT': 'SPEED_OUT_ROUTE_LEFT'})
    rows = []
    for (pid, ev, att, dr), d in ct.groupby(['nfl_id', 'event_id', 'attempt', 'drill_name']):
        d = d.sort_values('time'); f = phases(d.s.values, d.dir.values)
        if f: rows.append(dict(nfl_id=pid, event_id=ev, attempt=att, drill=dr, **f))
    pd.DataFrame(rows).to_csv(f'{OUT}/combine_phases.csv', index=False)

if not os.path.exists(f'{OUT}/game_phases.csv'):
    pp = pd.read_csv(f'{D}/player_play.csv', low_memory=False, usecols=['game_id', 'play_id', 'nfl_id', 'route_ran'])
    games = pd.read_csv(f'{D}/games.csv'); pp = pp[pp.game_id.isin(games.loc[games.season_type == 'REG', 'game_id'])]
    BREAK = ['OUT', 'POST', 'CORNER', 'IN', 'CROSS', 'SLANT', 'HITCH']
    keys = pp[pp.nfl_id.isin(WR) & pp.route_ran.isin(BREAK)]
    out = []
    for f in sorted(glob.glob(f'{D}/wr_all_*.csv.gz')):
        gt = pd.read_csv(f, usecols=['game_id', 'play_id', 'nfl_id', 'time', 's', 'dir', 'event'])
        gt = gt[gt.nfl_id.isin(WR)].merge(keys, on=['game_id', 'play_id', 'nfl_id']).sort_values(['game_id', 'play_id', 'nfl_id', 'time'])
        for (g, p, n, r), d in gt.groupby(['game_id', 'play_id', 'nfl_id', 'route_ran'], sort=False):
            ev = d.event.to_numpy(); snap = np.where(ev == 'ball_snap')[0]
            if len(snap) == 0: continue
            st = snap[0]; pf = np.where(np.isin(ev, ['pass_forward', 'qb_sack', 'qb_strip_sack']))[0]; pf = pf[pf > st]
            en = pf[0] + 1 if len(pf) else st + 35
            b = phases(d.s.to_numpy()[st:en], d.dir.to_numpy()[st:en])
            if b: out.append(dict(game_id=g, play_id=p, nfl_id=n, route=r, **b))
        print(os.path.basename(f), len(out), flush=True)
    pd.DataFrame(out).to_csv(f'{OUT}/game_phases.csv', index=False)
print('features done')
