import pandas as pd 
import numpy as np 
from itertools import combinations

import argparse
parser=argparse.ArgumentParser(usage="python jaccard.py -o result")
parser.add_argument('-o',required=True)
args=parser.parse_args()

cancerLi="BLCA BRCA COAD GBM HNSC KIRC LAML LUAD LUSC READ UCEC".split()
d={}
for cancer in cancerLi:
    df=pd.read_csv(cancer+'.ttest_go_pval_cut_community',sep='\t')
    df2=pd.DataFrame(df.groupby('community')['gene'].apply(list))
    for comID in df2.index:
        d['{}_{}'.format(cancer,comID)]=df2.loc[comID,'gene']
nC2=combinations(d.keys(),2)
with open(args.o,'w') as f:
    for pair in nC2:
        set1,set2=d[pair[0]],d[pair[1]]
        j_idx=float(np.intersect1d(set1,set2).size)/float(np.union1d(set1,set2).size)
        print >>f,"{}   {}  {}".format(pair[0],pair[1],j_idx)
