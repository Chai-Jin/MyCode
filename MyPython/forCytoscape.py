import pandas as pd 
import sys 

df=pd.read_csv(sys.argv[1],sep='\t').groupby(['gene']).mean().reset_index()
df['methyl+']=df['value']>0
df.to_csv(sys.argv[2],sep='\t',index=False)
