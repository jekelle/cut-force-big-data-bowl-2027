"""Dev-only extract for the NFL route field view: breaking routes (snap to pass forward) for a handful of receivers.
The notebook rebuilds this from the competition files; this file only feeds the local layout work."""
import os, glob
import numpy as np, pandas as pd
DATA = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BREAK = ['OUT', 'POST', 'CORNER', 'IN', 'CROSS', 'SLANT', 'HITCH']
P = pd.read_csv('combine_players.csv')
games = pd.read_csv(f'{DATA}/games.csv')
pp = pd.read_csv(f'{DATA}/player_play.csv', usecols=['game_id', 'play_id', 'nfl_id', 'route_ran'], low_memory=False)
pp = pp[pp.game_id.isin(games.loc[games.season_type == 'REG', 'game_id']) & pp.nfl_id.isin(P.nfl_id) & pp.route_ran.isin(BREAK)]
cnt = pp.groupby('nfl_id').size().rename('n_brk')
Q = P.merge(cnt, left_on='nfl_id', right_index=True)
Q = Q[Q.n_brk >= 300].sort_values('cf_z', ascending=False)
pick = pd.concat([Q.head(4), Q.tail(3)])
print(pick[['display_name', 'draft_year', 'cf_z', 'n_brk']].to_string())
ids = set(pick.nfl_id)
keys = pp[pp.nfl_id.isin(ids)]
parts = []
for f in sorted(glob.glob(f'{DATA}/game_tracking_*.csv')):
    for ch in pd.read_csv(f, usecols=['game_id', 'play_id', 'nfl_id', 'time', 'x', 'y', 's', 'dir', 'event'], chunksize=3_000_000):
        parts.append(ch[ch.nfl_id.isin(ids)])
    print(os.path.basename(f), sum(len(p) for p in parts), flush=True)
gt = pd.concat(parts).merge(keys, on=['game_id', 'play_id', 'nfl_id']).sort_values(['game_id', 'play_id', 'nfl_id', 'time'])
gt.to_csv('route_frames_dev.csv', index=False)
pick.to_csv('route_receivers_dev.csv', index=False)
print('rows', len(gt), 'routes', gt.groupby(['game_id', 'play_id', 'nfl_id']).ngroups)
