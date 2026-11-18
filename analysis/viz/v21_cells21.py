"""New and changed cells for notebook v21. Imported by build21.py and test21.py."""

SEC16_MD = """## 16. Interactive figures (Plotly)

Every figure in the writeup has an interactive version in this notebook. Hover for the receiver or the exact number, drag to zoom, and double-click to reset.

| Writeup | Interactive version |
|---|---|
| Figure 1, the break replay | section 17 (two reps, animated) and section 20 (every receiver's highest Cut Force rep) |
| Figure 2, Combine to NFL transfer | below |
| Figure 3, the break-phase scorecard | below |
| Figure 4, targets per route | below (player-level view) |
| Figure 5, the Cut Force card | section 20, for all 107 receivers |
| Figure 6, Cut Force under load | below |
| Figure 7, the historical Combine | below (needs the notebook's internet setting on, because it reads the public nflverse file) |
| Tables H1 and H2 | below |

The section 3 stopwatch check is here too. The static images above are the versions in the writeup."""

# Exact-match replacements inside the section 16 code cell: labels that tie each chart to the writeup.
SEC16_REPL = [
    ("def show(fig):\n    display(HTML(fig.to_html(include_plotlyjs=False, full_html=False, auto_play=False, config={'displaylogo': False, 'responsive': True})))\n",
     "def show(fig):\n    display(HTML(fig.to_html(include_plotlyjs=False, full_html=False, auto_play=False, config={'displaylogo': False, 'responsive': True})))\n"
     "def label(txt):\n    display(HTML(f'<p style=\"margin:22px 0 0;font:600 15px Helvetica,Arial,sans-serif;color:#13294B\">{txt}</p>'))\n"),
    ("# Figure 2: Combine to game transfer, hover shows the receiver\n",
     "# Writeup Figure 2: Combine to game transfer, hover shows the receiver\nlabel('Writeup Figure 2. Combine Cut Force against NFL game Cut Force')\n"),
    ("# Figure 3: independence from the stopwatch\n",
     "# Section 3 check (not a writeup figure): independence from the stopwatch\nlabel('Section 3 check. Cut Force against every stopwatch measure')\n"),
    ("# Figure 4: targets per route at the player level\n",
     "# Writeup Figure 4, player-level view: targets per route\nlabel('Writeup Figure 4, player-level view. Targets per route against Combine Cut Force')\n"),
    ("# Figure 6: ten break definitions on the same checks\n",
     "# Appendix H, Table H1: ten break definitions on the same checks\nlabel('Appendix H, Table H1. Ten break definitions on the same checks')\n"),
    ("# Figure 7: held-out draft class\n",
     "# Appendix H, Table H2: a held-out draft class\nlabel('Appendix H, Table H2. A held-out draft class')\n"),
]

