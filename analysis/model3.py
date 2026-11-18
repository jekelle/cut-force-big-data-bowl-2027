import pandas as pd, numpy as np, statsmodels.formula.api as smf
from scipy import stats
D='/mnt/user-data/uploads/Downloads/bdb2027/nfl-big-data-bowl-2027/'
pp=pd.read_csv(D+'player_play.csv',low_memory=False); pl=pd.read_csv(D+'players.csv')
al=pd.read_csv('align.csv'); P=pd.read_csv('players_master2.csv',index_col=0)
wr=set(pl.loc[pl.nfl_position=='WR','nfl_id'])
s=pp[pp.nfl_id.isin(wr)&pp.route_ran.notna()].merge(al,on=['game_id','play_id','nfl_id'],how='left')
s['slot']=(s.side_dist>13).astype(float); s.loc[s.side_dist.isna(),'slot']=np.nan
s['cov']=s.team_coverage_man_zone.fillna('UNK'); s['cush']=s.cushion
s=s.dropna(subset=['separation_at_pass_forward','slot','cush'])
s['ytg']=s.yards_to_go.clip(upper=20)
m=smf.ols('separation_at_pass_forward ~ C(route_ran)*C(cov) + C(route_ran)*slot + cush + C(down) + ytg',s).fit()
print('play model R2',round(m.rsquared,3),'n',len(s))
s['sres']=m.resid
def eb(df,col):
    g=df.groupby('nfl_id')[col].agg(['mean','count','var']); wv=np.nanmean(g['var'])
    t2=max(1e-9,g['mean'].var()-wv/g['count'].mean()); w=t2/(t2+wv/g['count']); return w*g['mean'],g['count'],t2,wv
se,sn,t2,wv=eb(s,'sres'); print('sep_oe tau',round(np.sqrt(t2),3))
P['sep_oe2']=se; P['routes2']=sn; P['slot_share']=s.groupby('nfl_id').slot.mean()
X=P.dropna(subset=['combine_cf','sep_oe2'])
for v in ['combine_cf','game_cf','combine_weight','forty','ten_yd_split','slot_share','ngs_athleticism_score']:
    q=X.dropna(subset=[v]); r,p=stats.pearsonr(q[v],q.sep_oe2); print(f'{v:22s} r={r:+.3f} p={p:.3f} n={len(q)}')
q=X.dropna(subset=['forty','combine_weight'])
mm=smf.ols('sep_oe2 ~ combine_cf + combine_weight + forty',q).fit(); print(mm.summary().tables[1])
# game cut force -> separation, player level, controlling weight
mm2=smf.ols('sep_oe2 ~ game_cf + combine_weight',X).fit(); print(mm2.summary().tables[1])
P.to_csv('players_master3.csv'); s[['game_id','play_id','nfl_id','route_ran','slot','sres','separation_at_pass_forward','cov','cush','target','expected_points_added','rec_yards']].to_csv('routes_sep.csv',index=False)
