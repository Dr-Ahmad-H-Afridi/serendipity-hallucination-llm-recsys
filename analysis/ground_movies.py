import gzip, csv, json, re, collections, pandas as pd
from rapidfuzz import fuzz, process
from matcher import MovieCatalogue, norm as _norm
def norm(x): return _norm(x) or ''
csv.field_size_limit(10**7)
mc = MovieCatalogue('ml_catalogue.csv')
pop = pd.read_csv('ml_popularity.csv', index_col=0)['n'].to_dict()
prof = json.load(open('ml_profiles.json'))
# IMDb index
idx = collections.defaultdict(list); dirs = {}
with gzip.open('imdb_slim.tsv.gz', 'rt', encoding='utf-8') as f:
    rd = csv.reader(f, delimiter='\t'); next(rd)
    for tc, ty, t, o, y, d in rd:
        y = int(y) if y.isdigit() else None
        dirs[tc] = [x for x in d.split('|') if x]
        for nm in {t, o} - {''}:
            k = norm(nm)
            if k: idx[k].append((y, tc, ty))
print('imdb keys', len(idx), flush=True)
byyear = collections.defaultdict(list)
for k, v in idx.items():
    for y, tc, ty in v:
        if y and ty in ('movie', 'tvMovie'): byyear[y].append(k)
for y in byyear: byyear[y] = list(set(byyear[y]))
def imdb_match(title, year):
    k = norm(title)
    if not k: return None, None
    c = idx.get(k, [])
    pref = sorted(c, key=lambda x: (x[2] not in ('movie', 'tvMovie'),))
    if year:
        for y, tc, ty in pref:
            if y and abs(y - year) <= 1: return tc, 'exact'
        pool = [kk for yy in (year - 1, year, year + 1) for kk in byyear.get(yy, [])]
        if pool:
            hit = process.extractOne(k, pool, scorer=fuzz.ratio, score_cutoff=92)
            if hit:
                for y, tc, ty in idx[hit[0]]:
                    if y and abs(y - year) <= 1: return tc, 'fuzzy'
        if pref: return pref[0][1], 'year_mismatch'
        return None, None
    return (pref[0][1], 'no_year') if pref else (None, None)

def imdb_cands(title, year):
    """All IMDb titles (any type) with this normalised title within one year."""
    k = norm(title); c = idx.get(k, [])
    films = [x for x in c if x[2] in ('movie', 'tvMovie')] or c
    if year:
        films = [x for x in films if x[0] and abs(x[0] - year) <= 1]
        films.sort(key=lambda x: abs(x[0] - year))
        if films: films = [x for x in films if x[0] == films[0][0]]   # closest year only
    return [tc for _, tc, _ in films]
def sq(x): return re.sub(r'[^a-z]', '', norm(x))
def name_ok(p, r):
    p2, r2 = sq(p), sq(r)
    if not p2 or not r2: return False
    if fuzz.ratio(p2, r2) >= 88 or fuzz.token_set_ratio(norm(p), norm(r)) >= 85: return True
    pt, rt = norm(p).split(), norm(r).split()
    if pt and rt and len(pt[-1]) > 3 and pt[-1].rstrip('s') == rt[-1].rstrip('s'): return True   # Nic Roeg, Oz Perkins, The Wachowskis
    if 'brothers' in norm(p) or 'bros' in norm(p):
        sur = norm(p).replace('brothers', '').replace('bros', '').split()
        return bool(sur) and sur[-1] in norm(r).split()
    return False
def dir_check(claimed, title, year):
    if not claimed.strip(): return 'unverifiable', None
    tcs = imdb_cands(title, year)
    real = [d for tc in tcs for d in dirs.get(tc, [])]
    if not real: return 'unverifiable', None
    parts = [p.strip() for p in re.split(r',| and |&|/', claimed) if p.strip()]
    ok = any(name_ok(p, r) for p in parts for r in real)
    return ('consistent' if ok else 'contradicted'), '|'.join(sorted(set(real)))[:200]
def variants(t):
    v = []
    base = re.sub(r'\s*\([^()]*\)', '', t).strip()          # drop parentheticals
    if base and base != t: v.append(base)
    m = re.match(r"^.*?(?:'s|’s)\b.*?[,:]\s*(.+)$", t)        # "X's director's previous film, Title"
    if m: v.append(m.group(1))
    for x in list(v) + [t]:
        if re.match(r'(?i)^the\s', x): v.append(x[4:])
        else: v.append('The ' + x)
        v.append(re.sub(r'(?i)\b(six)\b', '6', x)); v.append(re.sub(r"(?i)\s*\(?director'?s cut\)?", '', x))
    return [x for x in dict.fromkeys(v) if x and x != t]
R = pd.read_csv('items.csv', keep_default_na=False)
M = R[R.ds == 'movies'].copy()
out = []
for r in M.itertuples():
    y = int(r.year) if str(r.year).isdigit() else None
    row, s = mc.match(r.title, y)
    g, tc, how, mid = None, None, None, None
    if row is not None:
        g, mid = 'IC', int(row.movieId); tc = 'tt' + str(row.imdbId).zfill(7); how = 'movielens'
    else:
        tc, how = imdb_match(r.title, y)
        if tc and how in ('exact', 'fuzzy', 'no_year'): g = 'OOC'
        elif tc and how == 'year_mismatch':
            # title exists, year wrong: check whether it is a MovieLens title under a different year
            row2, _ = mc.match(r.title, None)
            if row2 is not None: g, mid = 'IC', int(row2.movieId); tc = 'tt' + str(row2.imdbId).zfill(7)
            else: g = 'OOC'
        else:
            g = 'FAB?'
            for vt in variants(r.title):
                row3, _ = mc.match(vt, y)
                if row3 is not None: g, mid, how = 'IC', int(row3.movieId), 'variant'; break
                tc3, how3 = imdb_match(vt, y)
                if tc3 and how3 in ('exact', 'fuzzy', 'no_year'): g, tc, how = 'OOC', tc3, 'variant'; break
    seen = (mid in set(prof[r.uid[1:]]['seen_ids'])) if mid else None
    dres, dreal = dir_check(r.director, r.title if how != 'variant' else vt, y) if g != 'FAB?' else ('n/a', None)
    out.append({'g': g, 'how': how, 'tconst': tc, 'movieId': mid, 'year_wrong': how == 'year_mismatch',
                'dir': dres, 'dir_real': dreal, 'seen': seen, 'pop': pop.get(mid, 0) if mid else None})
M = pd.concat([M.reset_index(drop=True), pd.DataFrame(out)], axis=1)
M.to_csv('movies_grounded.csv', index=False)
print(pd.crosstab([M.model, M.cond], M.g, normalize='index').round(4))
print(M.dir.value_counts())
