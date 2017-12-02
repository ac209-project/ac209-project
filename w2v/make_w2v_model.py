# Imports
import utils
import html
import re
import itertools
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from gensim.models.word2vec import Word2Vec, Text8Corpus, KeyedVectors

# Loads pre trained model on Text8 corpus from http://mattmahoney.net/dc/text8.zip
"""
Made with the below code:

sentences = Text8Corpus('/Users/paulblankley/Desktop/AC 209a/final_project/text8')

# These settings are both defaults. Size governs the dinemsionality of feature vectors, and sg=0 means CBOW model
model = Word2Vec(sentences, size=100, sg=0)
model.save('w2vmodel')
"""
model = Word2Vec.load('w2vmodel')

# Gets text to update the model with from my scrubbed newtext.txt file.
""" The file was made with the below code:

def clean_text(txt):
    txt = txt.lower()
    txt = html.unescape(txt)
    txt = ''.join(''.join(s)[:2] for _, s in itertools.groupby(txt))
    txt = re.sub('[^A-Za-z\s]+','',txt)
    txt = word_tokenize(txt)
    sw = set(stopwords.words('english'))
    ssw = set(stopwords.words('spanish'))
    out = []
    for word in txt:

        if word not in sw and word not in ssw:
            out.append(word)

    out = [w for w in out if w.strip()!='']
    return out

current_df = utils.make_working_df()
pl_names = current_df[['pl_id','pl_name']].drop_duplicates()

words = []
for r in pl_names['pl_name']:
    words.append(clean_text(r))

words = [w for w in words if w!=[]]

with open('newtext.txt','w') as file:
    for w in words:
        file.write(' '.join(w)+'\n')
"""
update_words = word2vec.LineSentence('newtext.txt')

# Add the new words from the playlist names to the corpus and save the model
model.build_vocab(update_words, update=True)
model.train(update_words, total_examples=model.corpus_count, epochs=model.iter)
word_vectors = model.wv
word_vectors.save('word2vec_model')
# NOTE: If you want to load use KeyedVectors.load('word2vec_model')
