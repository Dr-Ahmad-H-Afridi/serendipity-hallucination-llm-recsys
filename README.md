# Serendipity or Hallucination?

Code for the paper "Serendipity or Hallucination? Grounded Evaluation of LLM-Based Recommender Systems" (A. H. Afridi, F. A. Khan, F. Sohrab). It audits three open-weight LLMs (Qwen2.5-7B, Llama-3.1-8B, Gemma-3-12B) on Serendipity-2018 (movies) and Amazon Reviews 2023 All Beauty (products) under matched relevance and serendipity prompts.

## Data (not included; licences forbid redistribution)
Put these in `data/`: Serendipity-2018 (GroupLens, unzipped to `data/serendipity-sac2018/`); Amazon Reviews 2023 `All_Beauty.jsonl.gz` and `meta_All_Beauty.jsonl.gz` (McAuley Lab); IMDb `title.basics.tsv.gz`, `title.crew.tsv.gz`, `name.basics.tsv.gz` (datasets.imdbws.com).

## Reproduce
```
pip install -r requirements.txt
export DATA=data
python src/prep_movies.py && python src/prep_beauty.py && python src/popularity.py   # user profiles and catalogues
export OPENROUTER_API_KEY=...       # ~US$0.35 for the full run
python api/run_api.py               # 2,400 prompts, temperature 0, resumable
python analysis/rerun_capped.py     # re-run responses that hit the 800-token limit at 1,600
cd analysis
python build_imdb.py                # slim IMDb reference
python parse_outputs.py             # items.csv, lists.csv
python ground_movies.py             # MovieLens + IMDb grounding, director checks
python beauty_cands.py              # repeat until "remaining 0" (time-limited chunks)
python ground_beauty.py
python stats_main.py                # Wilcoxon + Holm, human anchor (AUC)
cd ../figures && python results_figs.py && python diagrams.py
```
The exact outputs used in the paper are in `outputs/` and `results/`, so every number can be checked without re-running the models. Source datasets are not included because their licences forbid redistribution; files refer to them by identifier only.

## Layout
| Folder | Contents |
|---|---|
| `prompts/` | Exact prompt templates and the two condition sentences |
| `src/` | User-profile and catalogue building from the raw datasets |
| `api/` | Experiment runner (OpenRouter, temperature 0, resumable) |
| `analysis/` | Parsing, grounding against MovieLens/IMDb/Amazon, statistics, robustness, baselines, inflation |
| `figures/` | Scripts that generate every figure in the paper |
| `outputs/model_outputs/` | Raw responses for all 2,400 prompts (3 models) and the 100 pilot responses |
| `results/` | Item-level grounding labels, per-list scores, all statistics, human validation labels |

## Licence
MIT (code). Datasets remain under their original licences.
