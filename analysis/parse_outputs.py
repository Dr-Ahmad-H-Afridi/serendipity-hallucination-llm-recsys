import json, re, glob, pandas as pd
def parse(raw):
    """Return (items, valid_json). Salvages objects from malformed arrays."""
    t = raw or ''
    t2 = re.sub(r'```(?:json)?', '', t)
    m = re.search(r'\[[\s\S]*\]', t2)
    if m:
        try:
            a = json.loads(m.group(0))
            if isinstance(a, list): return [x for x in a if isinstance(x, dict)], True
        except Exception: pass
    out = []
    for mm in re.finditer(r'\{[^{}]*\}', t2):
        s = mm.group(0)
        try: out.append(json.loads(s)); continue
        except Exception: pass
        d = {}
        for k in ['title', 'director', 'brand', 'reason']:
            km = re.search(r'"%s"\s*:\s*"((?:[^"\\]|\\.)*)' % k, s)
            if km: d[k] = km.group(1)
        ym = re.search(r'"year"\s*:\s*"?(\d{4})', s)
        if ym: d['year'] = int(ym.group(1))
        if d.get('title'): out.append(d)
    return out, False
rows = []; lists = []
for f in sorted(glob.glob('results/*.jsonl')):
    for l in open(f):
        r = json.loads(l); items, valid = parse(r['raw'])
        titles = [str(it.get('title', '')).strip().lower() for it in items]
        lists.append({'model': r['model'], 'ds': r['ds'], 'cond': r['cond'], 'uid': r['uid'], 'valid_json': valid,
                      'n_items': len(items), 'n_dup': len(titles) - len(set(titles))})
        seen = set()
        for k, it in enumerate(items):
            t = str(it.get('title', '')).strip()
            y = it.get('year'); y = int(y) if str(y).isdigit() else None
            rows.append({'model': r['model'], 'ds': r['ds'], 'cond': r['cond'], 'uid': r['uid'], 'rank': k + 1,
                         'title': t, 'year': y, 'director': str(it.get('director', '') or ''), 'brand': str(it.get('brand', '') or ''),
                         'reason': str(it.get('reason', '') or ''), 'dup_in_list': t.lower() in seen})
            seen.add(t.lower())
L = pd.DataFrame(lists); R = pd.DataFrame(rows)
L.to_csv('lists.csv', index=False); R.to_csv('items.csv', index=False)
print(L.groupby(['model', 'ds']).agg(lists=('uid', 'size'), valid=('valid_json', 'mean'), items=('n_items', 'mean'), dups=('n_dup', 'mean')).round(3))
print('total items', len(R))
