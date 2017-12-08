# imports
import sys
sys.path.append('../')
import pandas as pd
from collections import Counter
import utils

# Make the most common sub-genre feature
current_df = utils.make_working_df()
current_df['artist_genre'] = [tuple([i.replace('hip hop','hip_hop') for i in g]) if type(g)==list else () for g in current_df['artist_genre']]

trk_df = current_df[['trk_id','artist_genre']].drop_duplicates('trk_id')

assert(len(trk_df)==len(trk_df['trk_id'].unique()))

trk_df['artist_genre'] = [list(g) for g in trk_df['artist_genre']]

genres = []
for gen in trk_df['artist_genre']:
    if type(gen)==list:
        for gs in gen:
            genres.extend(gs.split())

gc = Counter(genres)
mc_genres = [i[0] for i in gc.most_common(15)]
print('The 15 most common genre-parts at track level:',mc_genres)

for g in mc_genres:
    trk_df['has_{}'.format(g)] = [g in ' '.join(row) for row in trk_df['artist_genre']]

trk_df['no_genre'] = [i==[] for i in trk_df['artist_genre']]

print(sum(trk_df['no_genre'])/len(trk_df['no_genre']),'do not have genres out of all tracks')

print('the working df has {} rows.'.format(len(trk_df)))

trk_df.drop('artist_genre',axis=1).to_json('data/genre_feat_trk_v2.json')
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

# out_df = pd.merge(current_df,pl_genres,how='left',on='pl_id')
# keep_cols = ['has_{}'.format(g) for g in mc_genres]+['no_genre','mode_genre','trk_id','pl_id']
# out_df = out_df[keep_cols]
pl_genres[['pl_id','mode_genre']].to_json('data/genre_feat_pl_v2.json')
