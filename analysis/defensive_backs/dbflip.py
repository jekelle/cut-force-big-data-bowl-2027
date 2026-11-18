import pandas as pd, numpy as np, pickle
src=open('../nb_src.py').read(); exec(src[src.index('def smooth'):src.index('# %% [markdown]\n# ## 2.')])
G=9.80665/0.9144
ct=pickle.load(open('db_ct.pkl','rb'))
DR=['BACK_PEDAL_AND_90_DEGREE_BREAK_TO_BALL','BACK_PEDAL_AND_TRANSITION_45_DEGREE_REACTION','TERYL_AUSTIN_DRILL_1','TERYL_AUSTIN_DRILL_2','BOX_DRILL','W_DRILL']
ct=ct[ct.drill_name.isin(DR)]
def flip(s,d,deg=60):
    spd=smooth(np.asarray(s,float)); head=smooth(np.degrees(np.unwrap(np.radians(np.asarray(d,float)))))
    n=len(spd); mv=np.where(spd>2.0)[0]
    if len(mv)==0 or n<20: return None
    i0=mv[0]; dh=np.abs(np.gradient(head))
    st=[i for i in range(i0,n) if dh[i]>3]
    if not st: return None
    a=st[0]; cum=np.cumsum(dh[a:]); e=np.where(cum>=deg)[0]
    if len(e)==0: return None
    b=a+e[0]
    vin=spd[max(0,a-5):a+1].max(); vmin=spd[a:b+1].min()
    lat=spd[a:b+1]*np.radians(dh[a:b+1]*10)
    return dict(t=(b-a+1)/10, keep=vmin/vin if vin>0 else np.nan, flipg=lat.mean()/G, vin=vin)
out=[]
for (pid,ev,att,dr,yr),d in ct.groupby(['nfl_id','event_id','attempt','drill_name','draft_year']):
    d=d.sort_values('time'); f=flip(d.s.values,d.dir.values); c6=cut_force(d.s.values,d.dir.values,frac=0.6)
    if f: out.append(dict(nfl_id=pid,drill=dr,draft_year=yr,cf06=c6['cut_force']/G if c6 else np.nan,**f))
o=pd.DataFrame(out); print(o.groupby('drill')[['t','keep','flipg','cf06']].mean().round(3))
def rel(o,col,sign=1,drills=None):
    oo=o.dropna(subset=[col]).copy()
    if drills: oo=oo[oo.drill.isin(drills)]
    g=oo.groupby(['drill','draft_year'])[col]; oo['res']=sign*(oo[col]-g.transform('mean'))/g.transform('std')
    rng=np.random.default_rng(2027); dl=sorted(oo.drill.unique()); rs=[]
    for _ in range(300):
        h=set(rng.choice(dl,len(dl)//2,replace=False))
        a=oo[oo.drill.isin(h)].groupby('nfl_id').res.mean(); b=oo[~oo.drill.isin(h)].groupby('nfl_id').res.mean()
        j=pd.concat([a,b],axis=1).dropna(); r=j.iloc[:,0].corr(j.iloc[:,1]); rs.append(2*r/(1+r))
    return round(float(np.median(rs)),3)
BP=['BACK_PEDAL_AND_90_DEGREE_BREAK_TO_BALL','BACK_PEDAL_AND_TRANSITION_45_DEGREE_REACTION','TERYL_AUSTIN_DRILL_1','TERYL_AUSTIN_DRILL_2']
for col,sg in [('t',-1),('keep',1),('flipg',1),('cf06',1),('vin',1)]:
    print(col,'all6',rel(o,col,sg),'bp4',rel(o,col,sg,BP))
o.to_pickle('db_flip.pkl')
