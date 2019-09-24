# -*- coding: utf-8 -*-
"""KEGG pathway 에서 keyword랑 match되는지 확인해서 gene set을 저장"""
import json
import os
import sys

work_base = sys.argv[1]
# work_base = "WORK/064070"
userinput_path = os.path.join(work_base, 'user_input.json')
KEGG_path = 'DATA/KEGG_pathway_genes.txt'

# preprocess some specific gene name
def preprocess(GN):
    # human genename -> mouse genename
    if (GN == 'TP53'):
        return 'TRP53'
    return GN
result = []
with open(os.path.join(work_base, "best_gene.txt"),'w') as bg:
    with open(userinput_path) as fh:
        userinput = json.load(fh)
        pathway = userinput['keyword2']

        with open(KEGG_path) as kegg:
            for check in kegg:
                check1 = check.split(',')[0]
                if (check1.upper() == pathway.upper()):
                    result = check.split(',')[1:]
                    bg.write('\n'.join(result))
                    exit(0)

        # no pathway found
        raise Exception('pathway %s - no pathway found.' % pathway)
