import pandas as pd, numpy as np
D='/mnt/user-data/uploads/Downloads/bdb2027/'
out=[]
for y in [2023,2024,2025]:
    gt=pd.read_csv(D+f'reduced/wr_all_{y}.csv.gz',usecols=['game_id','play_id','nfl_id','y','s','event'])
    sn=gt[gt.event=='ball_snap'].drop_duplicates(['game_id','play_id','nfl_id'])
    sn=sn.assign(side_dist=np.minimum(sn.y,53.3-sn.y))
    out.append(sn[['game_id','play_id','nfl_id','side_dist']])
a=pd.concat(out); a.to_csv('align.csv',index=False)
print(a.side_dist.describe().round(2)); print(np.histogram(a.side_dist,bins=range(0,28,2)))
