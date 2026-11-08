import gzip,json,collections,random
import os
U=os.environ.get('DATA','data')+'/'
cat={}
with gzip.open(U+'meta_All_Beauty.jsonl.gz','rt') as f:
    for l in f:
        r=json.loads(l)
        cat[r['parent_asin']]={'title':r.get('title') or '','store':r.get('store') or '',
            'brand':(r.get('details') or {}).get('Brand',''),'rating_number':r.get('rating_number') or 0}
rev=collections.defaultdict(list)
with gzip.open(U+'All_Beauty.jsonl.gz','rt') as f:
    for l in f:
        r=json.loads(l)
        rev[r['user_id']].append((int(r['timestamp']),float(r['rating']),r['parent_asin']))
elig=[u for u,v in rev.items() if len(v)>=8]
print('catalogue',len(cat),'users',len(rev),'users with >=8 reviews',len(elig))
random.seed(42); sample=random.sample(elig,min(500,len(elig)))
prof={}
for u in sample:
    v=sorted(rev[u]); hist,held=v[:-1],v[-1]   # leave-last-out holdout
    liked=[cat[a]['title'] for t,r,a in reversed(hist) if r>=4 and a in cat][:20]
    prof[u]={'liked':liked,'seen':[a for _,_,a in v],'holdout':held[2]}
json.dump(prof,open(U+'beauty_profiles.json','w'))
json.dump(cat,open(U+'beauty_catalogue.json','w'))
print('profiles',len(prof))
