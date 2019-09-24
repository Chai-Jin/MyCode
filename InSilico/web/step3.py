# -*- coding: utf-8 -*-

import sys
import os
import math


network_path = "DATA/mirna_network/mmu_mirna_network.txt"



work_base = sys.argv[1]
sub_mirna_path = sys.argv[2]
# work_base = "WORK/064070"
# sub_mirna_path = "WORK/064070/sub_result_mirna.txt"

outfile_path = os.path.join(work_base,"mirna_edge.txt")

with open(outfile_path, 'w') as outfile_fh:
    with open(sub_mirna_path, 'r') as sub_mirna_fh:
        for line in sub_mirna_fh:
            chunks = line.rstrip().split("\t")
            name = chunks[0]
            with open(network_path) as network_fh:
                for line2 in network_fh:
                    line2 = line2.rstrip()
                    chunks2 = line2.split("\t")
                    if chunks2[0] == name or chunks2[0] == name+"-5p":
                        outfile_fh.write(name+"\t"+line2+"\n")