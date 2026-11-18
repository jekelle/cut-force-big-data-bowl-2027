import json, os, sys, types, time, pickle, re
T0 = time.time()
def log(*a): print(f'[{time.time()-T0:5.0f}s]', *a, flush=True)
try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
except Exception:
    m = types.ModuleType('matplotlib'); p = types.ModuleType('matplotlib.pyplot'); m.pyplot = p; m.use = lambda *a, **k: None
    sys.modules['matplotlib'] = m; sys.modules['matplotlib.pyplot'] = p
import pandas as pd, numpy as np
H = os.path.expanduser('~/bdbcheck')
os.environ['BDB_DATA'] = os.path.expanduser('~/mnt/Desktop/nfl-big-data-bowl-2027')
_rc = pd.read_csv
def read_csv_patched(f, *a, **k):
    mt = re.search(r'game_tracking_(\d{4})\.csv$', str(f))
    if mt:
        g = pd.read_pickle(f'{H}/gt_{mt.group(1)}.pkl'); uc = k.get('usecols')
        g = g[uc] if uc else g
        return [g] if k.get('chunksize') else g
    return _rc(f, *a, **k)
pd.read_csv = read_csv_patched
nb = json.load(open(os.path.expanduser('~/mnt/Desktop/nfl-big-data-bowl-2027/submission/cut_force_bdb2027_v20.ipynb')))
src = {i: ''.join(c['source']) for i, c in enumerate(nb['cells']) if c['cell_type'] == 'code'}
NS = {'display': lambda x: print(x.to_string() if hasattr(x, 'to_string') else x, flush=True), 'pd': pd, 'np': np}
def run(i, s=None):
    log(f'--- cell {i} ---'); exec(s if s is not None else src[i], NS)
def X(code): exec(code, NS)
c9 = src[9]; cut = c9.index("for f in sorted(glob.glob(f'{DATA}/game_tracking_*.csv')):")
post = c9.index('GF = pd.DataFrame(gfe)')
C9_PRE, C9_LOOP, C9_POST = c9[:cut], c9[cut:post], c9[post:]
stage = sys.argv[1]
for i in [1, 3, 5, 7]:
    exec(src[i], NS)
log('common done')
if stage == 'g1':
    run(9)
    pickle.dump({k: NS[k] for k in ['GF', 'ALIGN', 'gph', 'P', 'REL_G', 'r_t', 'p_t']}, open(f'{H}/state9.pkl', 'wb'))
    log('saved state9')
else:
    X(C9_PRE)
    NS.update(pickle.load(open(f'{H}/state9.pkl', 'rb')))
    log('loaded state9')
    if stage not in ('g2', 't20', 't20b'):
        NS.update(pickle.load(open(f'{H}/state11.pkl', 'rb'))); log('loaded state11')
if stage == 'g2':
    run(11)
    pickle.dump({k: NS[k] for k in ['S', 'P', 'F']}, open(f'{H}/state11.pkl', 'wb'))
    X("import numpy as np; p0 = S.tgt.mean(); bc = np.array([0.1]); dpts = np.array([0.0187])")
    run(17)
    X('''
for nm, m in [('EPA', m_epa), ('YAC', m_yac), ('SNAPS', m_snp)]:
    ci = m.conf_int().loc['cf_z']; print(nm, 'b', f'{m.params.cf_z:.6f}', 'ci', f'{ci[0]:.6f}', f'{ci[1]:.6f}', 'p', f'{m.pvalues.cf_z:.6f}')
print('YAC baseline', T2.yacoe.mean(), 'n', len(T2), 'EPA base', T.expected_points_added.mean(), 'n', len(T), 'snaps median', Q.snaps_py.median())
''')
    run(19)
    run(26)
    X('''
o15 = W[(W.cf_z > 1.5)]; print('cf_z > 1.5:', len(o15)); print(o15[['display_name','cf_z','rr','tprr_pct','game_pct']].sort_values('cf_z', ascending=False).to_string())
print('median', med, 'n 100+', (P.rr >= 100).sum())
''')
    pickle.dump({k: NS[k] for k in ['S', 'P', 'F']}, open(f'{H}/state11.pkl', 'wb'))
    log('saved state11 (with P after 17/19)')
