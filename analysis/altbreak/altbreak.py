import sys, json, numpy as np, pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
IN = sys.argv[1]; OUT = sys.argv[2]
G = 9.80665 / 0.9144; SEED = 2027
DR = ['COMEBACK_ROUTE_RIGHT','CURL_ROUTE_RIGHT','DAGGER_ROUTE_LEFT','POST_CORNER_ROUTE_LEFT','POST_CORNER_ROUTE_RIGHT','SLANT_ROUTE_LEFT','SLOT_SAIL_ROUTE_RIGHT','SLOT_STRIKE_ROUTE_LEFT','SPEED_OUT_ROUTE_LEFT','SPEED_OUT_LEFT']
def smooth(x, k=3): return pd.Series(x).rolling(k, center=True, min_periods=1).mean().to_numpy()

def measures(s, d, hz=10, min_speed=3.0):
    s = np.asarray(s, float); n = len(s)
    if n < 15: return None
    out = {}
    for k_s in (3, 5):
        head = smooth(np.degrees(np.unwrap(np.radians(np.asarray(d, float)))), k_s); spd = smooth(s, k_s)
        lat = spd * np.radians(np.abs(np.gradient(head) * hz)); ok = (spd > min_speed) & (np.arange(n) > 8)
        if ok.sum() < 4: return None
        L = np.where(ok, lat, 0.0); k = int(np.argmax(L)); win = lat[max(0, k-3):k+4]
        if k_s == 3:
            out['peak'] = np.mean(np.sort(win)[-3:]) / G
            out['single'] = lat[k] / G
            # first break at 60% of max
            thr = 0.6 * L.max(); pk = [i for i in range(1, n-1) if L[i] >= thr and L[i] >= L[i-1] and L[i] >= L[i+1]]
            kf = pk[0] if pk else k; out['first'] = np.mean(np.sort(lat[max(0, kf-3):kf+4])[-3:]) / G
            # turn window: contiguous frames around k with lat >= 50% of peak
            a = k
            while a > 0 and lat[a-1] >= 0.5 * lat[k]: a -= 1
            b = k
            while b < n-1 and lat[b+1] >= 0.5 * lat[k]: b += 1
            seg = lat[a:b+1]
            out['impulse'] = seg.sum() / hz / G          # integrated lateral acceleration across the turn (g*s)
            out['meanturn'] = seg.mean() / G              # mean lateral acceleration across the turn
            out['duration'] = (b - a + 1) / hz            # seconds in the turn
            acc = np.gradient(spd) * hz
            pre, post = acc[max(0, k-10):k+1], acc[k:k+11]
            entry = spd[max(0, k-8):k+1].max(); low = spd[max(0, k-3):k+4].min()
            out['decel'] = max(0.0, -pre.min()) / G; out['accel'] = (max(0.0, post.max()) / G) if len(post) > 2 else np.nan
            out['kept'] = low / entry if entry > 0 else np.nan
        else:
            out['peak5'] = np.mean(np.sort(win)[-3:]) / G
    return out

ct = pd.read_csv(f'{IN}/combine_tracking.csv', usecols=['draft_year','nfl_id','event_id','entity_type','time','drill_name','attempt','s','dir'])
ct = ct[(ct.entity_type == 'PLAYER') & ct.drill_name.isin(DR)].copy()
ct['drill_name'] = ct.drill_name.replace({'SPEED_OUT_LEFT': 'SPEED_OUT_ROUTE_LEFT'})
P = pd.read_csv(f'{IN}/players_master4.csv')
ct = ct[ct.nfl_id.isin(P.nfl_id)]
rows = []
for (pid, ev, att, dr, yr), d in ct.groupby(['nfl_id','event_id','attempt','drill_name','draft_year']):
    d = d.sort_values('time'); f = measures(d.s.values, d.dir.values)
    if f: rows.append(dict(nfl_id=pid, drill=dr, draft_year=yr, **f))
R = pd.DataFrame(rows); print('reps', len(R), 'players', R.nfl_id.nunique())
M = ['peak','first','single','peak5','impulse','meanturn','duration','decel','accel','kept']
LAB = {'peak':'Peak Cut Force (primary: top 3 frames at the largest peak)','first':'First break only (first peak at 60% of max)','single':'Single peak frame (no 3-frame average)','peak5':'Peak with 5-frame smoothing','impulse':'Integrated lateral acceleration across the turn','meanturn':'Mean lateral acceleration across the turn','duration':'Turn duration (seconds above half peak)','decel':'Deceleration into the break','accel':'Acceleration out of the break','kept':'Speed kept through the break'}

def eb(df, col):
    g = df.groupby('nfl_id')[col].agg(['mean','count','var']); wv = np.nanmean(g['var']); t2 = max(1e-9, g['mean'].var() - wv / g['count'].mean())
    return (t2 / (t2 + wv / g['count'])) * g['mean']
