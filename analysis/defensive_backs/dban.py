import pandas as pd, numpy as np, statsmodels.formula.api as smf
from scipy import stats
src=open('../nb_src.py').read(); exec(src[src.index('def eb_shrink'):src.index('# %% [markdown]\n# ## 2.')])
G=9.80665/0.9144; U='/mnt/user-data/uploads/nfl-big-data-bowl-2027/analysis/'; D='/mnt/user-data/uploads/Downloads/bdb2027/nfl-big-data-bowl-2027/'
F=pd.concat([pd.read_csv(U+f'db_feats_{y}.csv') for y in [2023,2024,2025]]).dropna(subset=['cf'])
M=pd.concat([pd.read_csv(U+f'db_man_{y}.csv') for y in [2023,2024,2025]])
F['g']=F.cf/G; F['covg']=F['cov'].str.replace(r'_(LEFT|RIGHT)$','',regex=True)
F['res']=smf.ols('g ~ C(covg) + entry + has_pf',F).fit().resid
F['half']=F.groupby('nfl_id').cumcount()%2
h=F.groupby(['nfl_id','half']).res.mean().unstack(); r=h[0].corr(h[1]); RELG=2*r/(1+r)
print('coverage snaps',len(F),'DBs',F.nfl_id.nunique(),'game reliability',round(RELG,2))
pl=pd.read_csv(D+'players.csv'); cr=pd.read_csv(D+'combine_results.csv').drop_duplicates('nfl_id')
P=pl[pl.nfl_position.isin(['CB','SS','FS','DB'])][['nfl_id','display_name','nfl_position','draft_year','draft_overall_pick']].copy()
P['pick']=P.draft_overall_pick.fillna(262); P['lpick']=np.log(P.pick)
P=P.merge(eb_shrink(F,'res').rename('game_cf'),left_on='nfl_id',right_index=True,how='left')
P=P.merge(F.groupby('nfl_id').size().rename('snaps'),left_on='nfl_id',right_index=True,how='left')
reps=pd.read_pickle('db_reps.pkl'); flip=pd.read_pickle('db_flip.pkl')
P=P.merge(eb_shrink(reps,'res').rename('c_cf'),left_on='nfl_id',right_index=True,how='left')
fl=flip.dropna(subset=['flipg']).copy(); gg=fl.groupby(['drill','draft_year']).flipg; fl['res']=(fl.flipg-gg.transform('mean'))/gg.transform('std')
P=P.merge(eb_shrink(fl,'res').rename('c_flip'),left_on='nfl_id',right_index=True,how='left')
for c in ['c_cf','c_flip','game_cf']: P[c+'_z']=(P[c]-P[c].mean())/P[c].std()
P=P.merge(cr[['nfl_id','forty','ten_yd_split','three_cone','short_shuttle','combine_weight','ngs_athleticism_score']],on='nfl_id',how='left')
q=P[P.snaps>=100]
for c in ['c_cf_z','c_flip_z']:
    qq=q.dropna(subset=[c,'game_cf']); print(c,'-> game_cf r=%.2f p=%.3f n=%d'%(*stats.pearsonr(qq[c],qq.game_cf),len(qq)))
for v in ['forty','ten_yd_split','short_shuttle','three_cone','combine_weight','ngs_athleticism_score','lpick']:
    out=[]
    for c in ['c_cf_z','c_flip_z','game_cf_z']:
        qq=P.dropna(subset=[v,c]); out.append('%s r=%+.2f(n=%d)'%(c,stats.pearsonr(qq[v],qq[c])[0],len(qq)))
    print(v,' | '.join(out))
# man coverage pairs
M=M.dropna(subset=['sep_pf']).merge(P[['nfl_id','game_cf_z','c_cf_z','c_flip_z','combine_weight','forty','lpick']],left_on='db',right_on='nfl_id')
M['tgt']=M.target.astype(str).str.lower().isin(['true','1']).astype(int)
print('man pairs',len(M),'DBs',M.db.nunique(),'WRs',M.wr.nunique(),'targeted',M.tgt.sum())
for x in ['game_cf_z','c_cf_z','c_flip_z']:
    mm=M.dropna(subset=[x])
    a=smf.ols(f'sep_pf ~ {x} + C(route) + snap_dist',mm).fit(cov_type='cluster',cov_kwds={'groups':mm.db})
    b=smf.logit(f'tgt ~ {x} + C(route) + snap_dist',mm).fit(disp=0,cov_type='cluster',cov_kwds={'groups':mm.db})
    print(x,'sep b=%+.3f p=%.3f | tgt OR=%.3f p=%.3f n=%d'%(a.params[x],a.pvalues[x],np.exp(b.params[x]),b.pvalues[x],len(mm)))
# 40 as a comparator
mm=M.dropna(subset=['forty']); a=smf.ols('sep_pf ~ forty + C(route) + snap_dist',mm).fit(cov_type='cluster',cov_kwds={'groups':mm.db}); print('forty sep b=%+.3f p=%.3f'%(a.params.forty,a.pvalues.forty))
P.to_pickle('P_db.pkl'); M.to_pickle('M_db.pkl'); F.to_pickle('F_db.pkl')
