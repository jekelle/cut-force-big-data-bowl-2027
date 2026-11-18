"""Build and run a test notebook: real dev extracts (P, reps, Combine frames, as CSV) plus stand-in values for Figures 3 and 6,
then the new v21 cells exactly as they will ship. Writes test21_run.ipynb and test21.html."""
import json, os, importlib.util
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('cells21', os.path.join(HERE, 'cells21.py')); C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
v20 = json.load(open(os.path.join(HERE, 'v20.ipynb'))); src = [''.join(c['source']) for c in v20['cells']]

SETUP = r'''
import json, numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy import stats
U = '/mnt/user-data/uploads/Desktop/nfl-big-data-bowl-2027/'
V = U + 'analysis/viz/'
P = pd.read_csv(V + 'sec20_P.csv'); reps = pd.read_csv(V + 'sec20_reps.csv'); G = json.load(open(V + 'sec20_G.json'))['G']
REPS = {k: g.sort_values('time') for k, g in pd.read_csv(V + 'sec20_frames.csv').groupby(['nfl_id', 'event_id', 'attempt', 'drill'])}
_rc = pd.read_csv
def _read_csv(f, *a, **k):   # test only: the nflverse URL reads the local copy of the same file
    if str(f).startswith('https://github.com/nflverse'):
        return _rc(U + 'analysis/nflverse_combine_2000_2026.csv').drop(columns=['pos_group', 'ht_in'])
    return _rc(f, *a, **k)
pd.read_csv = _read_csv
cr = _rc(U + 'combine_results.csv').drop_duplicates('nfl_id'); players = _rc(U + 'players.csv')
rng = np.random.default_rng(1)
T10 = pd.DataFrame(dict(db_cf_z=rng.normal(size=600), sep=rng.normal(2.5, 1, 600), route=rng.choice(['OUT', 'IN', 'SLANT'], 600),
                        snap_dist=rng.normal(7, 2, 600), db=rng.integers(0, 60, 600)))
PHASES = pd.DataFrame(dict(phase=['Deceleration into the break', 'Cut Force (at the break)', 'Acceleration out of the break', 'Speed kept through the break'],
                           combine_rel=[0.31, 0.59, -0.01, 0.01], game_rel=[0.69, 0.43, 0.71, 0.43], transfer_r=[-0.07, 0.23, -0.04, 0.05],
                           stopwatch_max_abs_r=[0.40, 0.06, 0.24, 0.33], sep_b=[-0.021, -0.030, -0.007, 0.014], sep_p=[0.24, 0.09, 0.70, 0.42]))
REL_DB, REL_DBG, r_db = 0.28, 0.13, -0.05
QL = pd.DataFrame(dict(cum=[19, 87, 164, 259, 407], d=[-0.03, 0.085, 0.003, -0.028, -0.03], se=[0.068, 0.068, 0.066, 0.067, 0.066])); bsd = 1.0
WCOR = {'hsr_rt': (0.106, -0.364), 'spr_rt': (0.093, -0.445), 'eff_rt': (0.063, 0.044)}
'''
c39 = src[39]
for old, new in C.SEC16_REPL:
    assert c39.count(old) == 1, ('section 16 replacement not found once', old[:60])
    c39 = c39.replace(old, new)
helper = c39[:c39.index('# Writeup Figure 2:')]
s41 = src[41]
cells = [SETUP, src[3], s41[:s41.index('hi, lo = so.iloc')], helper, C.SEC16_ADD, C.SEC20_CARD, C.SEC20_REPLAY]
nb = nbformat.v4.new_notebook(); nb.cells = [nbformat.v4.new_code_cell(c) for c in cells]
nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
NotebookClient(nb, timeout=600, kernel_name='python3', allow_errors=True).execute()
nbformat.write(nb, os.path.join(HERE, 'test21_run.ipynb'))
body, _ = HTMLExporter().from_notebook_node(nb)
open(os.path.join(HERE, 'test21.html'), 'w').write(body)
for i, c in enumerate(nb.cells):
    for o in c.get('outputs', []):
        if o.output_type == 'stream':
            print(f'cell {i}:', o.text.strip()[:400])
        if o.output_type == 'error':
            print(f'cell {i} ERROR:', o.ename, o.evalue)
print('html bytes', len(body))
