# -*- coding: utf-8 -*-
"""filtered_best_gene """
import json
import os

import sys

work_base = sys.argv[1]
top_gene_path = sys.argv[2]
out_path = sys.argv[3]

# work_base = "WORK/064070"
# top_gene_path = os.path.join(work_base, "topPositive.txt")
# out_path = os.path.join(work_base, "topPositiveNetwork.json")

with open(top_gene_path) as fgene:

    result = {}
    targets = {}


    for x in fgene:
        keygene = x.split("\t")[0]

        generes = {}


        # mirna
        subres = []
        cmd = "grep -w \"%s\" DATA/mirna_network/mmu_mirna_network.txt" % keygene
        print cmd
        stdout = os.popen(cmd)
        for line in stdout:
            subres.append(line.rstrip())
        generes['mirna_network'] = subres

        # ppi_network
        subres = []
        cmd = "grep -w \"%s\" DATA/ppi_network/STRING_PPI_Mus_musculus_Symbol_sorted.txt" % keygene
        print cmd
        stdout = os.popen(cmd)
        for line in stdout:
            subres.append(line.rstrip())
        generes['ppi_network'] = subres

        # tf_network
        subres = []
        cmd = "grep -w \"%s\" DATA/tf_network/mmu10_normal_sample.topology" % keygene
        print cmd
        stdout = os.popen(cmd)
        for line in stdout:
            subres.append(line.rstrip())
        generes['tf_network'] = subres

        result[keygene] = generes

    with open(out_path,'w') as jsoutfh:
        json.dump(result, jsoutfh, indent=2)





