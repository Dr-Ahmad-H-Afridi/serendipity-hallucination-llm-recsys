"""
Serendipity vs hallucination: run the experiment through the OpenRouter API.
No GPU needed. Usage (in the folder holding this file and the two profile files):

    python run_api.py

It asks for your OpenRouter key, runs every model, and resumes if stopped.
"""
import os, json, time, getpass, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

MODELS = [
    "qwen/qwen-2.5-7b-instruct",
    "meta-llama/llama-3.1-8b-instruct",
    "google/gemma-3-12b-it",
]
N_USERS = 200          # users per domain
MAX_TOKENS = 800
WORKERS = int(os.environ.get("WORKERS","16"))            # parallel requests
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "results")
os.makedirs(OUTDIR, exist_ok=True)

COND = {
 "relevant": "Recommend 10 items this user is most likely to enjoy.",
 "serendipity": "Recommend 10 items that would be a pleasant surprise for this user: items they would genuinely enjoy, but that are unexpected given their history and that they would be unlikely to find on their own.",
}
def prompt(ds, cond, p):
    if ds == "movies":
        dis = ("\nThey disliked:\n" + "\n".join("- "+t for t in p["disliked"][:5]) + "\n") if p["disliked"] else ""
        return (f"You are a movie recommender system.\n\nA user rated these movies highly (most recent first):\n"
                + "\n".join("- "+t for t in p["liked"][:20]) + "\n" + dis +
                f"\nTask: {COND[cond].replace('items','movies',1)} Do not include any movie from the lists above.\n\n"
                "Return ONLY a JSON array of 10 objects, no other text, each with keys:\n"
                '"title" (string), "year" (number), "director" (string), "reason" (one sentence explaining why this user would like it).')
    return (f"You are a recommender system for an online beauty store.\n\nA user rated these products highly (most recent first):\n"
            + "\n".join("- "+t[:110] for t in p["liked"][:12]) +
            f"\n\nTask: {COND[cond].replace('items','real beauty products sold on Amazon',1)} Do not include any product from the list above.\n\n"
            "Return ONLY a JSON array of 10 objects, no other text, each with keys:\n"
            '"title" (the full product name as listed on Amazon), "brand" (string), "reason" (one sentence explaining why this user would like it).')

ml = json.load(open(os.path.join(HERE, "ml_profiles.json")))
be = json.load(open(os.path.join(HERE, "beauty_profiles.json")))
jobs = []
for u, p in list(ml.items())[:N_USERS]:
    for c in COND: jobs.append({"id": f"movies_{c}_m{u}", "ds": "movies", "cond": c, "uid": "m"+u, "prompt": prompt("movies", c, p)})
for u, p in [(u,p) for u,p in be.items() if len(p["liked"]) >= 5][:N_USERS]:
    for c in COND: jobs.append({"id": f"beauty_{c}_{u}", "ds": "beauty", "cond": c, "uid": u, "prompt": prompt("beauty", c, p)})
print(len(jobs), "prompts per model")

KEY = os.environ.get("OPENROUTER_API_KEY") or (getpass.getpass("OpenRouter API key (input hidden): ").strip())
HDR = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
       "HTTP-Referer": "https://github.com", "X-Title": "serendipity-hallucination-study"}

def available():
    req = urllib.request.Request("https://openrouter.ai/api/v1/models", headers=HDR)
    with urllib.request.urlopen(req, timeout=60) as r:
        return {m["id"] for m in json.load(r)["data"]}

def call(model, prompt):
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}],
                       "temperature": 0, "max_tokens": MAX_TOKENS}).encode()
    for attempt in range(6):
        try:
            req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=body, headers=HDR)
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.load(r)
            return d["choices"][0]["message"]["content"] or "", d.get("model", model), d.get("usage", {})
        except urllib.error.HTTPError as e:
            if e.code in (401, 402, 403):
                raise SystemExit(f"OpenRouter refused the request ({e.code}): check your key and credit.")
            time.sleep(2 ** attempt * 3)          # rate limit or server error: wait and retry
        except Exception:
            time.sleep(2 ** attempt * 3)
    raise RuntimeError("gave up after 6 attempts")

ids = available()
for model in MODELS:
    if model not in ids:
        alt = sorted(i for i in ids if model.split("/")[1].split("-")[0] in i)[:8]
        print(f"\n{model} is not on OpenRouter right now. Similar: {alt}. Skipping; tell Claude.")
        continue
    out = os.path.join(OUTDIR, model.split("/")[1] + ".jsonl")
    done = set()
    if os.path.exists(out):                      # drop a partly written last line, if any
        good = []
        for l in open(out):
            try: done.add(json.loads(l)["id"]); good.append(l if l.endswith("\n") else l + "\n")
            except Exception: pass
        open(out, "w").writelines(good)
    todo = [j for j in jobs if j["id"] not in done][:int(os.environ.get("MAX_JOBS", "100000"))]
    print(f"\n{model}: {len(done)} done, {len(todo)} to go")
    t0, n = time.time(), 0
    with ThreadPoolExecutor(WORKERS) as ex, open(out, "a") as f:
        futs = {ex.submit(call, model, j["prompt"]): j for j in todo}
        for fu in as_completed(futs):
            j = futs[fu]
            try:
                raw, served, usage = fu.result()
            except Exception as e:
                print(f"  {j['id']} failed ({e}); rerun the script to retry it"); continue
            f.write(json.dumps({"id": j["id"], "ds": j["ds"], "cond": j["cond"], "uid": j["uid"],
                                "model": model, "served_model": served, "usage": usage, "raw": raw}) + "\n"); f.flush()
            n += 1
            if n % 20 == 0 or n == len(todo):
                print(f"  {n}/{len(todo)} saved  ~{(len(todo)-n)/(n/(time.time()-t0))/60:.0f} min left", flush=True)
print("\nAll done. Upload the files in the results folder to Claude.")
