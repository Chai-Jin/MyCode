# -*- coding: utf-8 -*-
"""filtered_best_gene """
import json
import os
import requests
import re
# network_path = "DATA/mirna_network/mmu_mirna_network.txt"
import sys

work_base = sys.argv[1]
# work_base = "WORK/064070"
best_genes_path = os.path.join(work_base, 'best_gene.txt')
filtered_genes_path = os.path.join(work_base, 'filtered_gene.txt')

with open(filtered_genes_path) as fgene:
    targets = {}
    for x in fgene:
        k = x.split("\t")[0].upper()
        v = x
        targets[k] = v

    with open(os.path.join(work_base, "filtered_best_gene.txt"),'w') as fbg:
        with open(best_genes_path) as fh:
            for l in fh:
                l = l.strip().upper()
                if l in targets:
                    fbg.write(targets[l])



