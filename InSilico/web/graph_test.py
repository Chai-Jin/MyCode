# -*- coding: utf-8 -*-

import sys
import json
import os
import networkx as nx

# if os.path.exists("test.gpickle.gz"):
#     start_time = time.time()
#     G = nx.read_gpickle("test.gpickle.gz")
#     print time.time() - start_time
# else:
w = 'score'
G = nx.Graph()
G.add_path([0, 1], weight=1, score=100)
G.add_path([1, 2], weight=2, score=200)
G.add_path([1, 3], weight=1, score=100)
G.add_path([2, 4], weight=3, score=300)
G.add_path([3, 5], weight=1, score=100)
G.add_path([5, 4], weight=1, score=100)
f = 2
t = 5
print nx.shortest_path_length(G, f, t, weight=w)
print [p for p in nx.all_shortest_paths(G, f, t, weight=w)]
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
