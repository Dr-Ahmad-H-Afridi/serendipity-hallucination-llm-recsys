import pandas as pd, numpy as np, json
from scipy.stats import wilcoxon, spearmanr, mannwhitneyu
from statsmodels.stats.multitest import multipletests
M=pd.read_csv('movies_grounded.csv',keep_default_na=False); B=pd.read_csv('beauty_grounded.csv',keep_default_na=False)
short={'qwen/qwen-2.5-7b-instruct':'Qwen2.5-7B','meta-llama/llama-3.1-8b-instruct':'Llama-3.1-8B','google/gemma-3-12b-it':'Gemma-3-12B'}
for D in (M,B): D['m']=D.model.map(short)
M['unres']=(M.g=='FAB?').astype(float); M['ooc']=(M.g=='OOC').astype(float)
M['seenf']=pd.to_numeric(M.seen.replace({'True':1,'False':0,'':np.nan}),errors='coerce')
M['popn']=pd.to_numeric(M['pop'].replace('',np.nan),errors='coerce')
M['dchk']=M.dir.isin(['consistent','contradicted']); M['dwrong']=np.where(M.dchk,(M.dir=='contradicted').astype(float),np.nan)
B['ic']=(B.g=='IC').astype(float); B['seenf']=pd.to_numeric(B.seen.replace({'True':1,'False':0,'':np.nan}),errors='coerce')
B['popn']=pd.to_numeric(B['pop'].replace('',np.nan),errors='coerce')
B['bwrong']=np.where(B.brand_check.isin(['consistent','contradicted']),(B.brand_check=='contradicted').astype(float),np.nan)
rows=[]; tests=[]
def per_user(D,col,agg='mean'):
    return D.groupby(['m','uid','cond'])[col].agg(agg).unstack()
for D,dom,meas in [(M,'Movies',[('unres','Unresolvable titles (%)','mean'),('ooc','Out-of-catalogue (%)','mean'),('seenf','Already-rated (%)','mean'),('popn','Median popularity','median'),('dwrong','Director wrong (%)','mean')]),
                   (B,'Beauty',[('ic','Matched to catalogue (%)','mean'),('seenf','Already-reviewed (%)','mean'),('popn','Median popularity','median'),('bwrong','Brand wrong (%)','mean')])]:
    for mdl in ['Qwen2.5-7B','Llama-3.1-8B','Gemma-3-12B']:
        for col,lab,agg in meas:
            pu=per_user(D[D.m==mdl],col,agg).dropna()
            a,b=pu['relevant'],pu['serendipity']
            if col=='popn': r_,s_=D[(D.m==mdl)&(D.cond=='relevant')][col].median(),D[(D.m==mdl)&(D.cond=='serendipity')][col].median()
            else: r_,s_=D[(D.m==mdl)&(D.cond=='relevant')][col].mean()*100,D[(D.m==mdl)&(D.cond=='serendipity')][col].mean()*100
            try: p=wilcoxon(a,b,zero_method='zsplit').pvalue if (a-b).abs().sum()>0 else 1.0
            except Exception: p=np.nan
            rows.append(dict(domain=dom,model=mdl,measure=lab,relevance=r_,serendipity=s_,n_users=len(pu),p=p))
T=pd.DataFrame(rows); T['p_holm']=multipletests(T.p.fillna(1),method='holm')[1]
T.to_csv('results_table.csv',index=False)
pd.set_option('display.width',200); print(T.round(4).to_string())
# Human anchor: popularity-based novelty vs users' own serendipity judgments
A=pd.read_csv('ml_answers.csv'); pop=pd.read_csv('ml_popularity.csv',index_col=0)['n']
A['pop']=A.movieId.map(pop).fillna(1); A['nov']=1-np.log10(A['pop'])/np.log10(pop.max())
A['ser']=A[['s_ser_rel','s_ser_find','s_ser_imp','s_ser_rec']].astype(str).eq('True').any(axis=1)
A['unexp']=A['s3']  # statement s3 in Serendipity-2018 concerns surprise
r1=spearmanr(A.nov,A[['s1','s2','s3','s4','s5','s6','s7','s8']].mean(axis=1))
u=mannwhitneyu(A[A.ser].nov,A[~A.ser].nov); auc=u.statistic/(A.ser.sum()*(~A.ser).sum())
r2=spearmanr(A.predictedRating,A.rating)
json.dump({'n_pairs':len(A),'ser_share':A.ser.mean(),'nov_auc_for_serendipitous':auc,'nov_auc_p':u.pvalue,'rho_pred_vs_rating':r2.correlation},open('anchor.json','w'),indent=1)
print(json.load(open('anchor.json')))
