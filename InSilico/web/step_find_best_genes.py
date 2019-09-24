# -*- coding: utf-8 -*-
"""BEST에 Gene과 Hyp 조합 쿼리해서 best_genes.txt에 저장"""
import json
import os
import requests
import re
# network_path = "DATA/mirna_network/mmu_mirna_network.txt"
import sys

work_base = sys.argv[1]
# work_base = "WORK/064070"
userinput_path = os.path.join(work_base, 'user_input.json')

# preprocess some specific gene name
def preprocess(GN):
    # human genename -> mouse genename
    if (GN == 'TP53'):
        return 'TRP53'
	if (GN == 'T EBP'):
		return 'T/EBP'
    return GN


gene_found = []
with open(userinput_path) as fh:
    userinput = json.load(fh)
    genes = userinput['keyword1']
    genes = re.split(r'[\s,]+', genes)

    hyp = userinput['keyword2']
    hyp = re.split(r'[\s,]+', hyp)

    query = " ".join(genes + hyp)

    step = 100
    start = 0

    while True:
        resp = requests.get("http://best.korea.ac.kr/s",
                     {
                         "t": "l",
                         "wt": "xslt",
                         "tr": "tmpl.xsl",
                         "otype": "8",
                         "rows": step,
                         "start": start,
                         "q": query
                     })
        content = resp.content
        assert isinstance(content, str)
        lines = content.splitlines()
        lines.pop(0)
        lines = filter(lambda x: len(x)>0, lines)

        if len(lines) == 0:
            break

        while len(lines) > 0:
            l = lines.pop(0)
            if re.match(r'^\d+', l):
                chunks = re.split(r'\s+\|\s+',l)
                GN = preprocess(chunks[1])
                gene_found.append(GN)

        start += step

# if no gene had found, then raise exception
if (len(gene_found) == 0):
	raise Exception("No Genes were found from BEST! (query: %s)" % query)

print "total: %d" % len(gene_found)
print "top10: ",gene_found[:10]
with open(os.path.join(work_base,"best_gene.txt"),'w') as outfh:
    outfh.write(os.linesep.join(gene_found))
