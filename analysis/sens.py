import pandas as pd, numpy as np
from scipy import stats
from feats2 import feats3
D='/mnt/user-data/uploads/Downloads/bdb2027/nfl-big-data-bowl-2027/'
DR=['COMEBACK_ROUTE_RIGHT','CURL_ROUTE_RIGHT','DAGGER_ROUTE_LEFT','POST_CORNER_ROUTE_LEFT','POST_CORNER_ROUTE_RIGHT','SLANT_ROUTE_LEFT','SLOT_SAIL_ROUTE_RIGHT','SLOT_STRIKE_ROUTE_LEFT','SPEED_OUT_ROUTE_LEFT','SPEED_OUT_LEFT']
t=pd.read_csv(D+'combine_tracking.csv',usecols=['nfl_id','event_id','entity_type','time','drill_name','attempt','s','dir'])
t=t[(t.entity_type=='PLAYER')&t.drill_name.isin(DR)]; t['drill_name']=t.drill_name.replace({'SPEED_OUT_LEFT':'SPEED_OUT_ROUTE_LEFT'})
groups=[(k,d.sort_values('time')) for k,d in t.groupby(['nfl_id','event_id','attempt','drill_name'])]
P=pd.read_csv('players_master6.csv')
def run(frac):
    o=[]
    for (pid,ev,at,dr),d in groups:
        f=feats3(d.s.values,d.dir.values,frac=frac)
        if f: o.append(dict(nfl_id=pid,drill=dr,g=f['cut_force']))
    o=pd.DataFrame(o); o['res']=(o.g-o.groupby('drill').g.transform('mean'))/o.groupby('drill').g.transform('std')
    rng=np.random.default_rng(1); dr=sorted(o.drill.unique()); rs=[]
    for _ in range(200):
        h=set(rng.choice(dr,4,replace=False)); a=o[o.drill.isin(h)].groupby('nfl_id').res.mean(); b=o[~o.drill.isin(h)].groupby('nfl_id').res.mean()
        j=pd.concat([a,b],axis=1).dropna(); r=j.iloc[:,0].corr(j.iloc[:,1]); rs.append(2*r/(1+r))
    m=o.groupby('nfl_id').res.mean().rename('x'); X=P.merge(m,left_on='nfl_id',right_index=True)
    q=X.dropna(subset=['game_cf']); tr=stats.pearsonr(q.x,q.game_cf)
    q=X[X.rr>=100].dropna(subset=['tprr']); tp=stats.pearsonr(q.x,q.tprr)
    q=X.dropna(subset=['snaps_py']); sn=stats.spearmanr(q.x,q.snaps_py)
    print(f'frac={frac}: rel={np.median(rs):.2f} transfer r={tr[0]:.2f} (p={tr[1]:.3f}) TPRR r={tp[0]:.2f} (p={tp[1]:.3f}) snaps rho={sn[0]:.2f} (p={sn[1]:.3f})')
for fr in [0.5,0.6,0.7,0.8,0.9,1.0]: run(fr)
