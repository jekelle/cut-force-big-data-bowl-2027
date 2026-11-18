import pandas as pd, numpy as np, pickle
from scipy import stats
src=open('../nb_src.py').read()
exec(src[src.index('def smooth'):src.index('# %% [markdown]\n# ## 2.')])
G=9.80665/0.9144
D='/mnt/user-data/uploads/Downloads/bdb2027/nfl-big-data-bowl-2027/'
players=pd.read_csv(D+'players.csv'); ct=pickle.load(open('db_ct.pkl','rb'))
DR=['BACK_PEDAL_AND_90_DEGREE_BREAK_TO_BALL','BACK_PEDAL_AND_TRANSITION_45_DEGREE_REACTION','BOX_DRILL','W_DRILL','TERYL_AUSTIN_DRILL_1','TERYL_AUSTIN_DRILL_2']
ct=ct[ct.drill_name.isin(DR)]
out=[]
for (pid,ev,att,dr,yr),d in ct.groupby(['nfl_id','event_id','attempt','drill_name','draft_year']):
    d=d.sort_values('time'); f=cut_force(d.s.values,d.dir.values)
    if f: out.append(dict(nfl_id=pid,drill=dr,draft_year=yr,g=f['cut_force']/G,vmax=d.s.max()))
o=pd.DataFrame(out); grp=o.groupby(['drill','draft_year']).g
o['res']=(o.g-grp.transform('mean'))/grp.transform('std')
print(o.groupby('drill').g.agg(['mean','std','size']).round(3))
rng=np.random.default_rng(2027); drills=sorted(o.drill.unique()); rs=[]
for _ in range(500):
    h=set(rng.choice(drills,len(drills)//2,replace=False))
    a=o[o.drill.isin(h)].groupby('nfl_id').res.mean(); b=o[~o.drill.isin(h)].groupby('nfl_id').res.mean()
    j=pd.concat([a,b],axis=1).dropna(); r=j.iloc[:,0].corr(j.iloc[:,1]); rs.append(2*r/(1+r))
print('DB reliability',np.median(rs).round(3),np.percentile(rs,[25,75]).round(2),'players',o.nfl_id.nunique(),'reps/player',round(o.groupby('nfl_id').size().mean(),1))
# drill-by-drill intercorrelation
w=o.groupby(['nfl_id','drill']).res.mean().unstack(); print(w.corr().round(2))
o.to_pickle('db_reps.pkl')