SEC16_ADD = r'''

# Writeup Figure 3: the break-phase scorecard (same numbers and shading as the static figure in section 14)
label('Writeup Figure 3. Each break phase scored on the same checks')
try:
    tdb_ = T10.dropna(subset=['db_cf_z'])
    mdb_ = smf.ols('sep ~ db_cf_z + C(route) + snap_dist', tdb_).fit(cov_type='cluster', cov_kwds={'groups': tdb_.db})
    rows3 = list(PHASES.phase) + ['Defensive back Cut Force']
    V3 = [[r.combine_rel, r.game_rel, r.transfer_r, 1 - r.stopwatch_max_abs_r] for r in PHASES.itertuples()] + [[REL_DB, REL_DBG, r_db, None]]
    T3 = [[f'{r.combine_rel:.2f}', f'{r.game_rel:.2f}', f'{r.transfer_r:+.2f}', f'{r.stopwatch_max_abs_r:.2f}', f'{r.sep_b:+.3f} (p = {r.sep_p:.2f})'] for r in PHASES.itertuples()]
    T3 += [[f'{REL_DB:.2f}', f'{REL_DBG:.2f}', f'{r_db:+.2f}', 'not tested', f'{mdb_.params.db_cf_z:+.2f} (p = {mdb_.pvalues.db_cf_z:.2f})']]
    SCL3 = [(0, 0.7), (0, 0.8), (-0.1, 0.35), (0.4, 1.0)]
    Z3 = [[None if v is None else min(1, max(0, (v - SCL3[j][0]) / (SCL3[j][1] - SCL3[j][0]))) for j, v in enumerate(row)] + [None] for row in V3]
    H3 = ['Combine<br>reliability', 'NFL game<br>reliability', 'Combine to<br>NFL r', 'Overlap with<br>stopwatch, max |r|<br>(lower = newer)', 'Separation at<br>throw, yd per SD']
    WHY3 = ['How well one set of Combine drills agrees with another (Spearman-Brown, 1 = perfect)',
            'How well one set of NFL routes agrees with another',
            'Correlation between the Combine score and the same score in NFL routes',
            'Largest correlation with the 40, 10-yard split, 3-cone or shuttle. Lower means newer information',
            'Change in separation at the throw per SD, with weight and slot share controlled. Not shaded']
    CD3 = [[WHY3[j] for j in range(5)] for _ in rows3]
    fig = go.Figure(go.Heatmap(z=Z3, x=H3, y=rows3, text=T3, texttemplate='%{text}', textfont=dict(size=15), customdata=CD3,
                               colorscale=[[0, '#F3F4F6'], [0.5, '#C9D3E3'], [1, NV]], zmin=0, zmax=1, showscale=False, xgap=4, ygap=4, hoverongaps=False,
                               hovertemplate='<b>%{y}</b><br>%{x}: <b>%{text}</b><br>%{customdata}<extra></extra>'))
    fig.add_shape(type='rect', xref='paper', yref='y', x0=-0.355, x1=1.0, y0=0.5, y1=1.5, line=dict(color=GD, width=3))
    fig.update_layout(title='Only the cut itself is a Combine trait that carries to NFL routes', yaxis=dict(autorange='reversed', automargin=True),
                      xaxis=dict(side='top'), height=470, **{**LAY, 'margin': dict(l=230, r=20, t=110, b=30)})
    show(fig)
except Exception as e:
    print('Figure 3 interactive skipped:', repr(e))

# Writeup Figure 6: Cut Force under load (Appendix D)
label('Writeup Figure 6. Cut Force under game load')
try:
    fig = make_subplots(rows=1, cols=2, column_widths=[0.56, 0.44], horizontal_spacing=0.12,
                        subplot_titles=('A. Cut Force holds as game load builds', 'B. Workload numbers track speed, not cuts'))
    y6 = (QL.d / bsd * 100).to_numpy(); e6 = (1.96 * QL.se / bsd * 100).to_numpy()
    fig.add_shape(type='rect', xref='x domain', yref='y', x0=0, x1=1, y0=-10, y1=10, fillcolor='#E3E7EE', opacity=1, line_width=0, layer='below')
    fig.add_trace(go.Scatter(x=QL.cum, y=y6, mode='lines+markers', name='Cut Force vs his own average', line=dict(color=NV, width=2.6), marker=dict(size=10, color=NV),
                             error_y=dict(type='data', array=e6, color=NV, thickness=1.6, width=5), customdata=np.c_[y6 - e6, y6 + e6],
                             hovertemplate='About %{x:.0f} high speed yards already run<br>Cut Force %{y:+.1f}% of a player SD<br>95% interval %{customdata[0]:+.1f} to %{customdata[1]:+.1f}<extra></extra>'), 1, 1)
    L6 = ['High speed yd<br>per route', 'Sprint yd<br>per route', 'Accel + decel<br>efforts per route']
    fig.add_trace(go.Bar(x=L6, y=[abs(WCOR[c][1]) for c in WCOR], name='40 time', marker_color=GD,
                         hovertemplate='%{x}<br>|r| with the 40: %{y:.2f}<extra></extra>'), 1, 2)
    fig.add_trace(go.Bar(x=L6, y=[abs(WCOR[c][0]) for c in WCOR], name='Combine Cut Force', marker_color=NV,
                         hovertemplate='%{x}<br>|r| with Combine Cut Force: %{y:.2f}<extra></extra>'), 1, 2)
    fig.update_xaxes(title_text='High speed yards already run in the game', row=1, col=1)
    fig.update_yaxes(title_text='Cut Force vs own average (% of a player SD)', range=[-40, 40], zeroline=True, row=1, col=1)
    fig.update_yaxes(title_text='|r| with workload metric', range=[0, 0.6], row=1, col=2)
    fig.update_layout(barmode='group', height=470, legend=dict(orientation='h', y=-0.22), **LAY)
    fig.add_annotation(text='shaded band = within 10% of a player SD', xref='x domain', yref='y domain', x=0.98, y=0.04, showarrow=False, font=dict(color='#6B7280', size=12), row=1, col=1)
    show(fig)
except Exception as e:
    print('Figure 6 interactive skipped:', repr(e))

# Writeup Figure 7: the historical Combine (Appendix G). Public nflverse data, so this one needs the internet.
label('Writeup Figure 7. The 2000 to 2026 Combine in the 40 and vertical jump')
NV_URL = 'https://github.com/nflverse/nflverse-data/releases/download/combine/combine.csv'
PG7 = {'QB': 'QB', 'RB': 'RB', 'FB': 'RB', 'WR': 'WR', 'TE': 'TE', 'OT': 'OL', 'OG': 'OL', 'C': 'OL', 'G': 'OL', 'OL': 'OL',
       'DT': 'DL', 'DL': 'DL', 'NT': 'DL', 'DE': 'EDGE', 'EDGE': 'EDGE', 'OLB': 'LB', 'ILB': 'LB', 'LB': 'LB',
       'CB': 'DB', 'S': 'DB', 'SAF': 'DB', 'DB': 'DB', 'CB/WR': 'DB'}
def fig7_frames(nv, cr):
    nv = nv[nv.season != 2021].copy(); nv['grp'] = nv.pos.map(PG7); nv = nv[nv.grp.notna()]
    hist_all = nv[(nv.pos == 'WR') & (nv.season < 2023)]                     # means use every receiver with that measure
    kag_all = cr[cr.combine_position == 'WR'].merge(players[['nfl_id', 'display_name']], on='nfl_id', how='left')
    both = lambda d: d.dropna(subset=['forty', 'vertical'])                     # points need both measures
    nvb = both(nv)
    med = nvb.groupby('grp').agg(forty=('forty', 'median'), vertical=('vertical', 'median'), wt=('wt', 'median'), n=('forty', 'size')).reset_index()
    return nvb, med, both(hist_all), both(kag_all), hist_all, kag_all
try:
    nv7, med7, hist7, kag7, hist7a, kag7a = fig7_frames(pd.read_csv(NV_URL), cr)
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.09,
                        subplot_titles=('A. Participants with a 40 and a vertical, by position', 'B. Receivers: this study against 2000 to 2022'))
    fig.add_trace(go.Scattergl(x=nv7.forty, y=nv7.vertical, mode='markers', name=f'Participants with both measures (n = {len(nv7):,})', marker=dict(size=5, color='#C4CAD3', opacity=0.3),
                               text=[f'{n} ({p}, {s})' for n, p, s in zip(nv7.player_name, nv7.pos, nv7.season)], hovertemplate='%{text}<br>40: %{x:.2f} s<br>Vertical: %{y:.1f} in<extra></extra>'), 1, 1)
    fig.add_trace(go.Scatter(x=med7.forty, y=med7.vertical, mode='markers', name='Position median (size = median weight, lb)', text=med7.grp,
                             marker=dict(size=8 + (med7.wt - med7.wt.min()) / (med7.wt.max() - med7.wt.min()) * 22, color=[GD if g == 'WR' else NV for g in med7.grp], line=dict(color='white', width=1.5)),
                             customdata=np.c_[med7.wt, med7.n], hovertemplate='<b>%{text}</b> median<br>40: %{x:.2f} s<br>Vertical: %{y:.1f} in<br>Weight: %{customdata[0]:.0f} lb (n = %{customdata[1]})<extra></extra>'), 1, 1)
    fig.add_trace(go.Scattergl(x=hist7.forty, y=hist7.vertical, mode='markers', name=f'Combine receivers, 2000 to 2022 (n = {len(hist7)})', marker=dict(size=6, color='#B8BEC8', opacity=0.6),
                               text=[f'{n} ({s})' for n, s in zip(hist7.player_name, hist7.season)], hovertemplate='%{text}<br>40: %{x:.2f} s<br>Vertical: %{y:.1f} in<extra></extra>'), 1, 2)
    fig.add_trace(go.Scatter(x=kag7.forty, y=kag7.vertical, mode='markers', name=f'The competition\'s 2023 to 2025 receivers (n = {len(kag7)})', marker=dict(size=8, color=NV, opacity=0.85, line=dict(color='white', width=0.8)),
                             text=[f'{n} ({y})' for n, y in zip(kag7.display_name.fillna('Receiver'), kag7.draft_year)], hovertemplate='%{text}<br>40: %{x:.2f} s<br>Vertical: %{y:.1f} in<extra></extra>'), 1, 2)
    for d7, col, nm in [(hist7a, '#6B7280', '2000 to 2022 mean'), (kag7a, GD, '2023 to 2025 mean')]:
        mx, my = d7.forty.mean(), d7.vertical.mean()
        fig.add_trace(go.Scatter(x=[mx], y=[my], mode='markers', name=nm, marker=dict(symbol='x-thin', size=22, line=dict(color=col, width=4)),
                                 hovertemplate=f'{nm}<br>40: {mx:.2f} s<br>Vertical: {my:.1f} in<extra></extra>'), 1, 2)
    OFF7 = {'WR': (-46, 30), 'DB': (-50, -26), 'RB': (6, -44), 'LB': (34, -34), 'TE': (40, 26), 'QB': (46, 8), 'EDGE': (-6, 40), 'DL': (30, 34), 'OL': (34, 30)}
    for r7 in med7.itertuples():
        ax7, ay7 = OFF7.get(r7.grp, (30, -30))
        fig.add_annotation(x=r7.forty, y=r7.vertical, text=f'<b>{r7.grp}</b>', ax=ax7, ay=ay7, arrowcolor='#9CA3AF', arrowwidth=1, font=dict(size=13, color=GD if r7.grp == 'WR' else NV),
                           bgcolor='rgba(255,255,255,0.85)', row=1, col=1)
    for c in (1, 2):
        fig.update_xaxes(title_text='40-yard dash (s), faster to the left', row=1, col=c)
        fig.update_yaxes(title_text='Vertical jump (in)', row=1, col=c)
    fig.update_xaxes(range=[4.2, 5.6], row=1, col=1); fig.update_xaxes(range=[4.2, 4.85], row=1, col=2)
    fig.update_layout(height=520, legend=dict(orientation='h', y=-0.2), **LAY)
    show(fig)
    print(f'Means over every receiver with that measure. 2000 to 2022: 40 = {hist7a.forty.mean():.2f} s (n = {hist7a.forty.notna().sum()}), vertical = {hist7a.vertical.mean():.1f} in (n = {hist7a.vertical.notna().sum()}) | '
          f'this study: 40 = {kag7a.forty.mean():.2f} s (n = {kag7a.forty.notna().sum()}), vertical = {kag7a.vertical.mean():.1f} in (n = {kag7a.vertical.notna().sum()}). Plotted with both: {len(hist7)} and {len(kag7)}.')
except Exception as e:
    print('Figure 7 interactive skipped (it reads the public nflverse file, so the notebook needs internet on):', repr(e))
'''

