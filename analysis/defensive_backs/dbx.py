import sys, os, numpy as np, pandas as pd
Y=int(sys.argv[1]); D=os.path.expanduser('~/mnt/nfl-big-data-bowl-2027/'); OUT=D+'analysis/'
def smooth(x,k=3): return pd.Series(x).rolling(k,center=True,min_periods=1).mean().to_numpy()
def cut_force(s,d,hz=10,min_speed=3.0):
    s=np.asarray(s,float); n=len(s)
    if n<15: return None
    head=smooth(np.degrees(np.unwrap(np.radians(np.asarray(d,float))))); spd=smooth(s)
    lat=spd*np.radians(np.abs(np.gradient(head)*hz)); ok=(spd>min_speed)&(np.arange(n)>8)
    if ok.sum()<4: return None
    L=np.where(ok,lat,0.0); k=int(np.argmax(L)); win=lat[max(0,k-3):k+4]
    return float(np.mean(np.sort(win)[-3:])), float(spd[max(0,k-8):k+1].max())
pl=pd.read_csv(D+'players.csv'); g=pd.read_csv(D+'games.csv')
REG=set(g.loc[g.season_type=='REG','game_id'])
DB=set(pl.loc[pl.nfl_position.isin(['CB','SS','FS','DB']),'nfl_id']); WR=set(pl.loc[pl.nfl_position=='WR','nfl_id'])
pp=pd.read_csv(D+'player_play.csv',usecols=['game_id','play_id','nfl_id','coverage_assignment','route_ran','target','team_abbr'])
pp=pp[pp.game_id.isin(REG)]
cov=pp[pp.nfl_id.isin(DB)&pp.coverage_assignment.notna()][['game_id','play_id','nfl_id','coverage_assignment','team_abbr']]
wrr=pp[pp.nfl_id.isin(WR)&pp.route_ran.notna()][['game_id','play_id','nfl_id','route_ran','target']]
keys=set(map(tuple,cov[['game_id','play_id']].drop_duplicates().to_numpy()))
parts=[]
for ch in pd.read_csv(D+f'game_tracking_{Y}.csv',usecols=['game_id','play_id','nfl_id','time','x','y','s','dir','event'],chunksize=3_000_000):
    ch=ch[ch.nfl_id.isin(DB|WR)&ch.game_id.isin(REG)]
    parts.append(ch)
gt=pd.concat(parts).sort_values(['game_id','play_id','nfl_id','time'])
gt=gt.merge(cov[['game_id','play_id']].drop_duplicates(),on=['game_id','play_id']).sort_values(['game_id','play_id','nfl_id','time'])
print('frames',len(gt),flush=True)
covk=cov.set_index(['game_id','play_id','nfl_id']).coverage_assignment.to_dict()
wrk=wrr.set_index(['game_id','play_id','nfl_id'])[['route_ran','target']].to_dict('index')
F=[]; M=[]
for (gm,pl_),play in gt.groupby(['game_id','play_id'],sort=False):
    ev=play.event.to_numpy()
    trk={n:d for n,d in play.groupby('nfl_id',sort=False)}
    wrs={n:d for n,d in trk.items() if (gm,pl_,n) in wrk}
    for n,d in trk.items():
        ca=covk.get((gm,pl_,n))
        if ca is None: continue
        e=d.event.to_numpy(); sn=np.where(e=='ball_snap')[0]
        if len(sn)==0: continue
        st=sn[0]; pf=np.where(np.isin(e,['pass_forward','qb_sack','qb_strip_sack']))[0]; pf=pf[pf>st]
        en=pf[0]+1 if len(pf) else st+35
        r=cut_force(d.s.to_numpy()[st:en],d.dir.to_numpy()[st:en])
        rec=dict(game_id=gm,play_id=pl_,nfl_id=n,cov=ca,cf=r[0] if r else np.nan,entry=r[1] if r else np.nan,has_pf=int(len(pf)>0))
        F.append(rec)
        if ca=='MAN' and wrs:
            xs,ys=d.x.to_numpy()[st],d.y.to_numpy()[st]; best=None
            for w,wd in wrs.items():
                we=wd.event.to_numpy(); ws=np.where(we=='ball_snap')[0]
                if len(ws)==0: continue
                dd=np.hypot(wd.x.to_numpy()[ws[0]]-xs, wd.y.to_numpy()[ws[0]]-ys)
                if best is None or dd<best[1]: best=(w,dd,wd)
            if best and best[1]<=12:
                w,dsn,wd=best; we=wd.event.to_numpy(); wpf=np.where(np.isin(we,['pass_forward']))[0]
                sep=np.nan
                if len(wpf) and len(pf):
                    i=min(pf[0],len(d)-1); j=min(wpf[0],len(wd)-1)
                    sep=float(np.hypot(wd.x.to_numpy()[j]-d.x.to_numpy()[i], wd.y.to_numpy()[j]-d.y.to_numpy()[i]))
                M.append(dict(game_id=gm,play_id=pl_,db=n,wr=w,snap_dist=dsn,sep_pf=sep,route=wrk[(gm,pl_,w)]['route_ran'],target=wrk[(gm,pl_,w)]['target']))
pd.DataFrame(F).to_csv(OUT+f'db_feats_{Y}.csv',index=False); pd.DataFrame(M).to_csv(OUT+f'db_man_{Y}.csv',index=False)
print('done',Y,len(F),len(M),flush=True)
