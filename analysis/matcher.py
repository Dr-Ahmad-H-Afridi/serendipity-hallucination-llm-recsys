import re, json, unicodedata
import pandas as pd
from rapidfuzz import process, fuzz

def norm(s):
    s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()
    s=re.sub(r'\(\d{4}\)','',s)
    m=re.match(r'^(.*), (the|a|an)$',s.strip())          # "Matrix, The" -> "the matrix"
    if m: s=m.group(2)+' '+m.group(1)
    return re.sub(r'[^a-z0-9 ]+',' ',s).split() and ' '.join(re.sub(r'[^a-z0-9 ]+',' ',s).split())

class MovieCatalogue:
    def __init__(self,path):
        df=pd.read_csv(path,dtype=str).fillna('')
        df['year']=df.title.str.extract(r'\((\d{4})\)\s*$')[0].fillna('')
        self.df=df; self.keys=[]; self.rowidx=[]
        for i,t in enumerate(df.title):
            base=re.sub(r'\s*\(\d{4}\)\s*$','',t)
            names=[base]+re.findall(r'\(([^()]+)\)',base)          # alternate/original titles
            names.append(re.sub(r'\s*\([^()]*\)','',base))
            for nm in set(names):
                k=norm(nm)
                if k and not re.fullmatch(r'a k a',k):
                    self.keys.append(norm(re.sub(r'^a\.k\.a\. ','',nm))); self.rowidx.append(i)
    def match(self,title,year=None,threshold=90):
        """Return (row or None, score). Year (if given) must be within 1."""
        n=norm(title)
        cands=process.extract(n,self.keys,scorer=fuzz.ratio,limit=8)
        for key,score,idx in cands:
            if score<threshold: break
            r=self.df.iloc[self.rowidx[idx]]
            if year and r.year and abs(int(r.year)-int(year))>1: continue
            if year and not r.year: continue              # year-less catalogue rows are ambiguous
            return r,score
        # second pass: catalogue title contains the claimed title (e.g. "Dr. Strangelove or: ...")
        if len(n)>=6:
            for key,score,idx in process.extract(n,self.keys,scorer=fuzz.partial_ratio,limit=8):
                if score<100: break
                r=self.df.iloc[self.rowidx[idx]]
                if year and r.year and abs(int(r.year)-int(year))<=1 and len(key)<=3*len(n) and re.search(r'(^| )'+re.escape(n)+r'( |$)',key):
                    return r,99.0
        return None,(cands[0][1] if cands else 0)
    @staticmethod
    def director_ok(row,claimed):
        real=[norm(d) for d in str(row.directedBy).split(',') if norm(d)]
        if not claimed or not real: return None          # no evidence either way
        claimed=norm(claimed)
        return any(fuzz.token_set_ratio(claimed,d)>=85 for d in real if d)

class BeautyCatalogue:
    def __init__(self,path):
        cat=json.load(open(path))
        self.asins=list(cat); self.items=cat
        self.keys=[norm(cat[a]['title']) for a in self.asins]
    def match(self,title,threshold=85):
        n=norm(title)
        k,score,idx=process.extractOne(n,self.keys,scorer=fuzz.token_set_ratio)
        # token_set is lenient on short strings; also require partial length agreement
        if score>=threshold and fuzz.ratio(n,k)>=60:
            return self.asins[idx],score
        return None,score
