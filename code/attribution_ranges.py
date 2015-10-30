"""
This script runs naive attribution experiments for multiple corpora.
Given the combination of a vector space and distance metric, 
we obtain results for a leave-one-text-out experiment (restricted
to authors that have more than one text in the train data.
We use a simple centroid-based, IB1-classifier. 
"""
from __future__ import print_function

import os
import matplotlib
matplotlib.use('Agg') # Must be before importing matplotlib.pyplot or pylab!
import matplotlib.pyplot as plt
import seaborn as sb
import numpy as np
from mpl_toolkits.axes_grid.anchored_artists import AnchoredText
from experimentation import attribution_experiment
from utilities import get_vocab_size

# set shared hyperparameters:
corpus_dirs = ['../data/2014/du_essays/',
               #'../data/2014/du_reviews',
               #'../data/2014/en_essays',
               #'../data/2014/en_novels',
              ]
nb_experiments = 3 # nb of different feature ranges tested
ngram_type = 'char'
ngram_size = 4
base = 'profile'
min_df = 2

for corpus_dir in corpus_dirs:
    # determine the maximum nb of features available:
    max_vocab_size = get_vocab_size(corpus_dir=corpus_dir,
                                    ngram_type=ngram_type,
                                    ngram_size=ngram_size,
                                    phase='train')
    print('\t > vocab size:', max_vocab_size)

    for vector_space in ('tf_std', 'tf_idf'):

        # clear the plot:
        sb.plt.clf()
        f, ax = plt.subplots(1,1)
        sb.set_style("darkgrid")
        ax.set_ylim(.0, 1)

        for metric in ('minmax', 'euclidean'):
            feature_ranges = [int(r) for r in \
                np.linspace(30, max_vocab_size, num=nb_experiments)]
            scores = []
            for nb_feats in feature_ranges:
                print('\t\t- nb feats:', nb_feats)
                acc_score = attribution_experiment(corpus_dir = corpus_dir,
                                                   mfi = nb_feats,
                                                   vector_space = vector_space,
                                                   ngram_type = ngram_type,
                                                   ngram_size = ngram_size,
                                                   metric = metric,
                                                   base = base,
                                                   min_df = min_df)
                print('::::: Dev score ::::::')
                print('\t + F1:', acc_score)
                scores.append(acc_score)

            # annotate the maximum score for each metric:
            maxi_score = format(np.max(np.asarray(scores)), '.1f')
            maxi_pos = feature_ranges[np.argmax(scores)]
            an1 = ax.annotate(metric+"\nmax: "+str(maxi_score),
                      xy=(maxi_pos, maxi_score), xycoords="data",
                      va="center", ha="left", fontsize=8,
                      bbox=dict(boxstyle="round,pad=0.6", fc="w"))

            # extract the coefficient of variation across the experiments:
            cv = np.std(scores)/np.mean(scores)
            cv = format(cv, '.3f')
            l = metric+' ($\sigma$/$\mu$ :'+cv+')'

            # plot the scores:
            sb.plt.plot(feature_ranges, scores, label=l)

        # add info:
        sb.plt.title(vector_space.replace('_', '-'))
        sb.plt.xlabel('# MFI')
        sb.plt.ylabel('Weighted F1')
        sb.plt.legend(loc='best')
        c = os.path.basename(corpus_dir)
        sb.plt.savefig('../output/'+c+'_'+vector_space+'_attr.pdf')






