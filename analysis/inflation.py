"""Metric inflation (Eq. 3) from condition means, plus the per-user test used to compare conditions."""
import pandas as pd
from scipy.stats import wilcoxon
L = pd.read_csv('inflation_lists.csv')   # per-list S@10 and GS@10, written by stats pipeline
for (m, c), d in L.groupby(['m', 'cond']):
    S, G = d.S.mean(), d.GS.mean()
    print(f'{m:14s} {c:12s} S={S:.3f} GS={G:.3f} Infl={(S-G)/S*100:.1f}%')
for m, d in L.groupby('m'):
    p = d.pivot(index='uid', columns='cond', values=['S', 'GS'])
    ok = (p['S']['relevant'] > 0) & (p['S']['serendipity'] > 0)
    r = lambda c: (p['S'][c] - p['GS'][c]) / p['S'][c]
    print(m, 'per-user test, n =', ok.sum(), 'p =', wilcoxon(r('relevant')[ok], r('serendipity')[ok]).pvalue)
