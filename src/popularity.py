"""Count ratings per movie in Serendipity-2018 (used as the item popularity measure)."""
import os, pandas as pd
D = os.environ.get('DATA', 'data')
cnt = None
for ch in pd.read_csv(os.path.join(D, 'serendipity-sac2018/training.csv'), usecols=['movieId'],
                      dtype={'movieId': 'int32'}, chunksize=3_000_000, encoding='utf-8-sig'):
    v = ch.movieId.value_counts(); cnt = v if cnt is None else cnt.add(v, fill_value=0)
cnt.astype(int).to_csv(os.path.join(D, 'ml_popularity.csv'), header=['n'])
print(len(cnt), 'movies')
