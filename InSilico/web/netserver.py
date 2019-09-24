#
# edgeserver.py
# pre-loads all edge information and 
#

import net
import json
import SocketServer
import netclient
import os
import setting
import time

PORT = netclient.PORT

TFnetwork = 'DATA/tf_network/mmu10_normal_sample.nonZero.topology'
PPInetwork = 'DATA/ppi_network/STRING_PPI_Mus_musculus_Symbol_sorted.over500.txt'
miRNAnetwork = 'DATA/mirna_network/mmu_mirna_network.notNULL.txt'

net_base = net.Network()
net.loadSynonyms()

print('load data at first')
print('please wait during initalization process ...')
net_base.loadFile(TFnetwork, 'TF', True)
print('***--------')
net_base.loadFile(PPInetwork, 'PPI', False)
print('******-----')
net_base.loadFile(miRNAnetwork, 'miRNA', True)
print('***********')

# load TF gene list
TFs = []
with open('DATA/Mus_musculus_TF_co-factors_list_animalTFDB.txt', 'r') as f:
    for l in f.readlines()[1:]:
        args = l.split('\t')
        TFs.append(args[3])
        TFs += args[4].strip().split(';')
with open('DATA/Mus_musculus_TFlist_animalTFDB.txt', 'r') as f:
    for l in f.readlines()[1:]:
        args = l.split('\t')
        TFs.append(args[3])
        TFs += args[4].strip().split(';')
TFs = filter(lambda x: len(x)>0, TFs)

# save metadata
with open('net_meta.json', 'w') as f:
    n_node = len(net_base.nodes)
    n_edge = len(net_base.edges)
    # miRNA shouldn't have node connection between them, so extract them
    n_miRNA = 0
    for k,node in net_base.nodes.iteritems():
        if (k[:3] == "MMU"):
            n_miRNA += 1
    n_edge_possible = (n_node*(n_node-1)/2) - (n_miRNA*(n_miRNA-1)/2)
    json.dump({
        'n_node': n_node,
        'n_edge': n_edge,
        # TODO: is it okay? not good..?
        'edgeprob': float(n_edge) / n_edge_possible
        }, f)
print('init done!')




def process(workfolder):
    user_input = os.path.join(workfolder, "user_input.json")
    target_gene = os.path.join(workfolder, 'topTarget.txt')
    geneexp = os.path.join(workfolder, 'filtered_gene.txt')
    miRNAexp = os.path.join(workfolder, 'filtered_mirna.txt')
    outfile = os.path.join(workfolder, 'cydata.json')
    
    gene_root = ''
    gene_targets = set()
    filtergenes = []

    #read user input
    with open(user_input, 'r') as f:
        gene_root = json.load(f)['keyword1']

    #read target_gene
    with open(target_gene,'r') as f:
        for line in f:
            s=line.strip().split()
            if (len(s) == 0):
                continue
            # column : genename, t, pvalue
            gene=s[0]
            if gene == gene_root:
                continue
            ##
            # hay, only high-DEG genes should be target-considered.
            # (refer: step_exp.py)
            #
            #if (float(s[2]) < setting.DEG_PVAL):
            gene_targets.add(gene)

    # read geneexp / miRNAexp
    # you may can filter gene (with threshold about 0.03)
    # but we won't, as original one didn't do so.
    with open(geneexp, 'r') as f:
        for line in f.readlines():
            args = line.split('\t')
            if (len(args) < 4):
                continue
            gn = args[0].strip()
            pval = float(args[2])
            filtergenes.append(gn)
    with open(miRNAexp, 'r') as f:
        for line in f.readlines():
            args = line.split('\t')
            if (len(args) < 4):
                continue
            gn = args[0].strip()
            pval = float(args[2])
            filtergenes.append(gn)


    # set parameter
    net_base.setRoot(gene_root)
    net_base.setTargets(gene_targets)
    #net_base.setFiltergenes(filtergenes, setting.DEG_FILTER_PVAL)

    # get network
    stime = time.time()
    net_result = net_base.getNetwork()
    print '%.2f sec getNetwork' % (time.time() - stime)
    
    with open(geneexp,'r') as f:
        net_result.loadNodedata(f, 'mRNA')
    with open(miRNAexp,'r') as f:
        net_result.loadNodedata(f, 'miRNA')
    net_result.setNodetype(TFs, 'TF')
    stime = time.time()
    net_result.cutNodes(setting.DEG_FILTER_PVAL)    # remove mid nodes
    net_result.filterTargetPV(setting.DEG_PVAL)     # remove edges for failed targets
    print '%.2f sec network modify' % (time.time() - stime)

    net_result.status()
    j = net_result.dumpJson(True)
    net.convert2cytojs(j)
    # add for experiment
    j['root_nei_total_cnt'] = len(net_base.gene_root['neighbors'])
    with open(outfile, 'w') as f:
        json.dump(j, f, indent=4)


class TCPEdgeReq(SocketServer.StreamRequestHandler):
    def handle(self):
        # read json request 
        j = json.loads(self.rfile.readline())
        rj = {"result": "failed", "code": 1}

        if ('work' not in j):
            print "argument [work] is not existing."
        else:
            work = j['work']
            if (work == 'DEGsearch'):
                print "request arrived - %s" % j['workfolder']
                # process request
                try:
                    process(j['workfolder'])
                    rj = {"result": "ok", "code": 0}
                except Exception as e:
                    rj["result"] = str(e)
                    rj["code"] = 1

                print "request done! (%s)" % j['workfolder']
            elif (work == 'targetfilter'):
                print "request arrived - filter valid genes"
                genes = j['genes']
                gene_root = j['root']
                net.setRoot(gene_root)
                validgenes = net.getTargetCandidates()
                r = []
                for g in genes:
                    if (g in validgenes):
                        r.append(g)
                rj = {"result": "ok", "code": 0}
                rj['genes'] = r
                print "request done!"
            else:
                print "unknown request work argument - %s" % work

        # return result as json data
        self.wfile.write(json.dumps(rj))

if __name__ == "__main__":
    print("server start on port %d" % PORT)
    server = SocketServer.TCPServer(("localhost", PORT), TCPEdgeReq)
    server.serve_forever()
