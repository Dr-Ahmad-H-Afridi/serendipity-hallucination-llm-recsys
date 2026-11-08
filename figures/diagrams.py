import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],'font.size':9})
INK='#1a1a1a'; FILL='#eef2f7'; ACC='#dfe8f3'; WARM='#f6ead9'; GOOD='#e3f0e6'; BAD='#f6dede'

def box(ax,x,y,w,h,text,fc=FILL,bold=False,fs=8.5):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.02,rounding_size=0.06',fc=fc,ec=INK,lw=0.9))
    ax.text(x,y,text,ha='center',va='center',fontsize=fs,weight='bold' if bold else 'normal',color=INK,linespacing=1.25)
def arrow(ax,a,b,text=None,off=(0,0),rad=0):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=10,lw=0.9,color=INK,connectionstyle=f'arc3,rad={rad}'))
    if text: ax.text((a[0]+b[0])/2+off[0],(a[1]+b[1])/2+off[1],text,fontsize=7.5,ha='center',va='center',color=INK,style='italic')

# ---------- Fig 1: system overview ----------
fig,ax=plt.subplots(figsize=(10,4.6)); ax.set_xlim(0,10); ax.set_ylim(0,5); ax.axis('off')
box(ax,1.0,4.1,1.7,0.8,'User profile\n(liked / disliked\nitems)',ACC)
box(ax,1.0,2.7,1.7,0.8,'Prompt condition\nrelevance |\nserendipity',ACC)
box(ax,3.3,3.4,1.7,1.0,'LLM recommender\n(Qwen, Llama,\nGemma)',WARM,bold=True)
box(ax,5.6,3.4,1.7,1.0,'Output parser\nJSON repair,\nformat failures')
box(ax,7.9,4.15,1.9,0.8,'Item grounding\ncatalogue C\n→ reference R')
box(ax,7.9,2.65,1.9,0.8,'Rationale grounding\ndirector, year,\nbrand vs R')
box(ax,7.9,1.0,1.9,0.85,'Outcome label\n(six-way taxonomy)',GOOD,bold=True)
box(ax,4.9,1.0,2.3,0.85,'Measures: IC / OOC / FAB,\noverlap, popularity,\nS@k, GS@k, inflation')
box(ax,1.6,1.0,2.4,0.85,'Human anchor\nSerendipity-2018\nuser judgments',ACC)
arrow(ax,(1.85,4.0),(2.45,3.6)); arrow(ax,(1.85,2.8),(2.45,3.2))
arrow(ax,(4.15,3.4),(4.75,3.4),'10 items\n+ reasons',off=(0,0.55))
arrow(ax,(6.45,3.55),(6.95,4.05)); arrow(ax,(6.45,3.25),(6.95,2.75))
arrow(ax,(7.9,3.75),(7.9,3.05),'g(i)',off=(0.28,0)); arrow(ax,(7.9,2.25),(7.9,1.43),'r(i)',off=(0.28,0))
arrow(ax,(6.95,1.0),(6.05,1.0)); arrow(ax,(2.8,1.0),(3.75,1.0),'validates\nnovelty proxy',off=(0,0.55))
ax.text(7.9,4.75,'C: MovieLens / All Beauty    R: IMDb / human-verified sample',fontsize=7,ha='center',color='#444')
plt.tight_layout(); plt.savefig('fig1_system.png',dpi=300,bbox_inches='tight'); plt.close()

