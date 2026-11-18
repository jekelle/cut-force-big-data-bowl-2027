import pickle, pandas as pd, numpy as np, statsmodels.api as sm, statsmodels.formula.api as smf, os, time
t0 = time.time()
D = os.path.expanduser('~/mnt/Desktop/nfl-big-data-bowl-2027')
st = pickle.load(open('state11.pkl', 'rb')); S = st['S'].copy(); F = st['F']; P = st['P']
games = pd.read_csv(f'{D}/games.csv')
S = S.drop(columns=['season']).merge(games[['game_id', 'season']], on='game_id', how='left')
print('season counts', S.season.value_counts().sort_index().to_dict())
def fit(D_, f):
    return smf.glm(f, D_, family=sm.families.Binomial()).fit(cov_type='cluster', cov_kwds={'groups': D_.nfl_id})
g = fit(S, F); print(f'main OR {np.exp(g.params.cf_z):.4f} [{np.exp(g.conf_int().loc["cf_z"][0]):.3f}, {np.exp(g.conf_int().loc["cf_z"][1]):.3f}] p {g.pvalues.cf_z:.4f}')
NAC = P.loc[P.display_name == 'Puka Nacua', 'nfl_id'].iloc[0]
g2 = fit(S[S.nfl_id != NAC], F); print(f'without Nacua OR {np.exp(g2.params.cf_z):.4f} p {g2.pvalues.cf_z:.4f}')
MZ = S[S['cov'].isin(['MAN_COVERAGE', 'ZONE_COVERAGE'])].copy(); MZ['man'] = (MZ['cov'] == 'MAN_COVERAGE').astype(int)
for c in ['MAN_COVERAGE', 'ZONE_COVERAGE']:
    d = MZ[MZ['cov'] == c]; mc = fit(d, F.replace(' + C(cov)', '')); print(f'{c} OR {np.exp(mc.params.cf_z):.4f} p {mc.pvalues.cf_z:.4f}')
gm = fit(MZ, F.replace('cf_z', 'cf_z*man').replace(' + C(cov)', '')); print('man x zone p', round(gm.pvalues['cf_z:man'], 3))
loo = [np.exp(smf.glm(F, S[S.nfl_id != i], family=sm.families.Binomial()).fit().params.cf_z) for i in S.nfl_id.unique()]
ls_ = sorted(loo); print('LOO', [round(v, 4) for v in ls_[:2]], round(ls_[-1], 4), 'median', round(np.median(loo), 4))
pickle.dump(S, open('S_season_fixed.pkl', 'wb'))
print('time', round(time.time() - t0))
