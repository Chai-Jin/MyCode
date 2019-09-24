import pandas as pd
import sys
inp=sys.argv[1]
out=sys.argv[2]
df=pd.read_csv(inp,sep='\t')
df['Hybridization REF']=df['Hybridization REF'].apply(lambda x:x.split('|')[0])
df.to_csv(out,index=False,sep='\t')

