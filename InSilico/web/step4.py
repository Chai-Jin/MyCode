# -*- coding: utf-8 -*-

import sys
import json
import os
import networkx as nx

ppi_network_path = "DATA/ppi_network/STRING_PPI_Mus_musculus_Symbol_sorted.txt"
tf_network_path = "DATA/tf_network/mmu10_normal_sample.topology"

# work_base = sys.argv[1]
# key_from = sys.argv[2].lower()
# key_to = sys.argv[3].lower()

work_base = "WORK/064070"
key_from = "Trp53".lower()
key_to = "Gnai1".lower()

ppi_shorts_path = os.path.join(work_base, "ppi_shorts.txt")
tf_shorts_path = os.path.join(work_base, "tf_shorts.txt")

import time

# if os.path.exists("test.gpickle.gz"):
#     start_time = time.time()
#     G = nx.read_gpickle("test.gpickle.gz")
#     print time.time() - start_time
# else:

with open(ppi_network_path) as nfh:
    G = nx.DiGraph()
    cnt = 0
    start_time = time.time()
    for line in nfh:
        (a, b, score) = line.split("\t")
        G.add_path([a.lower(), b.lower()], weight=10-int(int(score)/100))
        cnt += 1
        if cnt % 10000 == 0:
            print cnt
    print time.time() - start_time
    # nx.write_gpickle(G,"test.gpickle.gz")
    shorts = [p for p in nx.all_shortest_paths(G, source=key_from, target=key_to, weight='weight')]
    with open(ppi_shorts_path, 'w') as ph:
        json.dump(shorts, ph)

#
# with open(tf_network_path) as nfh:
#     G = nx.DiGraph()
#     cnt = 0
#     for line in nfh:
#         (a, b, score, pvalue) = line.split("\t")
#         G.add_path([a.lower(), b.lower()])
#         cnt += 1
#         if cnt % 10000 == 0:
#             print cnt
#     shorts = [p for p in nx.all_shortest_paths(G, source=key_from, target=key_to)]
#     with open(tf_shorts_path, 'w') as ph:
#         json.dump(shorts, ph)