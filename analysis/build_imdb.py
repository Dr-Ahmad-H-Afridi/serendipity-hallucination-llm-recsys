import gzip, csv
KEEP={"movie","tvMovie","short","video","tvSpecial","tvSeries","tvMiniSeries"}
titles={}
with gzip.open("title.basics.tsv.gz","rt",encoding="utf-8") as f:
    next(f)
    for line in f:
        t=line.rstrip("\n").split("\t")
        if t[1] in KEEP and t[4]=="0": titles[t[0]]=(t[1],t[2],t[3],t[5])
print(len(titles),"titles",flush=True)
dirs={};need=set()
with gzip.open("title.crew.tsv.gz","rt",encoding="utf-8") as f:
    next(f)
    for line in f:
        tc,d,_=line.rstrip("\n").split("\t")
        if tc in titles and d!="\\N":
            ids=d.split(",")[:4]; dirs[tc]=ids; need.update(ids)
names={}
with gzip.open("name.basics.tsv.gz","rt",encoding="utf-8") as f:
    next(f)
    for line in f:
        n=line.split("\t",2)
        if n[0] in need: names[n[0]]=n[1]
with gzip.open("imdb_slim.tsv.gz","wt",encoding="utf-8") as g:
    w=csv.writer(g,delimiter="\t"); w.writerow(["tconst","type","title","original_title","year","directors"])
    for tc,(ty,p,o,y) in titles.items():
        w.writerow([tc,ty,p,"" if o==p else o,"" if y=="\\N" else y,"|".join(names.get(i,"") for i in dirs.get(tc,[]))])
print("IMDB_DONE",flush=True)
