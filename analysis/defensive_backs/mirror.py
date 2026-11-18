import pandas as pd, numpy as np, statsmodels.formula.api as smf
from scipy import stats
src=open('../nb_src.py').read(); exec(src[src.index('def eb_shrink'):src.index('# %% [markdown]\n# ## 2.')])
U='/mnt/user-data/uploads/nfl-big-data-bowl-2027/analysis/'
R=pd.concat([pd.read_csv(U+f'db_mirror_{y}.csv') for y in [2023,2024,2025]])
M=pd.read_pickle('M_db.pkl')[['game_id','play_id','db','wr','route','tgt','snap_dist','sep_pf']]
R=R.merge(M,on=['game_id','play_id','db','wr'])
R=R[R.wr_break_g>=0.3]   # a real break
print('pairs',len(R),'DBs',R.db.nunique(), R[['lag','xlag','xcorr','sep_break','sep_after','sep_end','db_resp_g']].describe().loc[['mean','50%','std']].round(2))
for col in ['xlag','lag','db_resp_g','xcorr']:
    R[col+'_r']=smf.ols(f'{col} ~ C(route) + wr_break_g + snap_dist',R).fit().resid
    R['half']=R.groupby('db').cumcount()%2
    h=R[R.groupby('db').db.transform('size')>=10].groupby(['db','half'])[col+'_r'].mean().unstack(); r=h[0].corr(h[1])
    print(col,'odd/even rel',round(2*r/(1+r),2))
# within-play validity: does a longer lag mean more separation after the break? (play level, DB fixed effects)
for col in ['xlag','lag','db_resp_g']:
    m=smf.ols(f'sep_after ~ {col} + sep_break + C(route) + wr_break_g + C(db)',R).fit(cov_type='cluster',cov_kwds={'groups':R.db})
    print('play-level',col,'-> sep_after b=%+.3f p=%.4f'%(m.params[col],m.pvalues[col]))
R.to_pickle('R_db.pkl')
