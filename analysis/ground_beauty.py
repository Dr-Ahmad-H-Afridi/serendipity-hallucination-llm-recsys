import json, re, pandas as pd
from rapidfuzz import process, fuzz
from matcher import norm as _n
def norm(x): return _n(x) or ''
cat = json.load(open('beauty_catalogue.json'))
asins = list(cat); keys = [norm(cat[a]['title']) for a in asins]
prof = json.load(open('beauty_profiles.json'))
CANDS = json.load(open('beauty_cands.json')); AIDX = {a: i for i, a in enumerate(asins)}
R = pd.read_csv('items.csv', keep_default_na=False); B = R[R.ds == 'beauty'].copy()
out = []
for r in B.itertuples():
    n = norm(r.title); res = {'g': 'UNMATCHED', 'asin': None, 'mtitle': None, 'brand_check': 'n/a', 'seen': None, 'pop': None, 'score': 0}
    if n:
        hits = [(norm(cat[a]['title']), sc, a) for a, sc in CANDS.get(n, [])]
        for k, sc, a in hits:
            i = AIDX[a]
            if fuzz.ratio(n, k) < 60: continue
            it = cat[asins[i]]; real = norm(it['brand'] or it['store']); cb = norm(r.brand)
            if real and cb and fuzz.token_set_ratio(cb, real) < 80 and cb not in n.split()[:3] and real not in n:
                continue                                   # same-sounding product from another brand: not a match
            res.update(g='IC', asin=asins[i], mtitle=it['title'], score=sc, pop=it['rating_number'],
                       seen=asins[i] in set(prof[r.uid]['seen']),
                       brand_check=('unverifiable' if not (real and cb) else ('consistent' if fuzz.token_set_ratio(cb, real) >= 80 else 'contradicted')))
            break
    out.append(res)
B = pd.concat([B.reset_index(drop=True), pd.DataFrame(out)], axis=1)
B.to_csv('beauty_grounded.csv', index=False)
print(pd.crosstab([B.model, B.cond], B.g, normalize='index').round(4))
print(B[B.g == 'IC'].brand_check.value_counts())
