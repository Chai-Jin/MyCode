# -*- coding: utf-8 -*-
"""filtered_best_gene.txt 의 마지막 로그값으로 top10 양/음수로 뽑음"""
import json
import os
import requests
import re
from operator import itemgetter
# network_path = "DATA/mirna_network/mmu_mirna_network.txt"
import sys

work_base = sys.argv[1]
# work_base = "WORK/064070"
best_genes_path = os.path.join(work_base, 'best_gene.txt')
filtered_best_genes_path = os.path.join(work_base, 'filtered_best_gene.txt')
with open(os.path.join(work_base, 'user_input.json'),'r') as f:
    custom_genes = json.load(f)['custom_targets']

with open(filtered_best_genes_path) as fgene:
    data = []
    pos = []
    neg = []
    for x in fgene:
        x = x.strip()
        (a, b, c, d) = x.split("\t")
        data.append([a, float(b), float(c), float(d)])
        if (float(b) < 0):  # check log-foldchange
            neg.append(data[-1])
        else:
            pos.append(data[-1])

    # itemgetter index -
    # 1: log2 foldchange
    # 2: pvalue
    negative = sorted(neg, key=itemgetter(2))
    positive = sorted(pos, key=itemgetter(2))
    absolute = sorted(data, key=lambda x: abs(itemgetter(2)(x)))

    with open(os.path.join(work_base,"topNegative.txt"),'w') as negafh:
        datastr = os.linesep.join(map(lambda x:
            "\t".join([str(x[0]),str(x[1]),str(x[2]),str(x[3])]), negative[:5]))
        negafh.write(datastr)

    with open(os.path.join(work_base, "topPositive.txt"),'w') as posifh:
        datastr = os.linesep.join(map(lambda x:
            "\t".join([str(x[0]),str(x[1]),str(x[2]),str(x[3])]), positive[:5]))
        posifh.write(datastr)

    with open(os.path.join(work_base, "topAbsolute.txt"), 'w') as absofh:
        datastr = os.linesep.join(map(lambda x: "\t".join([str(x[0]), str(x[1]), str(x[2]),
            str(x[3])]), absolute[:10]))
        absofh.write(datastr)

    with open(os.path.join(work_base, "topCustom.txt"), 'w') as f:
        dic = {}
        for d_ in data:
            dic[d_[0]] = d_
        lines = []
        for g in custom_genes:
            if (g in dic):
                x = dic[g]
                lines.append('\t'.join((str(x[0]), str(x[1]), str(x[2]), str(x[3]))))
        f.write('\n'.join(lines))