def split_half(o, col, n=400):
    rng = np.random.default_rng(SEED); drills = sorted(o.drill.unique()); rs = []
    for _ in range(n):
        h = set(rng.choice(drills, len(drills)//2, replace=False))
        a = o[o.drill.isin(h)].groupby('nfl_id')[col].mean(); b = o[~o.drill.isin(h)].groupby('nfl_id')[col].mean()
        j = pd.concat([a, b], axis=1).dropna(); r = j.iloc[:,0].corr(j.iloc[:,1]); rs.append(2*r/(1+r))
    return float(np.median(rs))

yr = ct.groupby('nfl_id').draft_year.first().rename('draft_year')
X = P.merge(yr, left_on='nfl_id', right_index=True)
res = {}
for m in M:
    o = R.dropna(subset=[m]).copy(); grp = o.groupby(['drill','draft_year'])[m]
    o['z'] = (o[m] - grp.transform('mean')) / grp.transform('std')
    rel = split_half(o, 'z'); z = eb(o, 'z').rename('mz'); Xm = X.merge(z, left_on='nfl_id', right_index=True)
    Xm['mz'] = (Xm.mz - Xm.mz.mean()) / Xm.mz.std()
    q = Xm.dropna(subset=['game_cf']); tr = stats.pearsonr(q.mz, q.game_cf)
    q = Xm.dropna(subset=['forty']); r40 = stats.pearsonr(q.mz, q.forty)[0]
    q = Xm.dropna(subset=['three_cone']); r3 = stats.pearsonr(q.mz, q.three_cone)[0]
    q = Xm[(Xm.rr >= 100)].dropna(subset=['tprr']); tp = stats.pearsonr(q.mz, q.tprr)
    # leave one draft class out at the player level
    q = Xm[(Xm.rr >= 100)].dropna(subset=['tprr','lpick','slot_share','combine_weight']).copy()
    base = 'tprr ~ lpick + slot_share + combine_weight'; folds = []; resid = []
    for y in sorted(q.draft_year.unique()):
        tr_, te = q[q.draft_year != y], q[q.draft_year == y].copy()
        if len(te) < 5: continue
        te['pb'] = smf.ols(base, tr_).fit().predict(te); te['pf'] = smf.ols(base + ' + mz', tr_).fit().predict(te)
        rb = np.sqrt(np.mean((te.tprr - te.pb)**2)); rf = np.sqrt(np.mean((te.tprr - te.pf)**2))
        rr_ = stats.pearsonr(te.mz, te.tprr - te.pb)
        folds.append(dict(held_out=int(y), n=len(te), rmse_base=round(rb*100,2), rmse_with=round(rf*100,2), resid_r=round(rr_[0],2), resid_p=round(rr_[1],3)))
        resid.append(te)
    H = pd.concat(resid); pooled = stats.pearsonr(H.mz, H.tprr - H.pb)
    rmse_b = np.sqrt(np.mean((H.tprr - H.pb)**2))*100; rmse_f = np.sqrt(np.mean((H.tprr - H.pf)**2))*100
    res[m] = dict(label=LAB[m], reps=int(len(o)), players=int(o.nfl_id.nunique()), reliability=round(rel,2), r_forty=round(r40,2), r_three_cone=round(r3,2),
                  transfer_r=round(tr[0],2), transfer_p=round(tr[1],3), transfer_n=int(len(Xm.dropna(subset=['game_cf']))),
                  tprr_r=round(tp[0],2), tprr_p=round(tp[1],3), tprr_n=int(len(Xm[(Xm.rr>=100)].dropna(subset=['tprr']))),
                  heldout=dict(folds=folds, pooled_resid_r=round(pooled[0],2), pooled_resid_p=round(pooled[1],3), n=int(len(H)), rmse_base=round(rmse_b,2), rmse_with=round(rmse_f,2)))
    print(m, res[m]['reliability'], 'transfer', res[m]['transfer_r'], 'tprr', res[m]['tprr_r'], 'held-out pooled r', res[m]['heldout']['pooled_resid_r'], 'rmse', res[m]['heldout']['rmse_base'], '->', res[m]['heldout']['rmse_with'], [ (f['held_out'], f['resid_r'], f['n']) for f in folds])
# correlation among measures at the player level
Z = pd.DataFrame({m: eb(R.dropna(subset=[m]).assign(z=lambda o: (o[m]-o.groupby(['drill','draft_year'])[m].transform('mean'))/o.groupby(['drill','draft_year'])[m].transform('std')), 'z') for m in M})
res['_corr'] = Z.corr().round(2).to_dict()
json.dump(res, open(f'{OUT}/altbreak_results.json','w'), indent=1)
Z.join(X.set_index('nfl_id')[['display_name','draft_year','game_cf','tprr','rr','lpick','forty','three_cone','combine_weight','slot_share']]).to_csv(f'{OUT}/altbreak_players.csv')
print('done')