SEC20_MD = """## 20. Every receiver: his card and his highest Cut Force rep

The writeup shows one Cut Force card (Figure 5, Puka Nacua) and two reps (Figure 1). Here all 107 receivers get both. Pick a name from the menu above each chart.

The card has the same three panels as Figure 5: his percentiles against the class, every Combine route drill against the middle 80% of the class, and what happened in the NFL. The replay shows the one Combine rep with his highest Cut Force, turned the same way as Figure 1, with the sideways (centripetal) acceleration across the rep. The dot marks the peak frame. A rep's Cut Force averages the top three frames around that peak, so it can sit just under the dot."""

SEC20_CARD = r'''# Writeup Figure 5 for every receiver: the Cut Force card, chosen from a menu
NAMES20 = P.sort_values('cf_z', ascending=False).display_name.tolist()     # menu order: highest Cut Force first
DR20 = sorted(reps.drill.unique()); NICE20 = [d.replace('_ROUTE', '').replace('_', ' ').title() for d in DR20]
CLS20 = {d: reps[reps.drill == d].res for d in DR20}
q100 = P[P.rr >= 100]
def pct20(col, v, low_good=False):
    s = P[col].dropna()
    return None if pd.isna(v) else float(((s > v) if low_good else (s < v)).mean() * 100)
ITEMS20 = ['Cut Force', 'NGS athleticism', '40-yard dash', '3-cone', 'Draft slot (earlier = higher)']
fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.2,
                    subplot_titles=('What the stopwatch saw vs the break (percentile)', 'Every Combine route drill (z vs class)'))
fig.add_trace(go.Bar(y=ITEMS20[::-1], x=[100] * 5, orientation='h', marker_color='#E9ECF1', hoverinfo='skip', showlegend=False, width=0.6), 1, 1)
fig.update_layout(barmode='overlay')
for i, d in enumerate(DR20):
    lo_, hi_, md_ = CLS20[d].quantile(.1), CLS20[d].quantile(.9), CLS20[d].median()
    fig.add_trace(go.Scatter(x=[lo_, hi_], y=[NICE20[i]] * 2, mode='lines', line=dict(color='#D9DEE7', width=12), hoverinfo='skip', showlegend=False), 1, 2)
    fig.add_trace(go.Scatter(x=[md_], y=[NICE20[i]], mode='markers', marker=dict(symbol='line-ns-open', size=16, color='#6B7280', line=dict(width=2)),
                             hovertemplate=f'{NICE20[i]}<br>class median {md_:+.2f}, middle 80% {lo_:+.2f} to {hi_:+.2f}<extra></extra>', showlegend=False), 1, 2)
NBASE20 = len(fig.data); ann20 = {}
for k, nm in enumerate(NAMES20):
    p = P.set_index('display_name').loc[nm]
    v = [pct20('cf_z', p.cf_z), pct20('ngs_athleticism_score', p.ngs_athleticism_score), pct20('forty', p.forty, True), pct20('three_cone', p.three_cone, True), pct20('lpick', p.lpick, True)]
    xs = [0 if a is None else a for a in v][::-1]
    tx = ['did not run' if a is None else f'{a:.0f}' for a in v][::-1]
    fig.add_trace(go.Bar(y=ITEMS20[::-1], x=xs, orientation='h', width=0.6, marker_color=[NV, NV, NV, NV, GD], text=tx, textposition='outside', cliponaxis=False,
                         hovertemplate='%{y}: %{text}<extra></extra>', visible=(k == 0), showlegend=False), 1, 1)
    mine = reps[reps.nfl_id == p.nfl_id].groupby('drill').res.max().reindex(DR20)
    fig.add_trace(go.Scatter(x=mine.values, y=NICE20, mode='markers', marker=dict(size=12, color=GD, line=dict(color=NV, width=1)),
                             hovertemplate='%{y}<br>his best rep: %{x:+.2f}<extra></extra>', visible=(k == 0), showlegend=False), 1, 2)
    g_pct = f'{(P.game_cf.dropna() <= p.game_cf).mean() * 100:.0f}th pct' if pd.notna(p.game_cf) else 'n/a'
    tp = f'{p.tprr * 100:.1f}%' if pd.notna(p.tprr) else 'n/a'
    rr = f'{int(p.rr):,}' if pd.notna(p.rr) else '0'
    ann20[nm] = [dict(text=f'<b>{nm}</b>   WR   {int(p.draft_year)} draft, pick {int(p.pick)}<br><span style="font-size:12px;color:#6B7280">Percentiles among the {len(P)} receivers with Combine route-drill tracking (2023 to 2025 classes)</span>',
                      x=0, y=1.27, xref='paper', yref='paper', showarrow=False, xanchor='left', align='left', font=dict(size=19, color=NV)),
                 dict(text=f'<b>What happened in the NFL</b><br>Targets per route: <b>{tp}</b> (median of receivers with 100+ routes {q100.tprr.median() * 100:.1f}%)'
                           f'<br>NFL game Cut Force: <b>{g_pct}</b> (route and speed adjusted)<br>Regular-season routes run: <b>{rr}</b> (2023 to 2025)',
                      x=0, y=-0.3, xref='paper', yref='paper', showarrow=False, xanchor='left', align='left', font=dict(size=13, color='#1A1A1A'),
                      bgcolor='#F3F4F6', borderpad=8)]
fig.add_annotation(text='gold = his best rep, bar = middle 80%, tick = median', xref='x2 domain', yref='y2 domain', x=1.0, y=-0.12,
                   showarrow=False, xanchor='right', font=dict(size=11, color='#6B7280'))
STATIC20 = list(fig.layout.annotations)          # the two panel titles and the key stay on every receiver
btn20 = []
for k, nm in enumerate(NAMES20):
    vis = [True] * NBASE20 + [False] * (2 * len(NAMES20)); vis[NBASE20 + 2 * k] = vis[NBASE20 + 2 * k + 1] = True
    btn20.append(dict(label=nm, method='update', args=[{'visible': vis}, {'annotations': STATIC20 + ann20[nm]}]))
start = NAMES20.index('Puka Nacua') if 'Puka Nacua' in NAMES20 else 0
for j, t in enumerate(fig.data[NBASE20:]):
    t.visible = (j // 2 == start)
fig.update_layout(updatemenus=[dict(buttons=btn20, active=start, x=1.0, xanchor='right', y=1.32, yanchor='top', direction='down', bgcolor='white', font=dict(size=13))],
                  annotations=STATIC20 + ann20[NAMES20[start]], height=640, **{**LAY, 'margin': dict(l=200, r=30, t=150, b=170)})
fig.update_xaxes(range=[0, 118], tickvals=[0, 50, 100], row=1, col=1)
fig.update_xaxes(zeroline=True, zerolinecolor='#9CA3AF', row=1, col=2)
fig.update_yaxes(autorange='reversed', row=1, col=2)
show(fig)
'''

