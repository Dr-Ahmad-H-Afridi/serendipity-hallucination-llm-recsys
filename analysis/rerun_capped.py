import json, os, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE=os.path.dirname(os.path.abspath(__file__)); KEY=open(f'{HERE}/.key').read().strip()
HDR={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"}
src=open(f'{HERE}/../api/run_api.py').read()
ns={'os':os,'json':json,'__file__':f'{HERE}/../api/run_api.py'}
exec(src.split('KEY = ')[0], ns)       # rebuild identical prompts
P={j['id']:j['prompt'] for j in ns['jobs']}
def call(model,prompt):
    body=json.dumps({"model":model,"messages":[{"role":"user","content":prompt}],"temperature":0,"max_tokens":1600}).encode()
    for a in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request("https://openrouter.ai/api/v1/chat/completions",data=body,headers=HDR),timeout=240) as r: d=json.load(r)
            return d["choices"][0]["message"]["content"] or "", d.get("model",model), d.get("usage",{})
        except Exception: time.sleep(3*2**a)
    raise RuntimeError('failed')
T0=time.time()
for name,model in [('gemma-3-12b-it','google/gemma-3-12b-it'),('llama-3.1-8b-instruct','meta-llama/llama-3.1-8b-instruct'),('qwen-2.5-7b-instruct','qwen/qwen-2.5-7b-instruct')]:
    f=f'{HERE}/results/{name}.jsonl'; rows=[json.loads(l) for l in open(f)]
    todo=[r for r in rows if (r.get('usage') or {}).get('completion_tokens',0)>=795 and not r.get('rerun_1600')]
    print(name,'capped:',len(todo),flush=True)
    with ThreadPoolExecutor(8) as ex:
        futs={ex.submit(call,model,P[r['id']]):r for r in todo}
        for fu in as_completed(futs):
            if time.time()-T0>240: print('TIME',flush=True); os._exit(0)
            r=futs[fu]
            try: raw,served,usage=fu.result()
            except Exception as e: print('fail',r['id'],flush=True); continue
            r.update(raw=raw,served_model=served,usage=usage,rerun_1600=True)
            with open(f+'.tmp','w') as g:
                for x in rows: g.write(json.dumps(x)+'\n')
            os.replace(f+'.tmp',f)
    print(name,'done',flush=True)
print('ALL_DONE',flush=True)
