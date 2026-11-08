import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],'font.size':9})
W='../analysis/'
M=pd.read_csv(W+'movies_grounded.csv',keep_default_na=False)
short={'qwen/qwen-2.5-7b-instruct':'Qwen2.5-7B','meta-llama/llama-3.1-8b-instruct':'Llama-3.1-8B','google/gemma-3-12b-it':'Gemma-3-12B'}
M['m']=M.model.map(short); models=['Qwen2.5-7B','Llama-3.1-8B','Gemma-3-12B']; conds=['relevant','serendipity']; CL={'relevant':'Relevance','serendipity':'Serendipity'}
seen=M.seen.astype(str).eq('True')
M['cat']=np.select([(M.g=='IC')&~seen,(M.g=='IC')&seen,M.g=='OOC'],['New, in catalogue','Already rated','Out-of-catalogue'],'Unresolvable title')
def sp(ax):
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
# Fig 5
cats=['New, in catalogue','Already rated','Out-of-catalogue','Unresolvable title']; cols=['#9db7d9','#d9d9d9','#f2c98a','#c0504d']
fig,ax=plt.subplots(figsize=(7.2,3.0)); x=[];labels=[];bottom=None;pos=0;xt=[]
share=M.groupby(['m','cond']).cat.value_counts(normalize=True).unstack().fillna(0)*100
xs=[];names=[]
for i,mdl in enumerate(models):
    for j,c in enumerate(conds):
        xs.append(i*2.6+j); names.append(f'{mdl}\n{CL[c]}')
b=np.zeros(len(xs))
for cat,col in zip(cats,cols):
    v=[share.loc[(mdl,c),cat] for mdl in models for c in conds]
    ax.bar(xs,v,bottom=b,color=col,edgecolor='#1a1a1a',lw=0.5,width=0.85,label=cat); b+=v
ax.set_xticks(xs); ax.set_xticklabels([CL[c] for mdl in models for c in conds],fontsize=7.5)
for i,mdl in enumerate(models): ax.text(i*2.6+0.5,-17,mdl,ha='center',fontsize=8.5,weight='bold')
ax.set_ylabel('Share of recommendations (%)'); ax.set_ylim(0,100); ax.legend(ncol=4,frameon=False,fontsize=7.5,loc='upper center',bbox_to_anchor=(0.5,1.14)); sp(ax)
plt.tight_layout(); plt.savefig('fig5_outcomes.png',dpi=300,bbox_inches='tight'); plt.close()
# Fig 6: unresolvable rate with user bootstrap CI
rng=np.random.default_rng(0); CI=[]
fig,ax=plt.subplots(figsize=(3.6,2.8))
for j,c in enumerate(conds):
    means=[];lo=[];hi=[]
    for mdl in models:
        g=M[(M.m==mdl)&(M.cond==c)].groupby('uid').g.agg(lambda s:((s=='FAB?').sum(),len(s)))
        k=np.array([x[0] for x in g]); n=np.array([x[1] for x in g])
        idx=[rng.integers(0,len(k),len(k)) for _ in range(2000)]
        bs=[k[i].sum()/n[i].sum() for i in idx]
        means.append(k.sum()/n.sum()*100); lo.append(np.percentile(bs,2.5)*100); hi.append(np.percentile(bs,97.5)*100)
        CI.append((mdl,c,round(means[-1],2),round(lo[-1],2),round(hi[-1],2)))
    xx=np.arange(3)+(j-0.5)*0.36
    ax.bar(xx,means,width=0.34,color=['#9db7d9','#f2c98a'][j],edgecolor='#1a1a1a',lw=0.5,label=CL[c])
    ax.errorbar(xx,means,yerr=[np.array(means)-lo,np.array(hi)-means],fmt='none',ecolor='#1a1a1a',capsize=2,lw=0.8)
ax.set_xticks(range(3)); ax.set_xticklabels(models,fontsize=7.5); ax.set_ylabel('Unresolvable titles (%)'); ax.legend(frameon=False,fontsize=7.5); sp(ax)
plt.tight_layout(); plt.savefig('fig6_unresolvable.png',dpi=300,bbox_inches='tight'); plt.close()
# Fig 7: long-tail shift
fig,(a,b2)=plt.subplots(1,2,figsize=(7.2,2.8))
pop=pd.to_numeric(M['pop'].replace('',np.nan),errors='coerce'); M['popn']=pop
for j,c in enumerate(conds):
    xx=np.arange(3)+(j-0.5)*0.36
    a.bar(xx,[seen[(M.m==m_)&(M.cond==c)&(M.g=='IC')].mean()*100 for m_ in models],width=0.34,color=['#9db7d9','#f2c98a'][j],edgecolor='#1a1a1a',lw=0.5,label=CL[c])
    b2.bar(xx,[M[(M.m==m_)&(M.cond==c)].popn.median() for m_ in models],width=0.34,color=['#9db7d9','#f2c98a'][j],edgecolor='#1a1a1a',lw=0.5)
for ax_,yl,t in [(a,'Already-rated items (%)','(a) History overlap'),(b2,'Median ratings per film (log)','(b) Popularity of recommended films')]:
    ax_.set_xticks(range(3)); ax_.set_xticklabels(models,fontsize=7.5); ax_.set_ylabel(yl); ax_.set_title(t,fontsize=9); sp(ax_)
b2.set_yscale('log'); a.legend(frameon=False,fontsize=7.5)
plt.tight_layout(); plt.savefig('fig7_longtail.png',dpi=300,bbox_inches='tight'); plt.close()
# Fig 8: S vs GS per list
L=pd.read_csv(W+'inflation_lists.csv')
fig,axs=plt.subplots(1,2,figsize=(7.2,3.1),sharey=True)
for ax_,c in zip(axs,conds):
    for mdl,mk,col in zip(models,['o','s','^'],['#4c72b0','#55a868','#c44e52']):
        d=L[(L.m==mdl)&(L.cond==c)]; ax_.scatter(d.S,d.GS,s=9,marker=mk,alpha=0.55,color=col,label=mdl,edgecolors='none')
    ax_.plot([0,1],[0,1],'--',color='#1a1a1a',lw=0.8); ax_.set_xlim(0,1); ax_.set_ylim(0,1)
    ax_.set_xlabel('Ungrounded serendipity score S@10'); ax_.set_title(CL[c]+' prompt',fontsize=9); sp(ax_)
axs[0].set_ylabel('Grounded score GS@10'); axs[1].legend(frameon=False,fontsize=7.5,loc='upper left')
plt.tight_layout(); plt.savefig('fig8_inflation.png',dpi=300,bbox_inches='tight'); plt.close()
print(CI)