if stage == 'g3':
    s15 = src[15].replace("trace_wo = fit_target_model(S_wo); _ = report(trace_wo, S_wo, 'Without Nacua')", "")
    run(15, s15)
    X('''
ls_ = sorted(zip(loo, S.nfl_id.unique())); nm = P.set_index('nfl_id').display_name
print('LOO lowest 4:', [(round(v, 4), nm.get(i)) for v, i in ls_[:4]]); print('LOO highest 3:', [(round(v, 4), nm.get(i)) for v, i in ls_[-3:]])
''')
if stage == 'g4':
    X("NAVY, GOLD, GRAY, LIGHT = '#13294B', '#B08400', '#6B7280', '#E9ECF1'\ndef panel(ax, letter): pass")
    try:
        run(30)
    except Exception as e:
        print('fig error (ignored):', repr(e)[:120])
    X('''
print('QL quintiles:'); print(QL.assign(pct=QL.d / bsd * 100, ci=1.96 * QL.se / bsd * 100).to_string())
print('cum_hsr quantiles', X12.cum_hsr.quantile([.2, .4, .6, .8, .9, .95]).round(0).to_dict(), 'WL n', len(WL))
''')
if stage == 'g5':
    X("cres = pd.read_csv(f'{DATA}/combine_results.csv')[['nfl_id', 'forty', 'combine_weight']]")
    run(32)
    X('''
t = T10.dropna(subset=['f10']); print('40-model snaps', len(t), 'DBs', t.db.nunique())
t2 = T10.dropna(subset=['db_cf_z']); print('CF-model snaps', len(t2), 'DBs', t2.db.nunique()); print('DB transfer n', len(qd))
''')
log('END')
if stage == 'g6':
    run(28)
    X('''
pos2 = players.set_index('nfl_id').nfl_position
dlp = TRR[TRR.drill.isin(DLD)].nfl_id.unique(); olp = TRR[TRR.drill.isin(OLD)].nfl_id.unique()
print('players with DL drills:', len(dlp), 'DL positions:', int(pos2.reindex(dlp).isin(['DT','DE','NT','OLB']).sum()), pos2.reindex(dlp).value_counts().to_dict())
print('players with OL drills:', len(olp), 'OL positions:', int(pos2.reindex(olp).isin(['G','T','C']).sum()), pos2.reindex(olp).value_counts().to_dict())
''')
    a37 = src[37]; a37 = a37[:a37.index("X = P[[")]
    run(37, a37)
    X('''
sc = {}
for m in ['peak','single','peak5','first','meanturn','impulse']:
    o = AR.dropna(subset=[m]).copy(); gq = o.groupby(['drill','draft_year'])[m]
    o['res'] = (o[m] - gq.transform('mean')) / gq.transform('std'); sc[m] = eb_shrink(o, 'res')
SC = pd.DataFrame(sc); print(SC.corr().round(3).to_string())
''')
    log('END g6')
if stage == 'g7':
    run(34)
    X('''
import pickle
SF = pickle.load(open('S_season_fixed.pkl', 'rb'))
SP2 = SF.merge(PP[['nfl_id'] + [m + '_cz' for m in PH_LAB]].rename(columns={m + '_cz': m + '_ph' for m in PH_LAB}), on='nfl_id')
gj2 = smf.glm(F.replace('cf_z', ' + '.join(m + '_ph' for m in PH_LAB)), SP2, family=sm.families.Binomial()).fit(cov_type='cluster', cov_kwds={'groups': SP2.nfl_id})
print('Joint model with NFL season:', {m: (round(np.exp(gj2.params[m + '_ph']), 3), round(gj2.pvalues[m + '_ph'], 4)) for m in PH_LAB})
print('Joint model as coded      :', {m: (round(np.exp(gj.params[m + '_ph']), 3), round(gj.pvalues[m + '_ph'], 4)) for m in PH_LAB})
SF['brk'] = SF.route_ran.isin(BREAK).astype(int)
gi2 = smf.glm(F.replace('cf_z', 'cf_z*brk'), SF, family=sm.families.Binomial()).fit(cov_type='cluster', cov_kwds={'groups': SF.nfl_id})
print('breaking interaction p (season fixed):', gi2.pvalues.get('cf_z:brk'), 'coef', gi2.params.get('cf_z:brk'))
gi1 = smf.glm(F.replace('cf_z', 'cf_z*brk'), S.assign(brk=S.route_ran.isin(BREAK).astype(int)), family=sm.families.Binomial()).fit()
print('breaking interaction (as coded, non-robust) coef', gi1.params.get('cf_z:brk'), 'p', gi1.pvalues.get('cf_z:brk'))
''')
if stage == 't20':
    run(11)
    print('season values', NS['S'].season.value_counts().sort_index().to_dict())
    X("import numpy as np; p0 = S.tgt.mean(); bc = np.array([0.1]); dpts = np.array([0.0187])")
    run(17); run(19); run(28)
    X("NAVY, GOLD, GRAY, LIGHT = '#13294B', '#B08400', '#6B7280', '#E9ECF1'\ndef panel(ax, letter): pass")
    try:
        run(30)
    except Exception as e:
        print('fig error (ignored):', repr(e)[:100])
    log('t20 part 1 done')
if stage == 't20b':
    run(11); X("import numpy as np; p0 = S.tgt.mean(); bc = np.array([0.1]); dpts = np.array([0.0187])"); run(17); run(19)
    run(37)
    log('t20b done')
