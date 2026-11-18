import sys, os, numpy as np, pandas as pd
Y=int(sys.argv[1]); D=os.path.expanduser('~/mnt/nfl-big-data-bowl-2027/'); OUT=D+'analysis/'
def smooth(x,k=3): return pd.Series(x).rolling(k,center=True,min_periods=1).mean().to_numpy()
def lat(s,d):
    head=smooth(np.degrees(np.unwrap(np.radians(np.asarray(d,float))))); spd=smooth(np.asarray(s,float))
    return spd*np.radians(np.abs(np.gradient(head))*10), spd
M=pd.read_csv(OUT+f'db_man_{Y}.csv')
need=set(M.db)|set(M.wr); keys=M[['game_id','play_id']].drop_duplicates()
parts=[]
for ch in pd.read_csv(D+f'game_tracking_{Y}.csv',usecols=['game_id','play_id','nfl_id','time','x','y','s','dir','event'],chunksize=3_000_000):
    parts.append(ch[ch.nfl_id.isin(need)].merge(keys,on=['game_id','play_id']))
gt=pd.concat(parts).sort_values(['game_id','play_id','nfl_id','time'])
T={k:d for k,d in gt.groupby(['game_id','play_id','nfl_id'],sort=False)}
out=[]
for r in M.itertuples():
    a=T.get((r.game_id,r.play_id,r.db)); b=T.get((r.game_id,r.play_id,r.wr))
    if a is None or b is None: continue
    ea=a.event.to_numpy(); eb=b.event.to_numpy()
    sa=np.where(ea=='ball_snap')[0]; sb=np.where(eb=='ball_snap')[0]
    if not len(sa) or not len(sb): continue
    pf=np.where(np.isin(eb,['pass_forward','qb_sack','qb_strip_sack']))[0]; pf=pf[pf>sb[0]]
    n=min(len(a)-sa[0], len(b)-sb[0], (pf[0]-sb[0]+1) if len(pf) else 35)
    if n<15: continue
    A=a.iloc[sa[0]:sa[0]+n]; B=b.iloc[sb[0]:sb[0]+n]
    la,va=lat(A.s,A.dir); lb,vb=lat(B.s,B.dir)
    ok=(vb>3)&(np.arange(n)>8)
    if ok.sum()<4: continue
    kb=int(np.argmax(np.where(ok,lb,0)))          # WR break frame
    w=la[kb:min(n,kb+16)]                          # DB response within 1.5 s
    if len(w)<3: continue
    ka=int(np.argmax(w)); lag=ka/10
    # cross-correlation lag of turn-load series, 0 to 1.0 s
    best=(np.nan,-9)
    for L in range(0,11):
        x=lb[:n-L]; y=la[L:n]
        if len(x)>8 and x.std()>0 and y.std()>0:
            c=np.corrcoef(x,y)[0,1]
            if c>best[1]: best=(L/10,c)
    d_at=lambda i: float(np.hypot(B.x.to_numpy()[i]-A.x.to_numpy()[i], B.y.to_numpy()[i]-A.y.to_numpy()[i]))
    j=min(n-1,kb+5)
    out.append(dict(game_id=r.game_id,play_id=r.play_id,db=r.db,wr=r.wr,wr_break_g=lb[kb]/10.725,lag=lag,xlag=best[0],xcorr=best[1],
                    sep_break=d_at(kb),sep_after=d_at(j),sep_end=d_at(n-1),db_resp_g=w.max()/10.725))
pd.DataFrame(out).to_csv(OUT+f'db_mirror_{Y}.csv',index=False); print('done',Y,len(out),flush=True)
