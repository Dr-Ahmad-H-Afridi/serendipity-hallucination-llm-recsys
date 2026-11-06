import json, os, time, pandas as pd
from rapidfuzz import process, fuzz
from matcher import norm as _n
def norm(x): return _n(x) or ''
T0 = time.time()
cat = json.load(open('beauty_catalogue.json')); asins = list(cat); keys = [norm(cat[a]['title']) for a in asins]
C = json.load(open('beauty_cands.json')) if os.path.exists('beauty_cands.json') else {}
R = pd.read_csv('items.csv', keep_default_na=False)
todo = [t for t in sorted(set(norm(x) for x in R[R.ds == 'beauty'].title)) if t not in C]
print('todo', len(todo), flush=True)
for i, n in enumerate(todo):
    C[n] = [(asins[j], sc) for k, sc, j in process.extract(n, keys, scorer=fuzz.token_set_ratio, limit=5, score_cutoff=85)] if n else []
    if time.time() - T0 > 250: break
json.dump(C, open('beauty_cands.json', 'w'))
print('cached', len(C), 'remaining', len(todo) - i - 1, flush=True)
