import pandas as pd, json, csv
import os, sys
D=os.path.join(os.environ.get('DATA','data'),'serendipity-sac2018/')
ans=pd.read_csv(D+'answers.csv',encoding='utf-8-sig')
users=set(ans.userId)
# movies: tolerant parse (some rows contain unescaped quotes)
rows=[]
with open(D+'movies.csv',encoding='utf-8') as f:
    rd=csv.reader(f,quotechar='"',escapechar=None)
    header=next(rd)
    for r in rd:
        if len(r)==8: rows.append(r)
        elif len(r)>8: rows.append(r[:4]+[','.join(r[4:len(r)-3])]+r[-3:])
mov=pd.DataFrame(rows,columns=header)
mov['movieId']=mov.movieId.astype(int)
print('movies parsed',len(mov))
parts=[]
for ch in pd.read_csv(D+'training.csv',usecols=['userId','movieId','rating','timestamp'],
                      dtype={'userId':'int32','movieId':'int32','rating':'float32','timestamp':'int64'},chunksize=2_000_000,encoding='utf-8-sig'):
    parts.append(ch[ch.userId.isin(users)])
tr=pd.concat(parts); print('training rows for survey users',len(tr))
tr=tr.merge(mov[['movieId','title']],on='movieId',how='left')
prof={}
for u,g in tr.groupby('userId'):
    liked=g[g.rating>=4.0].sort_values('timestamp',ascending=False)
    disl=g[g.rating<=2.0].sort_values('timestamp',ascending=False)
    prof[int(u)]={'n_ratings':int(len(g)),
        'liked':liked.title.dropna().head(25).tolist(),
        'disliked':disl.title.dropna().head(8).tolist(),
        'seen_ids':g.movieId.astype(int).tolist()}
json.dump(prof,open(os.path.join(os.environ.get('DATA','data'),'ml_profiles.json'),'w'))
mov.to_csv(os.path.join(os.environ.get('DATA','data'),'ml_catalogue.csv'),index=False)
ans.to_csv(os.path.join(os.environ.get('DATA','data'),'ml_answers.csv'),index=False)
print('profiles',len(prof),'median ratings',int(pd.Series([p['n_ratings'] for p in prof.values()]).median()))
