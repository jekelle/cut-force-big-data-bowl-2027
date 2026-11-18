import sys, time, os, pandas as pd, numpy as np
t0 = time.time()
D = os.path.expanduser('~/mnt/Desktop/nfl-big-data-bowl-2027')
players = pd.read_csv(f'{D}/players.csv')
keep = set(players.loc[players.nfl_position.isin(['WR', 'CB', 'SS', 'FS', 'DB']), 'nfl_id'])
yr = sys.argv[1]
parts = []
for ch in pd.read_csv(f'{D}/game_tracking_{yr}.csv', usecols=['game_id', 'play_id', 'nfl_id', 'time', 'x', 'y', 's', 'dis', 'dir', 'event'], chunksize=4_000_000):
    parts.append(ch[ch.nfl_id.isin(keep)])
gt = pd.concat(parts); gt['event'] = gt.event.astype('category')
gt.to_pickle(os.path.expanduser(f'~/bdbcheck/gt_{yr}.pkl'))
print(yr, len(gt), 'rows', round(time.time() - t0), 's', round(gt.memory_usage(deep=True).sum() / 1e6), 'MB')
