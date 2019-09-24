import pandas as pd
from math import log
import sys 

mutSamples=sys.argv[1]
exp=sys.argv[2]
out=sys.argv[3]

with open(mutSamples) as f:
    samples=f.read().strip().split()
df=pd.read_csv(exp,sep='\t')
df['no_mut']=df.loc[:,~df.columns.isin(samples)].mean(axis=1)+1
df['mut']=df.loc[:,df.columns.isin(samples)].mean(axis=1)+1
df['log2FC']=(df['mut']/df['no_mut']).apply(lambda x:log(x,2))
df.loc[:,['Hybridization REF','log2FC']].rename(columns={'Hybridization REF':'symbol'}).to_csv(out,sep='\t',index=False)

