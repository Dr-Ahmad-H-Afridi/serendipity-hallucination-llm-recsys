"""Inter-annotator agreement (raw and Cohen's kappa) and final validation summaries."""
import pandas as pd
from sklearn.metrics import cohen_kappa_score as kappa
from statsmodels.stats.proportion import proportion_confint as ci
D = '../results/validation/two_annotator/'
A = pd.read_excel(D + 'Annotator_A_Afridi.xlsx', 'Movies', dtype=str).fillna('')
raw = pd.read_excel(D + 'Annotator_B_Khan.xlsx', 'Movies', dtype=str, header=None).fillna('')
h = raw.index[(raw[0] == 'Item') & (raw.index > 15)][0]
B = raw.iloc[h + 1:].copy(); B.columns = list(raw.iloc[h]); B = B[B.Item.str.startswith('M')].reset_index(drop=True)
for q in ['Title status', 'Year correct?', 'Director correct?']:
    print(q, 'agreement', round((A[q] == B[q]).mean() * 100, 1), 'kappa', round(kappa(A[q], B[q]), 2))
F = pd.read_csv(D + 'final_labels_films.csv', keep_default_na=False)
u = F[F.stratum == 'm_fab']; k = (u['Title status'] == 'No such film').sum()
print('unresolvable titles wholly invented:', k, '/', len(u), ci(k, len(u), method='wilson'))
