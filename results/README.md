# Supplementary data — Serendipity or Hallucination?

All files are derived from the experiment described in the paper. Source datasets (Serendipity-2018, Amazon Reviews 2023, IMDb) are not redistributed; rows refer to them only by identifier (MovieLens `movieId`, IMDb `tconst`, Amazon `parent_asin`, dataset user IDs).

- `model_outputs/` — raw responses for all 800 prompts per model (prompt id, domain, condition, user id, requested and served model, token usage, raw text; `rerun_1600: true` marks the 230 responses re-run with a 1,600-token limit), plus `pilot_claude.jsonl` (100 pilot responses).
- `grounding/movies_items.csv` — one row per movie recommendation: parsed title, year, director, reason; `grounding` (IC, OOC, UNRESOLVABLE); match method; IMDb `tconst`; MovieLens `movieId`; `year_wrong`; `director_check` (consistent, contradicted, unverifiable); `seen` (already rated by the user); `pop` (ratings count).
- `grounding/beauty_items.csv` — one row per product recommendation: parsed title, brand, reason; `grounding` (IC, UNMATCHED); `asin`; `brand_check`; `seen`; `pop` (review count).
- `grounding/lists.csv` — one row per response: valid JSON, number of items, repeated items.
- `scores/` — all per-condition measures with Wilcoxon and Holm-corrected p values (Table S4); S@10, GS@10 and inflation per list; format quality; all 68 distinct unresolvable titles; novelty-proxy validation (AUC).
- `validation/validation_labels_careful_40.csv` — the 40 human labels used in the paper, with seconds per item.
- `validation/DISCARDED_rapid_pass_144.csv` — the discarded first labelling pass, released for transparency only and not used in any result.
