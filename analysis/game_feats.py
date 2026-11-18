import pandas as pd, numpy as np
from feats2 import feats2
D='/mnt/user-data/uploads/Downloads/bdb2027/'
pp=pd.read_csv(D+'nfl-big-data-bowl-2027/player_play.csv',low_memory=False)
pl=pd.read_csv(D+'nfl-big-data-bowl-2027/players.csv')
wr=set(pl.loc[pl.nfl_position=='WR','nfl_id'])
routes=['OUT','POST','CORNER','IN','CROSS','SLANT','HITCH']
keys=pp[pp.nfl_id.isin(wr)&pp.route_ran.isin(routes)][['game_id','play_id','nfl_id','route_ran']]
out=[]
for y in [2023,2024,2025]:
    gt=pd.read_csv(D+f'reduced/wr_all_{y}.csv.gz',usecols=['game_id','play_id','nfl_id','time','s','dir','event'])
    gt=gt.merge(keys,on=['game_id','play_id','nfl_id']).sort_values(['game_id','play_id','nfl_id','time'])
    for (g,p,n,r),f in gt.groupby(['game_id','play_id','nfl_id','route_ran'],sort=False):
        ev=f.event.to_numpy(); snap=np.where(ev=='ball_snap')[0]
        if len(snap)==0: continue
        st=snap[0]; pf=np.where(np.isin(ev,['pass_forward','qb_sack','qb_strip_sack']))[0]; pf=pf[pf>st]
        en=pf[0]+1 if len(pf) else st+35
        b=feats2(f.s.to_numpy()[st:en],f.dir.to_numpy()[st:en])
        if b: b.update(game_id=g,play_id=p,nfl_id=n,route=r); out.append(b)
    print(y,len(out),flush=True)
pd.DataFrame(out).to_csv('game_feats2.csv',index=False)