SEC20_REPLAY = r'''# Writeup Figure 1 for every receiver: his highest Cut Force rep, chosen from a menu
best20 = reps.loc[reps.groupby('nfl_id').g.idxmax()].merge(P[['nfl_id', 'display_name', 'cf_z']], on='nfl_id').sort_values('cf_z', ascending=False)
fig = make_subplots(rows=1, cols=2, column_widths=[0.5, 0.5], horizontal_spacing=0.1,
                    subplot_titles=('Route path (upfield to the right)', 'Sideways acceleration across the rep (g)'))
B20 = []
for k, r in enumerate(best20.itertuples()):
    R = replay_data(REPS[(r.nfl_id, r.event_id, r.attempt, r.drill)]); kk = R['k']; vis = (k == 0)
    R = {**R, 'x': np.round(R['x'], 2), 'y': np.round(R['y'], 2), 'lat': np.round(R['lat'], 3), 't': np.round(R['t'], 1)}
    drill = r.drill.replace('_ROUTE', '').replace('_', ' ').title()
    fig.add_trace(go.Scatter(x=R['x'], y=R['y'], mode='lines', line=dict(color=NV, width=3), visible=vis, showlegend=False,
                             customdata=np.c_[R['t'], R['lat']], hovertemplate='t = %{customdata[0]:.1f} s<br>%{customdata[1]:.2f} g<extra></extra>'), 1, 1)
    fig.add_trace(go.Scatter(x=[R['x'][kk]], y=[R['y'][kk]], mode='markers', marker=dict(size=13, color=GD, line=dict(color='white', width=1.5)), visible=vis, showlegend=False,
                             hovertemplate=f'peak frame: {R["lat"][kk]:.2f} g<extra></extra>'), 1, 1)
    fig.add_trace(go.Scatter(x=R['t'], y=R['lat'], mode='lines', line=dict(color=NV, width=2.6), visible=vis, showlegend=False,
                             hovertemplate='t = %{x:.1f} s<br>%{y:.2f} g<extra></extra>'), 1, 2)
    fig.add_trace(go.Scatter(x=[R['t'][kk]], y=[R['lat'][kk]], mode='markers', marker=dict(size=12, color=GD, line=dict(color='white', width=1.5)), visible=vis, showlegend=False,
                             hovertemplate=f'peak frame: {R["lat"][kk]:.2f} g<extra></extra>'), 1, 2)
    B20.append((r.display_name, f'{r.display_name}: highest Cut Force rep, {drill}, {r.g:.2f} g'))
btn = []
for k, (nm, title) in enumerate(B20):
    vis = [False] * (4 * len(B20)); vis[4 * k:4 * k + 4] = [True] * 4
    btn.append(dict(label=nm, method='update', args=[{'visible': vis}, {'title.text': title}]))
fig.update_layout(title=B20[0][1], updatemenus=[dict(buttons=btn, x=1.0, xanchor='right', y=1.25, yanchor='top', direction='down', bgcolor='white', font=dict(size=13))],
                  height=500, **{**LAY, 'margin': dict(l=60, r=20, t=120, b=50)})
fig.update_xaxes(title_text='Yards upfield', row=1, col=1); fig.update_yaxes(title_text='Yards across', scaleanchor='x', scaleratio=1, row=1, col=1)
fig.update_xaxes(title_text='Seconds into the rep', row=1, col=2); fig.update_yaxes(title_text='Sideways acceleration (g)', rangemode='tozero', row=1, col=2)
show(fig)
print(f'{len(B20)} receivers in the menu, ordered by Combine Cut Force (highest first).')
'''
