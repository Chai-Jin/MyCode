# make result.json for summary

import sys
import os
import json

basepath = sys.argv[1]

res = {}

# Number of target gene by BEST
with open(os.path.join(basepath, 'best_gene.txt'), 'r') as f:
    res['cnt_best'] = len(f.readlines())

# Number of DEGs (by limma)
with open(os.path.join(basepath, 'gene.txt'), 'r') as f:
    res['cnt_deg'] = len(f.readlines())

# num of miRNA/PPI/TF/DEGs
with open(os.path.join(basepath, 'cydata.json'), 'r') as f:
    r = json.load(f)
    
    cnt_TF_edge = 0
    cnt_PPI_edge = 0
    cnt_miRNA_edge = 0
    cnt_graph_edge = 0
    cnt_TF_node = 0
    cnt_mRNA_node = 0
    cnt_miRNA_node = 0
    cnt_graph_node = 0
    cnt_graph_deg = 0

    for edge in r['edges']:
        cls = edge['classes'].split(',')
        if ('TF' in cls):
            cnt_TF_edge += 1
        if ('PPI' in cls):
            cnt_PPI_edge += 1
        if ('miRNA' in cls):
            cnt_miRNA_edge += 1
        cnt_graph_edge += 1
        pass
    for node in r['nodes']:
        cls = ''
        if 'parent' in node['data']:
            cls = node['data']['parent'].split(' ')[0]
            cnt_graph_deg += 1
        if ('TF' == cls):
            cnt_TF_node += 1
        if ('mRNA' == cls):
            cnt_mRNA_node += 1
        if ('miRNA' == cls):
            cnt_miRNA_node += 1
        if 'exp' in node['data']:
            cnt_graph_node += 1

    res['cnt_TF_edge'] = cnt_TF_edge
    res['cnt_PPI_edge'] = cnt_PPI_edge
    res['cnt_miRNA_edge'] = cnt_miRNA_edge
    res['cnt_graph_edge'] = cnt_graph_edge
    res['cnt_TF_node'] = cnt_TF_node
    res['cnt_mRNA_node'] = cnt_mRNA_node
    res['cnt_miRNA_node'] = cnt_miRNA_node
    res['cnt_graph_node'] = cnt_graph_node
    res['cnt_graph_deg'] = cnt_graph_deg

# score
res['score'] = 0

# p-value
res['pvalue'] = 0

with open(os.path.join(basepath, 'result.json'), 'w') as f:
    json.dump(res, f)
