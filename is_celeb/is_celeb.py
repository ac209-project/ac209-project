"""
Is playlist owner a celebrity or not?

Creates DataFrame with index of unique playlist owners and columns indicating
whether playlist owner deemed to be celebrity (or not) based on their name by
comparing to list of celebrity names obtained from US Magazine.

Saves DF to CSV in directory of this file.
"""

from string import digits

from nltk.metrics.distance import edit_distance
import numpy as np
from pandas import Series
import pandas as pd

import utils

#####################################################################
# Methods to prepare celebrity names and playlist owner names for comparison.

remove_digits = str.maketrans('', '', digits)  # remove numbers


def clean_owner (owner):
    """Cleans owner name so it is more easily comparable to names from
    celebrity list.
    """
    try:
        owner = owner.translate(remove_digits)
        return owner
    except:
        return owner


def clean_celeb (name):
    """Normalizes celeb name for better comparison to playlist owners."""
    # Remove spaces.
    return name.replace(' ', '')


#####################################################################

# Get list of celebrity names against which to compare playlist owners.
celeb_df = utils.load_celebs_df(lcase=True)
celeb_names = celeb_df['name'].unique().tolist()
celeb_names = [clean_celeb(name) for name in celeb_names]


def is_celeb (owner, max_thresh):
    """Returns affirmative results if edit distance divided by the length of
    the celebrity's name is below max_thresh.
    """
    if isinstance(owner, int):
        return pd.Series(data=[False, np.NaN], index=['is_celeb', 'celeb_name'])
    for celeb in celeb_names:
        if edit_distance(celeb, owner)/len(celeb) <= max_thresh:
            return Series(data=[True, celeb], index=['is_celeb', 'celeb_name'])
    return pd.Series(data=[False, np.NaN], index=['is_celeb', 'celeb_name'])


# Create results DataFrame indexed by unique playlist owners.
trk_df = utils.make_working_df()
uniq_pl_owners = trk_df['pl_owner'].unique().tolist()
results_df = pd.DataFrame(uniq_pl_owners, columns=['owner'])

# Add new fields.
results_df[['is_celeb', 'celeb_name']] = results_df['owner'].apply(is_celeb,
                                                                   args=(0.25,))

# Save results.
results_df.set_index('owner', inplace=True, drop=True)
results_df.to_csv('is_celeb_tests.csv')
