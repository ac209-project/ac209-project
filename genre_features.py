# imports
import sys
sys.path.append('../')
import pandas as pd
from collections import Counter
import utils

# Make the most common sub-genre feature
current_df = utils.make_working_df()
current_df['artist_genre'] = [g if type(g)==list else [] for g in current_df['artist_genre']]

genres = []
for gen in current_df['artist_genre']:
    if type(gen)==list:
        for gs in gen:
            genres.extend(gs.split())

gc = Counter(genres)
mc_genres = [i[0] for i in gc.most_common(15)]
print('The 10 most common genre-parts:',mc_genres)

for g in mc_genres:
    current_df['has_{}'.format(g)] = [g in ' '.join(row) for row in current_df['artist_genre']]

current_df['no_genre'] = [i==[] for i in current_df['artist_genre']]

print(sum(current_df['no_genre'])/len(current_df['no_genre']),'do not have genres out of all tracks')

# done with sub genre features

# Get down to the artist level without duplicates
current_df['artist_genre_t'] = [tuple(g) for g in current_df['artist_genre']]
genre_pl = current_df[['pl_id','artist_genre_t']].drop_duplicates()

# convert back to lists
genre_pl['artist_genre_list'] = [list(g) for g in genre_pl['artist_genre_t']]
genre_pl = genre_pl.drop('artist_genre_t',axis=1)

# Aggregate over the non-unique pl_id's and pick the mode.  NOTE: random selection on tie.
pl_gens = {'pl_id': [], 'mode_genre': []}
for pl in genre_pl['pl_id'].drop_duplicates():
    c = Counter([itm for sl in genre_pl[genre_pl['pl_id']==pl]['artist_genre_list'] for itm in sl])
    pl_gens['mode_genre'].append('NA' if c.most_common()==[] else c.most_common()[0][0])
    pl_gens['pl_id'].append(pl)

pl_genres = pd.DataFrame(pl_gens)

print(len(pl_genres['mode_genre'].value_counts()),'unique genres out of',len(pl_genres['mode_genre']))

out_df = pd.merge(current_df,pl_genres,how='left',on='pl_id')
keep_cols = ['has_{}'.format(g) for g in mc_genres]+['no_genre','mode_genre','trk_id']
out_df = out_df[keep_cols]
out_df.to_hdf('data/genre_features.h5','table')
