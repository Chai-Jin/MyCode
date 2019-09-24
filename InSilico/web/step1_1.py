# -*- coding: utf-8 -*-

import sys
import os
import math


work_base = sys.argv[1]
# work_base = "WORK/064070"
gene_path = os.path.join(work_base,'gene.txt')
mirna_path = os.path.join(work_base,'mirna.txt')

#
# write filtered_gene, filtered_mirna file
# type: matrix file with no HEADER
# header: (genename), (t), (pv), (logfc)
#

with open(gene_path, 'r') as gene_fh:
    label_line = gene_fh.readline().rstrip()
    labels = label_line.split("\t")
    print labels

    filtered_gene_path = os.path.join(work_base,'filtered_gene.txt')
    with open(filtered_gene_path,'w') as out_fh:
        for gene_line in list(gene_fh)[1:]:
            chunks = gene_line.rstrip().split("\t")
            gene_short_name = chunks[1].replace('"', '')
            logfc = float(chunks[2])
            t = float(chunks[4])
            pv = float(chunks[5])
            output = ("\t".join(str(item) for item in [gene_short_name, t, pv, logfc])) + "\n"
            out_fh.write(output)


with open(mirna_path, 'r') as gene_fh:
    label_line = gene_fh.readline().rstrip()
    labels = label_line.split("\t")
    print labels

    filtered_gene_path = os.path.join(work_base,'filtered_mirna.txt')
    with open(filtered_gene_path,'w') as out_fh:
        for gene_line in list(gene_fh)[1:]:
            chunks = gene_line.rstrip().split("\t")
            gene_short_name = chunks[1].replace('"', '')
            logfc = float(chunks[2])
            t = float(chunks[4])
            pv = float(chunks[5])
            output = ("\t".join(str(item) for item in [gene_short_name, t, pv, logfc])) + "\n"
            out_fh.write(output)

    #
    #         if (fpkm1 > 0) and (fpkm2 > 0) and (status1 == 'OK') and (status2 == 'OK'):
