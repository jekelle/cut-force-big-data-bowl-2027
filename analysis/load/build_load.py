import pandas as pd, numpy as np
R='/mnt/user-data/uploads/Downloads/bdb2027/reduced/'
out=[]
for y in [2023,2024,2025]:
    g=pd.read_csv(R+f'wr_all_{y}.csv.gz',usecols=['game_id','play_id','nfl_id','time','s','a','dis','event'])
    g=g.sort_values(['game_id','play_id','nfl_id','time'])
    # a in tracking is magnitude; signed accel from ds/dt at 10 Hz
    g['ds']=g.groupby(['game_id','play_id','nfl_id']).s.diff()*10
    agg=g.groupby(['game_id','play_id','nfl_id']).agg(
        frames=('s','size'), dist=('dis','sum'),
        hsr=('dis', lambda d: d[g.loc[d.index,'s']>=6.0].sum()),   # >= 6 yd/s ~ 5.5 m/s (Catapult-style HSR band)
        spr=('dis', lambda d: d[g.loc[d.index,'s']>=7.5].sum()),   # sprint band ~ 6.9 m/s
        acc=('ds', lambda v: int(((v>=3.3)&(np.r_[False,(v.to_numpy()[:-1]<3.3)])).sum())), # efforts >= ~3 m/s^2
        dec=('ds', lambda v: int(((v<=-3.3)&(np.r_[False,(v.to_numpy()[:-1]>-3.3)])).sum())),
        vmax=('s','max'))
    agg=agg.reset_index(); agg['season']=y; out.append(agg); print(y,len(agg),flush=True)
pd.concat(out).to_csv('play_load.csv',index=False)
