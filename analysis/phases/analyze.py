import numpy as np, pandas as pd, statsmodels.api as sm, statsmodels.formula.api as smf, json
from scipy import stats
D = '/home/claude/bdb3/data'; OUT = '/home/claude/bdb3/out'; SEED = 2027
METRICS = ['decel', 'cut', 'accel', 'kept']
LAB = {'decel': 'Deceleration into the break', 'cut': 'Cut Force (at the break)', 'accel': 'Acceleration out of the break', 'kept': 'Speed kept through the break'}
players = pd.read_csv(f'{D}/players.csv'); cr = pd.read_csv(f'{D}/combine_results.csv').drop_duplicates('nfl_id')
CB = pd.read_csv(f'{OUT}/combine_phases.csv').merge(players[['nfl_id', 'draft_year']], on='nfl_id')
GP = pd.read_csv(f'{OUT}/game_phases.csv')

def eb(df, col, by='nfl_id'):
    g = df.groupby(by)[col].agg(['mean', 'count', 'var']); wv = np.nanmean(g['var']); t2 = max(1e-9, g['mean'].var() - wv / g['count'].mean())
    return (t2 / (t2 + wv / g['count'])) * g['mean']
def split_half(o, col, n=500, seed=SEED):
    r_ = np.random.default_rng(seed); drills = sorted(o.drill.unique()); rs = []
    for _ in range(n):
        h = set(r_.choice(drills, len(drills) // 2, replace=False))
        a = o[o.drill.isin(h)].groupby('nfl_id')[col].mean(); b = o[~o.drill.isin(h)].groupby('nfl_id')[col].mean()
        j = pd.concat([a, b], axis=1).dropna(); r = j.iloc[:, 0].corr(j.iloc[:, 1]); rs.append(2 * r / (1 + r))
    return np.array(rs)

res = {}
P = players[players.nfl_id.isin(CB.nfl_id)][['nfl_id', 'display_name', 'draft_overall_pick']].copy()
P = P.merge(cr[['nfl_id', 'forty', 'ten_yd_split', 'three_cone', 'short_shuttle', 'combine_weight']], on='nfl_id', how='left')
P['lpick'] = np.log(P.draft_overall_pick.fillna(262))
for m in METRICS:
    grp = CB.groupby(['drill', 'draft_year'])[m]
    CB[m + '_r'] = (CB[m] - grp.transform('mean')) / grp.transform('std')
    rel = float(np.median(split_half(CB, m + '_r')))
    z = eb(CB, m + '_r').rename(m + '_cz'); P = P.merge(z, left_on='nfl_id', right_index=True, how='left')
    P[m + '_cz'] = (P[m + '_cz'] - P[m + '_cz'].mean()) / P[m + '_cz'].std()
    GP[m + '_res'] = smf.ols(f'{m} ~ C(route) + entry', GP.dropna(subset=[m])).fit().resid
    GP['half'] = GP.groupby('nfl_id').cumcount() % 2
    h = GP.groupby(['nfl_id', 'half'])[m + '_res'].mean().unstack(); r = h[0].corr(h[1]); relg = 2 * r / (1 + r)
    P = P.merge(eb(GP.dropna(subset=[m + '_res']), m + '_res').rename(m + '_gz'), left_on='nfl_id', right_index=True, how='left')
    q = P.dropna(subset=[m + '_gz', m + '_cz']); rt, pt = stats.pearsonr(q[m + '_cz'], q[m + '_gz'])
    ind = {}
    for v in ['forty', 'ten_yd_split', 'three_cone', 'short_shuttle', 'combine_weight', 'lpick']:
        qq = P.dropna(subset=[v, m + '_cz']); ind[v] = round(stats.pearsonr(qq[v], qq[m + '_cz'])[0], 2)
    res[m] = dict(label=LAB[m], combine_rel=round(rel, 2), game_rel=round(relg, 2), transfer_r=round(rt, 2), transfer_p=round(pt, 3), n=len(q),
                  combine_mean=round(CB[m].mean(), 3), game_mean=round(GP[m].mean(), 3), **{'r_' + k: v for k, v in ind.items()})

# inter-phase correlations (Combine player level)
res['corr_combine'] = P[[m + '_cz' for m in METRICS]].corr().round(2).to_dict()

# outcomes: separation over expected and targets per route, same controls as the notebook
pp = pd.read_csv(f'{D}/player_play.csv', low_memory=False); games = pd.read_csv(f'{D}/games.csv')
pp = pp[pp.game_id.isin(games.loc[games.season_type == 'REG', 'game_id'])]
WR = set(players.loc[players.nfl_position == 'WR', 'nfl_id'])
S = pp[pp.nfl_id.isin(WR) & pp.route_ran.notna() & (pp.play_nullified_by_penalty != 'Y')].copy()
# alignment from snap y in the reduced tracking
al = []
for y in (2023, 2024, 2025):
    g = pd.read_csv(f'{D}/wr_all_{y}.csv.gz', usecols=['game_id', 'play_id', 'nfl_id', 'y', 'event'])
    sn = g[g.event == 'ball_snap'].drop_duplicates(['game_id', 'play_id', 'nfl_id'])
    al.append(sn.assign(side_dist=np.minimum(sn.y, 53.3 - sn.y))[['game_id', 'play_id', 'nfl_id', 'side_dist']])
S = S.merge(pd.concat(al), on=['game_id', 'play_id', 'nfl_id'], how='left')
S['slot'] = (S.side_dist > 13).astype(float); S['cov'] = S.team_coverage_man_zone.fillna('UNK'); S['ytg'] = S.yards_to_go.clip(upper=20)
S['tgt'] = S.target.astype(str).str.lower().isin(['true', '1', '1.0']).astype(int); S['season'] = S.game_id.astype(str).str[:4].astype(int)
S = S.merge(P[['nfl_id', 'lpick', 'combine_weight'] + [m + '_cz' for m in METRICS]], on='nfl_id').dropna(subset=['cut_cz', 'slot'])
S['wt_z'] = (S.combine_weight - S.combine_weight.mean()) / S.combine_weight.std()
res['routes'] = len(S); res['receivers'] = int(S.nfl_id.nunique())
sp = S.dropna(subset=['separation_at_pass_forward', 'cushion']).copy()
ms = smf.ols('separation_at_pass_forward ~ C(route_ran)*C(cov) + C(route_ran)*slot + cushion + C(down) + ytg', sp).fit(); sp['sres'] = ms.resid
P = P.merge(eb(sp, 'sres').rename('sep_oe'), left_on='nfl_id', right_index=True, how='left')
P = P.merge(S.groupby('nfl_id').slot.mean().rename('slot_share'), left_on='nfl_id', right_index=True, how='left')
F = 'tgt ~ X + C(route_ran) + slot + C(cov) + C(down) + ytg + lpick + wt_z + C(season)'
for m in METRICS:
    q = P.dropna(subset=['sep_oe', 'combine_weight', m + '_cz'])
    msep = smf.ols(f'sep_oe ~ {m}_cz + combine_weight + slot_share', q).fit()
    # game-measured version too: does the in-game phase predict in-game separation?
    qg = P.dropna(subset=['sep_oe', 'combine_weight', m + '_gz']); qg = qg.assign(gz=(qg[m + '_gz'] - qg[m + '_gz'].mean()) / qg[m + '_gz'].std())
    mg = smf.ols('sep_oe ~ gz + combine_weight + slot_share', qg).fit()
    gl = smf.glm(F.replace('X', m + '_cz'), S, family=sm.families.Binomial()).fit(cov_type='cluster', cov_kwds={'groups': S.nfl_id})
    b, se = gl.params[m + '_cz'], gl.bse[m + '_cz']
    res[m].update(sep_b=round(msep.params[m + '_cz'], 3), sep_p=round(msep.pvalues[m + '_cz'], 3), sep_n=len(q),
                  gsep_b=round(mg.params.gz, 3), gsep_p=round(mg.pvalues.gz, 3), gsep_n=len(qg),
                  tgt_or=round(np.exp(b), 3), tgt_lo=round(np.exp(b - 1.96 * se), 3), tgt_hi=round(np.exp(b + 1.96 * se), 3), tgt_p=round(gl.pvalues[m + '_cz'], 3))
# all four together
gl4 = smf.glm(F.replace('X', ' + '.join(m + '_cz' for m in METRICS)), S, family=sm.families.Binomial()).fit(cov_type='cluster', cov_kwds={'groups': S.nfl_id})
res['joint'] = {m: dict(or_=round(np.exp(gl4.params[m + '_cz']), 3), p=round(gl4.pvalues[m + '_cz'], 3)) for m in METRICS}
P.to_csv(f'{OUT}/player_phases.csv', index=False)
json.dump(res, open(f'{OUT}/phase_results.json', 'w'), indent=1, default=float)
for m in METRICS: print(m, res[m])
print('corr', res['corr_combine']); print('joint', res['joint']); print(res['routes'], res['receivers'])
