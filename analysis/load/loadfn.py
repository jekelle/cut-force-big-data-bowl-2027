import numpy as np, pandas as pd
def play_load(gt):
    """Wearable-style load per player-play from 10 Hz tracking (s in yd/s, dis in yd)."""
    gt = gt.sort_values(['game_id', 'play_id', 'nfl_id', 'time']).copy()
    gt['s'] = gt.s.clip(upper=12.5)                                   # drop tracking glitches (> 25 mph)
    gt['ds'] = gt.groupby(['game_id', 'play_id', 'nfl_id']).s.diff() * 10
    up = gt.ds >= 3.3; dn = gt.ds <= -3.3                             # about 3 m/s^2 efforts
    k = ['game_id', 'play_id', 'nfl_id']
    first = gt.groupby(k).cumcount() == 0
    gt['acc'] = up & ~(up.shift(fill_value=False) & ~first)
    gt['dec'] = dn & ~(dn.shift(fill_value=False) & ~first)
    gt['hsr'] = np.where(gt.s >= 6.0, gt.dis, 0.0)                   # high speed running, about 5.5 m/s
    gt['spr'] = np.where(gt.s >= 7.5, gt.dis, 0.0)                   # sprint band, about 6.9 m/s
    return gt.groupby(k).agg(dist=('dis', 'sum'), hsr=('hsr', 'sum'), spr=('spr', 'sum'),
                             acc=('acc', 'sum'), dec=('dec', 'sum')).reset_index()
