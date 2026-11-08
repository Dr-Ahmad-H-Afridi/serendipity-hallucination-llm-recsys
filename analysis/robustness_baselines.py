"""Effect sizes (rank-biserial), robustness without the dominant near-miss titles, and non-LLM baselines."""
import pandas as pd, numpy as np, json
from scipy.stats import rankdata, wilcoxon
from statsmodels.stats.contingency_tables import mcnemar
from matcher import norm as _n
def norm(x): return _n(x) or ''
M = pd.read_csv('movies_grounded.csv', keep_default_na=False); M['k'] = M.title.map(norm)
fam = M.k.str.contains('wilderpig|huntman'); M['unres'] = (M.g == 'FAB?').astype(float)
for mdl, d in M.groupby('model'):
    x = d[~fam[d.index]]; pu = x.groupby(['uid', 'cond']).unres.mean().unstack().dropna()
    print(mdl, 'excluding near-miss families:', round(x[x.cond=='relevant'].unres.mean()*100, 2), round(x[x.cond=='serendipity'].unres.mean()*100, 2))
g = M[M.model == 'google/gemma-3-12b-it'].assign(f=fam); u = g.groupby(['uid', 'cond']).f.any().unstack()
print(mcnemar(pd.crosstab(u.relevant, u.serendipity).values, exact=True))
# baselines on the same 200 users
prof = json.load(open('ml_profiles.json')); users = list(prof)[:200]
pop = pd.read_csv('ml_popularity.csv', index_col=0)['n']; pmax = pop.max()
nov = lambda m: 1 - np.log10(max(pop.get(m, 1), 1)) / np.log10(pmax)
R = pd.read_csv('../data/serendipity-sac2018/recommendations.csv', encoding='utf-8-sig')
for name in ['MovieLens recommender', 'Most-popular unseen']:
    gs = []
    for us in users:
        seen = set(prof[us]['seen_ids'])
        lst = R[R.userId == int(us)].movieId.tolist() if name.startswith('MovieLens') else [m for m in pop.sort_values(ascending=False).index if m not in seen][:10]
        gs.append(np.mean([0 if m in seen else nov(m) for m in lst]))
    print(name, 'GS@10 =', round(np.mean(gs), 3))
