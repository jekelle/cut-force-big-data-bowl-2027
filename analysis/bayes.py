import pandas as pd, numpy as np, pymc as pm, arviz as az
s=pd.read_csv('routes_tgt.csv',low_memory=False)
s['dn']=s.down.clip(upper=3).astype(int); s['yb']=pd.cut(s.ytg,[0,3,7,10,30],labels=False)
cells=s.groupby(['nfl_id','route_ran','slot','cov','dn']).agg(n=('tgt','size'),y=('tgt','sum')).reset_index()
pid,players=pd.factorize(cells.nfl_id); rid,routes=pd.factorize(cells.route_ran); cid,covs=pd.factorize(cells['cov'])
did,dl=pd.factorize(cells.dn); print('cells',len(cells))
PL=s.groupby('nfl_id')[['cf_z','lpick','wt_z']].first().reindex(players)
cf=PL.cf_z.values; cf=(cf-cf.mean())/cf.std(); lp=(PL.lpick-PL.lpick.mean())/PL.lpick.std(); wt=PL.wt_z.values
REL=0.563
with pm.Model() as m:
    # measurement model: observed Combine Cut Force = latent trait + drill noise (reliability 0.56)
    true_cf=pm.Normal('true_cf',0,np.sqrt(REL),shape=len(players))
    pm.Normal('cf_obs',true_cf,np.sqrt(1-REL),observed=cf)
    a=pm.Normal('a',-1.5,1); b_cf=pm.Normal('b_cf',0,0.5); b_lp=pm.Normal('b_pick',0,0.5); b_wt=pm.Normal('b_wt',0,0.5)
    sig=pm.HalfNormal('sigma_player',0.5); z=pm.Normal('z',0,1,shape=len(players))
    u=b_cf*true_cf/np.sqrt(REL)+b_lp*lp.values+b_wt*wt+sig*z   # b_cf per SD of TRUE cut force
    r=pm.ZeroSumNormal('route',1,shape=len(routes)); c=pm.ZeroSumNormal('cov',0.5,shape=len(covs))
    d=pm.ZeroSumNormal('down',0.5,shape=len(dl));
    b_sl=pm.Normal('b_slot',0,0.5)
    eta=a+u[pid]+r[rid]+c[cid]+d[did]+b_sl*cells.slot.values
    pm.Binomial('y',n=cells.n.values,p=pm.math.invlogit(eta),observed=cells.y.values)
    tr=pm.sample(1000,tune=1000,chains=4,cores=4,target_accept=0.9,random_seed=2027,progressbar=False)
print(az.summary(tr,var_names=['b_cf','b_pick','b_wt','b_slot','sigma_player'],hdi_prob=0.95).round(3))
bc=tr.posterior.b_cf.values.ravel(); print('P(b_cf>0)=',round((bc>0).mean(),3),'OR median',round(np.exp(np.median(bc)),3))
np.save('b_cf_post.npy',bc); cells.to_csv('cells.csv',index=False)
