"""Build cut_force_bdb2027_v21.ipynb from v20: section 16 tied to the writeup's figure numbers plus interactive Figures 3, 6 and 7,
and a new section 20 with the card and the sharpest Combine rep for every receiver."""
import json, copy, importlib.util, os
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('cells21', os.path.join(HERE, 'cells21.py')); C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
nb = json.load(open(os.path.join(HERE, 'v20.ipynb'))); v21 = copy.deepcopy(nb); cells = v21['cells']
def lines(s):
    out = s.split('\n'); return [l + '\n' for l in out[:-1]] + ([out[-1]] if out[-1] else [])
intro = ''.join(cells[0]['source'])
old = 'It runs top to bottom.'
assert intro.count(old) == 1
cells[0]['source'] = lines(intro.replace(old, 'It runs top to bottom. Every writeup figure also has an interactive version (section 16 lists where each one is), and section 20 has the Cut Force card and the highest Cut Force rep for all 107 receivers.'))
assert ''.join(cells[38]['source']).startswith('## 16. Interactive figures')
cells[38]['source'] = lines(C.SEC16_MD)
c39 = ''.join(cells[39]['source'])
for o, n in C.SEC16_REPL:
    assert c39.count(o) == 1, o[:60]
    c39 = c39.replace(o, n)
cells[39]['source'] = lines(c39.rstrip('\n') + '\n' + C.SEC16_ADD.lstrip('\n'))
def md(s): return {'cell_type': 'markdown', 'metadata': {}, 'source': lines(s)}
def code(s): return {'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': lines(s.strip('\n') + '\n')}
cells += [md(C.SEC20_MD), code(C.SEC20_CARD), code(C.SEC20_REPLAY)]
for c in cells:
    if c['cell_type'] == 'code':
        c['outputs'] = []; c['execution_count'] = None
txt = json.dumps(v21)
assert '—' not in txt and '–' not in txt, 'dash found'
json.dump(v21, open(os.path.join(HERE, 'cut_force_bdb2027_v21.ipynb'), 'w'), indent=1, ensure_ascii=False)
print('cells', len(cells), 'bytes', os.path.getsize(os.path.join(HERE, 'cut_force_bdb2027_v21.ipynb')))