# ---------- Fig 2: taxonomy decision tree ----------
fig,ax=plt.subplots(figsize=(10,5.2)); ax.set_xlim(0,10); ax.set_ylim(0,6.2); ax.axis('off')
box(ax,5,5.6,2.6,0.6,'Recommended item i',ACC,bold=True)
box(ax,5,4.5,2.6,0.65,'In catalogue C?')
box(ax,8.2,3.4,2.2,0.65,'Exists in reference R?')
box(ax,9.0,2.1,1.6,0.6,'Item\nhallucination',BAD,bold=True)
box(ax,6.9,2.1,1.9,0.6,'Rationale\ncontradicted?')
box(ax,6.0,0.7,1.6,0.6,'Rationale\nhallucination',BAD,bold=True)
box(ax,7.9,0.7,1.6,0.6,'Out-of-\ncatalogue',WARM,bold=True)
box(ax,2.9,3.4,2.4,0.65,'Rationale contradicted?')
box(ax,4.6,2.1,1.6,0.6,'Rationale\nhallucination',BAD,bold=True)
box(ax,1.9,2.1,2.0,0.6,'Relevant? Unexpected?')
for x,t,c in [(0.7,'True\nserendipity',GOOD),(1.95,'Accurate,\nexpected',FILL),(3.2,'Mere\nnovelty',FILL)]:
    box(ax,x,0.7,1.15,0.6,t,c,bold=True,fs=8)
arrow(ax,(5,5.3),(5,4.83))
arrow(ax,(6.3,4.4),(7.6,3.73),'no',off=(0.25,0.2)); arrow(ax,(3.7,4.4),(3.2,3.73),'yes',off=(-0.25,0.2))
arrow(ax,(8.8,3.07),(9.0,2.4),'no',off=(0.3,0)); arrow(ax,(7.7,3.07),(7.1,2.4),'yes',off=(-0.3,0))
arrow(ax,(6.6,1.8),(6.1,1.0),'yes',off=(-0.3,0)); arrow(ax,(7.2,1.8),(7.7,1.0),'no',off=(0.3,0))
arrow(ax,(3.5,3.07),(4.4,2.4),'yes',off=(0.3,0)); arrow(ax,(2.4,3.07),(2.0,2.4),'no',off=(-0.3,0))
arrow(ax,(1.4,1.8),(0.8,1.0),'yes / yes',off=(-0.45,0)); arrow(ax,(1.9,1.8),(1.95,1.0),'yes / no',off=(0.32,0.05)); arrow(ax,(2.4,1.8),(3.1,1.0),'no / yes',off=(0.45,0))
plt.tight_layout(); plt.savefig('fig2_taxonomy.png',dpi=300,bbox_inches='tight'); plt.close()

# ---------- Fig 3: study design ----------
fig,ax=plt.subplots(figsize=(10,3.8)); ax.set_xlim(0,10); ax.set_ylim(0,4); ax.axis('off')
box(ax,1.2,3.0,2.0,0.9,'Serendipity-2018\nmovies\n200 users',ACC)
box(ax,1.2,1.2,2.0,0.9,'Amazon 2023\nAll Beauty\n200 users',ACC)
box(ax,3.7,2.1,1.8,1.1,'Profiles\n20 liked movies\nor 12 liked products')
box(ax,6.0,2.9,1.7,0.7,'Relevance prompt',WARM); box(ax,6.0,1.3,1.7,0.7,'Serendipity prompt',WARM)
box(ax,8.5,2.1,2.3,1.5,'3 open-weight LLMs\nQwen2.5-7B\nLlama-3.1-8B\nGemma-3-12B\ntemp. 0, via API',FILL,bold=False)
arrow(ax,(2.2,2.8),(2.8,2.35)); arrow(ax,(2.2,1.4),(2.8,1.85))
arrow(ax,(4.6,2.3),(5.15,2.8)); arrow(ax,(4.6,1.9),(5.15,1.4))
arrow(ax,(6.85,2.9),(7.35,2.45)); arrow(ax,(6.85,1.3),(7.35,1.75))
ax.text(5.0,0.25,'2 domains × 200 users × 2 conditions × 3 models = 2,400 prompts, up to 24,000 recommendations',ha='center',fontsize=8,style='italic')
ax.text(6.0,2.1,'paired:\nsame user\nboth prompts',ha='center',va='center',fontsize=7,color='#444')
plt.tight_layout(); plt.savefig('fig3_design.png',dpi=300,bbox_inches='tight'); plt.close()
print('done')
