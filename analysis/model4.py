import pandas as pd, numpy as np, statsmodels.formula.api as smf, statsmodels.api as sm
from scipy import stats
D='/mnt/user-data/uploads/Downloads/bdb2027/nfl-big-data-bowl-2027/'
pp=pd.read_csv(D+'player_play.csv',low_memory=False); pl=pd.read_csv(D+'players.csv')
al=pd.read_csv('align.csv'); P=pd.read_csv('players_master6.csv')
wr=set(pl.loc[pl.nfl_position=='WR','nfl_id'])
s=pp[pp.nfl_id.isin(wr)&pp.route_ran.notna()&(pp.play_nullified_by_penalty!='Y')].merge(al,on=['game_id','play_id','nfl_id'],how='left')
s['slot']=(s.side_dist>13).astype(float)
s['cov']=s.team_coverage_man_zone.fillna('UNK'); s['ytg']=s.yards_to_go.clip(upper=20)
s['tgt']=s.target.astype(str).str.lower().isin(['true','1','1.0']).astype(int)
s['season']=s.game_id.astype(str).str[:4].astype(int)
s=s.merge(P[['nfl_id','cf_z','lpick','combine_weight','forty']],on='nfl_id').dropna(subset=['cf_z','slot'])
s['lpick']=s.lpick.fillna(np.log(263)); s['undrafted']=P.set_index('nfl_id').pick.isna().reindex(s.nfl_id).values.astype(int)
s['wt_z']=(s.combine_weight-s.combine_weight.mean())/s.combine_weight.std()
print('routes',len(s),'players',s.nfl_id.nunique(),'target rate',round(s.tgt.mean(),3))
f='tgt ~ cf_z + C(route_ran) + slot + C(cov) + C(down) + ytg + lpick + wt_z + C(season)'
g=smf.glm(f,s,family=sm.families.Binomial()).fit(cov_type='cluster',cov_kwds={'groups':s.nfl_id})
b=g.params['cf_z']; se=g.bse['cf_z']; print(f'GLM cluster: cf_z OR={np.exp(b):.3f} [{np.exp(b-1.96*se):.3f},{np.exp(b+1.96*se):.3f}] p={g.pvalues["cf_z"]:.4f}')
# marginal effect in TPRR points
p0=g.predict(s.assign(cf_z=0)).mean(); p1=g.predict(s.assign(cf_z=1)).mean(); print('TPRR +1SD effect',round(p1-p0,4),'base',round(p0,4))
# Bayesian mixed GLM with player random intercept
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
bm=BinomialBayesMixedGLM.from_formula(f,{'player':'0+C(nfl_id)'},s).fit_vb()
i=list(bm.model.exog_names).index('cf_z'); print('BayesMixed VB cf_z',round(bm.fe_mean[i],4),'sd',round(bm.fe_sd[i],4), 'z',round(bm.fe_mean[i]/bm.fe_sd[i],2),'player sd',round(np.exp(bm.vcp_mean[0]),3))
# route-type heterogeneity: breaking vs vertical
s['brk']=s.route_ran.isin(['OUT','IN','SLANT','CORNER','POST','HITCH','CROSS']).astype(int)
g2=smf.glm(f.replace('cf_z','cf_z*brk'),s,family=sm.families.Binomial()).fit(cov_type='cluster',cov_kwds={'groups':s.nfl_id})
print(g2.params.filter(like='cf_z').round(4).to_dict(),g2.pvalues.filter(like='cf_z').round(4).to_dict())
for r in ['SLANT','OUT','IN','HITCH','CROSS','POST','CORNER','GO','FLAT','SCREEN','ANGLE','WHEEL']:
    q=s[s.route_ran==r]
    if len(q)<800: continue
    gg=smf.glm('tgt ~ cf_z + slot + C(cov) + C(down) + ytg + lpick + wt_z',q,family=sm.families.Binomial()).fit(cov_type='cluster',cov_kwds={'groups':q.nfl_id})
    print(f'{r:7s} n={len(q):5d} OR={np.exp(gg.params.cf_z):.3f} p={gg.pvalues.cf_z:.3f}')
s.to_csv('routes_tgt.csv',index=False)
