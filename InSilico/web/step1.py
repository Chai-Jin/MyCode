# -*- coding: utf-8 -*-

import sys
import os
import math

# work_base = sys.argv[1]
work_base = "WORK/064070"
gene_path = os.path.join(work_base,'gene.txt')
mirna_path = os.path.join(work_base,'mirna.txt')

with open(gene_path, 'r') as gene_fh:
    label_line = gene_fh.readline().rstrip()
    labels = label_line.split("\t")
    print labels

    filtered_gene_path = os.path.join(work_base,'filtered_gene.txt')
    with open(filtered_gene_path,'w') as out_fh:
        for gene_line in gene_fh:
            chunks = gene_line.rstrip().split("\t")
            gene_short_name = chunks[4]
            fpkm1 = float(chunks[9])
            status1 = chunks[12]
            fpkm2 = float(chunks[13])
            status2 = chunks[16]

            if (fpkm1 > 0) and (fpkm2 > 0) and (status1 == 'OK') and (status2 == 'OK'):
                log2 = math.log(fpkm2/fpkm1, 2)
                output = ("\t".join(str(item) for item in [gene_short_name, fpkm1, fpkm2, log2])) + "\n"
                out_fh.write(output)


with open(mirna_path, 'r') as gene_fh:
    label_line = gene_fh.readline().rstrip()
    labels = label_line.split("\t")
    print labels

    filtered_gene_path = os.path.join(work_base,'filtered_mirna.txt')
    with open(filtered_gene_path,'w') as out_fh:
        for gene_line in gene_fh:
            chunks = gene_line.rstrip().split("\t")
            mirna = chunks[0]

            a1 = float(chunks[1])
            a2 = float(chunks[2])
            b1 = float(chunks[3])
            b2 = float(chunks[4])

            if a1 > 0 and a2 > 0 and b1 > 0 and b2 > 0 :
                avr_a = (a1 + a2) / 2.0
                avr_b = (b1 + b2) / 2.0

                log2 = math.log(avr_b/avr_a, 2)
                output = ("\t".join(str(item) for item in [mirna, avr_a, avr_b, log2])) + "\n"
                out_fh.write(output)


    #
    #         if (fpkm1 > 0) and (fpkm2 > 0) and (status1 == 'OK') and (status2 == 'OK'):
