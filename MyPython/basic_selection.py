# basic selection

import sys

f1=open(sys.argv[1], 'r')
set_gene=set()
for line in f1:
    s1=line.strip().split('\t')[0]
    set_gene.add(s1)

f2=open(sys.argv[2],'r')
print f2.readline().strip()
for line2 in f2:
    s2=line2.strip().split('\t')[0]
    if s2 in set_gene:
        print line2.strip()
