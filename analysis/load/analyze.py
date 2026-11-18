import pickle, pandas as pd, numpy as np, statsmodels.formula.api as smf
S=pickle.load(open('../state.pkl','rb')); GF=S['GF'].copy(); P=S['P']; pp=S['pp']
L=pd.read_csv('play_load.csv')
# all regular-season WR routes in order, with load per route
wr=pp[pp.nfl_id.isin(P.nfl_id)&pp.route_ran.notna()][['game_id','play_id','nfl_id','possession_team','quarter','game_clock','target']]
R=wr.merge(L,on=['game_id','play_id','nfl_id'],how='left').sort_values(['game_id','nfl_id','play_id'])
print('routes',len(R),'with load',R.dist.notna().mean())
for c in ['dist','hsr','spr','acc','dec']: R[c]=R[c].fillna(R[c].median())
R['eff']=R.acc+R.dec
grp=R.groupby(['game_id','nfl_id'])
R['k']=grp.cumcount()                                 # routes already run this game
R['cum_hsr']=grp.hsr.cumsum()-R.hsr                   # high-speed yards before this route
R['cum_eff']=grp.eff.cumsum()-R.eff
R['cum_dist']=grp.dist.cumsum()-R.dist
# short-term load: consecutive team dropbacks with this WR running a route
team=pp[pp.team_abbr==pp.possession_team][['game_id','play_id','possession_team']].drop_duplicates().sort_values(['game_id','play_id'])
team['tix']=team.groupby(['game_id','possession_team']).cumcount()
R=R.merge(team,on=['game_id','play_id','possession_team'],how='left')
R=R.sort_values(['game_id','nfl_id','tix'])
R['gap']=R.groupby(['game_id','nfl_id']).tix.diff().ne(1)
R['streak']=R.groupby(['game_id','nfl_id',R.gap.cumsum()]).cumcount()   # prior back-to-back routes
R['hsr3']=R.groupby(['game_id','nfl_id']).hsr.transform(lambda s:s.shift(1).rolling(3,min_periods=1).sum()).fillna(0)
R.to_pickle('routes_load.pkl')
# merge breaking-route Cut Force
X=GF.merge(R,on=['game_id','play_id','nfl_id']).merge(P[['nfl_id','cf_z']],on='nfl_id')
for c in ['cum_hsr','cum_eff','k','hsr3','streak']:
    X[c+'_z']=(X[c]-X[c].mean())/X[c].std()
X['late']=(X.quarter>=4).astype(int)
print('breaking routes with load',len(X), 'players',X.nfl_id.nunique())
def fit(f,lab):
    m=smf.ols(f,X).fit(cov_type='cluster',cov_kwds={'groups':X.nfl_id})
    print(lab); print(m.params.filter(regex='_z|late|cf_z').round(4).to_string()); print(m.pvalues.filter(regex='_z|late|cf_z').round(3).to_string()); return m
# res is already route- and entry-speed adjusted; player fixed effects -> within-player change
m1=fit('res ~ cum_hsr_z + C(nfl_id)','cumulative HSR')
m2=fit('res ~ k_z + C(nfl_id)','route count')
m3=fit('res ~ hsr3_z + streak_z + C(nfl_id)','short-term load')
m4=fit('res ~ late + C(nfl_id)','4th quarter')
m5=fit('res ~ cum_hsr_z*cf_z + C(nfl_id)','interaction')
m6=fit('res ~ hsr3_z*cf_z + streak_z + C(nfl_id)','short interaction')
sd=X.groupby('nfl_id').res.mean().std(); print('SD of player mean res',round(sd,4),'route SD',round(X.res.std(),4))
X.to_pickle('X.pkl')
