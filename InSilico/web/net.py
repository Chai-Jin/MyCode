"""

files -

TFnetwork : 'DATA/tf_network/mmu10_normal_sample.nonZero.topology'
PPInetwork : 'DATA/ppi_network/STRING_PPI_Mus_musculus_Symbol_sorted.over500.txt'
miRNAnetwork : 'DATA/mirna_network/mmu_mirna_network.notNULL.txt'

"""

import sys, os
import random
import setting
import copy
import json
import time

SHOW_WARNING = False

# a simple sorting function for prevent duplication
def K(g1,g2):
    if g1 < g2:
        return (g1, g2)
    else:
        return (g2, g1)

# TODO: use this function,
# instead of using ID comparsion
def NODE_CMP(n1, n2):
    return (n1['id'] == n2['id'])
def NODE_IN(n, l):
    for n2 in l:
        if NODE_CMP(n, n2):
            return True
    return False
def EDGE_CMP(e1, e2):
    return (NODE_CMP(e1[0], e2[0]) and NODE_CMP(e1[1], e2[1]) and e1[3] == e2[3])
def EDGE_REMOVE(e, l):
    for i in range(len(l)):
        if (EDGE_CMP(e, l[i])):
            del l[i]
            break


synonym = {}
def loadSynonyms():
    synpath = 'DATA/gene_synonyms.txt'
    with open(synpath,'r') as f:
        # tax_id, GeneID, symbol, Locustag, Synonyms
        for l in f.readlines()[1:]:
            if (len(l) == 0):
                continue
            args = l.split('\t')
            if (args[4] == '-'):
                continue
            sym = args[2]
            synos = args[4].split('|')
            for syno in synos:
                synonym[syno.upper()] = sym.upper()
    synonym['DICER'] = 'DICER1'

def preprocessGN(GN):
    #if (GN == 'TP53'):
    #    return 'TRP53'
    if (GN in synonym):
        GN = synonym[GN]
    return GN



class Network:
    def __init__(self):
        # metadata about network
        self.gene_root = None      # root gene
        self.gene_targets = []     # target genes

        # network data
        # - name (already set)
        # - id (for cytoscape identification)
        # - class
        # - neighbors
        # - pval
        self.nodes = {}
        # edge data
        # - (A, B, pval, class)
        # - same data used at self.nodes
        self.edges = []

        # arguments about network processing
        self.threshold = 0#0.5      # minimum allowed correlation ...?
        self.filtergenes = []       # filtering genes (only these genes will construct network)
        self.preserveRT = True      # preserve root and target genes?

        self.clear()

    def clear(self):
        self.gene_root = None
        self.gene_targets = []
        self.nodes = {}
        self.edges = []

    def status(self):
        print 'node count: %d, edge count: %d' % (len(self.nodes), len(self.edges))


    #
    # metadata
    #
    def setRoot(self, gn):
        GN = preprocessGN(gn.upper())
        if (GN not in self.nodes):
            raise Exception("%s is not in node data!" % gn)
        self.gene_root = self.nodes[GN]

    def addTarget(self, gn):
        if (gn == self.gene_root['name']):
            print('[Warning] %s gene is already placed in root' % gn)
            return
        GN = preprocessGN(gn.upper())
        if (GN not in self.nodes):
            #raise Exception("%s is not in node data!" % gn)
            print("[Warning] addTarget - %s is not in node data!" % gn)
            return
        # TODO: gene_targets -> gene_targets_GN (performance is bad)
        nodeobj = self.nodes[GN]
        #if nodeobj not in self.gene_targets:
        self.gene_targets.append( self.nodes[GN] )

    def setTargets(self, gns):
        self.gene_targets = []
        for gn in gns:
            self.addTarget(gn)

    # MUST CALL after loadNodedata() !
    def setFiltergenes(self, gns, thres=1.0):
        self.filtergenes = []
        for gn in gns:
            GN = preprocessGN(gn.upper())
            if (GN not in self.nodes):
                #raise Exception("%s is not in node data!" % gn)
                if (SHOW_WARNING):
                    print("[WARNING] filtergene = %s is not in node data!" % gn)
                continue
            if (abs(self.nodes[GN]['pval']) <= thres):
                self.filtergenes.append( self.nodes[GN] )
        if (len(self.filtergenes)):
            print("[WARNING] no genes are actually filtered")

    def clearTarget(self):
        self.gene_targets = set()



    #
    # network load/save
    #
    def loadFile(self, fp, edgetype='', bidirectional=False):
        edge_sets = set()   # to prevent edge duplication
        edges = []
        with open(fp, 'r') as f:
            for line in f.readlines():
                s=line.strip().split()
                if (len(s) < 3):
                    continue
                if (len(s) == 3):
                    s.append(1) # pval = 1, in case of no given data
                # (g1, g2, etype, pval, corr)
                edge=(s[0],s[1],edgetype,float(s[3]),float(s[2]))
                #if (edge[3] > setting.EDGE_LOAD_PVAL):
                #    continue    # we won't consider under proper pvalue network
                # TODO: in case of reverse TF direction?
                edge_hash = '%s|%s' % (s[0], s[1])
                if (edge_hash not in edge_sets):
                    edge_sets.add(edge_hash)
                    edges.append(edge)
                if (bidirectional):
                    edge_hash = '%s|%s' % (s[1], s[0])
                    edge_sets.add(edge_hash)
                    edge=(s[1],s[0],edgetype,float(s[3]),float(s[2]))
                    edges.append(edge)

        # add node first
        def appendGN(gn):
            GN = gn.upper()
            if (GN not in self.nodes):
                n = {
                    'name': gn,
                    'id': gn,
                    'neighbors': [],
                    'class': 'normal',
                    'type': '',
                    'pval': 1.0
                }
                self.nodes[GN] = n
        for edge in edges:
            appendGN(edge[0])
            appendGN(edge[1])

        # add edge
        for edge in edges:
            source = self.nodes[edge[0].upper()]
            target = self.nodes[edge[1].upper()]
            # source, target, pval, etype
            e1 = [source, target, edge[3], edgetype]
            #e2 = [target, source, edge[3], edgetype]
            self.edges.append(e1)
            #self.edges.append(e2)
            source['neighbors'].append(e1)
            #target['neighbors'].append(e2)


    # mainly for BEST node data file
    # (genename), (t), (pv), (logfc)
    def loadNodedata(self, fp, nodetype, addnew=False):
        for line in fp.readlines()[1:]:
            args = line.strip().split('\t')
            if (len(args) == 0):
                continue
            gn = args[0]
            GN = gn.upper()
            if (GN not in self.nodes):
                if (addnew):
                    n = {
                        'name': gn,
                        'id': gn,
                        'neighbors': [],
                        'class': 'normal',
                        'type': '',
                        'pval': 1.0,
                    }
                    self.nodes[GN] = n
                else:
                    continue
            n = self.nodes[GN]
            n['pval'] = float(args[2])
            if (float(args[3]) < 0):
                n['pval'] *= -1
            n['type'] = nodetype

    def loadJson(self, fp):
        # load json cytoscape file
        j = json.load(fp)
        # clear network data
        self.clear()
        # regenerate data
        nodes = j['nodes']
        edges = j['edges']
        for node in nodes:
            if ('parent' in node['classes']):
                continue
            gene_class = 'normal'
            if ('target' in node['classes']):
                gene_class = 'target'
            elif ('root' in node['classes']):
                gene_class = 'root'
            node_type = ''
            if ('type' in node['data']):
                node_type = node['data']['type']
            n = {
                'name': node['data']['name'],
                'id': node['data']['id'],
                'neighbors': [],
                'class': gene_class,
                'type': node_type, # TF or somewhat ...
                'pval': float(node['data']['pval']),
            }
            GN = n['id'].upper()
            self.nodes[GN] = n
            if (gene_class == 'target'):
                self.gene_targets.append(n)
            elif (gene_class == 'root'):
                self.gene_root = n
        for edge in edges:
            cls = edge['classes']
            pval = float(edge['data']['pval'])
            source = edge['data']['source']
            target = edge['data']['target']
            source = self.nodes[source.upper()]
            target = self.nodes[target.upper()]
            e1 = [source, target, pval, cls]
            #e2 = [target, source, pval, cls]
            source['neighbors'].append(e1)
            #target['neighbors'].append(e2)
            self.edges.append(e1)
            #self.edges.append(e2)

    def dumpJson(self, addLevel=False, metadata={}):
        # recommend: run deleteIsolatedNodes() before save/export.
        edges = []
        nodes = []
        j = {'edges': edges, 'nodes': nodes}
        for edge in self.edges:
            source = edge[0]
            target = edge[1]
            edges.append({
                'classes': edge[3],
                'data': {
                    'pval': edge[2],
                    'source': source['id'],
                    'target': target['id'],
                    }
                })

        target_ids = [n['id'] for n in self.gene_targets]
        for k, node in self.nodes.iteritems():
            class_ = node['class']
            if (node['id'] in target_ids):
                level = 2
                class_ = 'target'
            elif (node['id'] == self.gene_root['id']):
                level = 0
                class_ = 'root'
            else:
                level = 1

            nodes.append({
                'classes': '%s %s' % (class_, node['type']),
                'data': {
                    'id': node['id'],
                    'name': node['name'],
                    'pval': node['pval'],
                    'type': node['type'],
                    'level': level,
                    }
                })

        # sort edges using pvalue
        nodes.sort(key=lambda x: abs(x['data']['pval']), reverse=False)

        j.update(metadata)
        return j

    def saveJson(self, fp, addLevel=False, metadata={}):
        j = self.dumpJson(addLevel, metadata)
        json.dump(j, fp, indent=4)



    #
    # utilities (modification)
    #
    def cutEdges(self, thres):
        edge_copy = copy.copy(self.edges)
        for edge in edge_copy:
            if (abs(edge[2]) > thres):
                self.deleteEdge(edge)

    def cutNodes(self, thres):
        # DO NOT remove root/targets
        node_copy = copy.copy(self.nodes)
        for k,node in node_copy.iteritems():
            if (abs(node['pval']) > thres):
                self.deleteNode(node)

    def deleteEdge(self, edge):
        # delete from database
        EDGE_REMOVE(edge, self.edges)
        source = edge[0]
        EDGE_REMOVE(edge, source['neighbors'])

    def deleteNode(self, node):
        # check should I remove node
        if (self.preserveRT):
            if (NODE_IN(node, self.gene_targets) or NODE_CMP(node, self.gene_root)):
                return
        # remove edge first
        edge_copy = copy.copy(self.edges)
        for edge in edge_copy:
            if NODE_CMP(edge[0], node) or NODE_CMP(edge[1], node):
                self.deleteEdge(edge)
        # remove node
        GN = node['id'].upper()
        del self.nodes[GN]

    def deleteNodetype(self, nodetype):
        # delete node with specified type
        deadnodes = []
        alivenodes = []
        for x in self.nodes.iteritems():
            if (x[1]['type'] != nodetype):
                alivenodes.append(x)
            else:
                deadnodes.append(x)
        for k,node in deadnodes:
            self.deleteNode(node)

    def filterNodetype(self, nodetype):
        # delete node except specified type
        deadnodes = []
        alivenodes = []
        for x in self.nodes.iteritems():
            if (x[1]['type'] == nodetype):
                alivenodes.append(x)
            else:
                deadnodes.append(x)
        for k,node in deadnodes:
            self.deleteNode(node)

    
    def setNodetype(self, gns, nodetype):
        for gn in gns:
            GN = gn.upper()
            if (GN not in self.nodes):
                if (SHOW_WARNING):
                    print '[WARNING] setNodetype failed (%s)' % gn
                continue
            self.nodes[GN]['type'] = nodetype

    # remove edges to target which has low p-value
    def filterTargetPV(self, thres=1.0):
        failed_targets = []
        for node in self.gene_targets:
            if (abs(node['pval']) > thres):
                failed_targets.append(node)
        edge_copy = copy.copy(self.edges)
        for edge in edge_copy:
            if NODE_IN(edge[1], failed_targets):
                self.deleteEdge(edge)
        # remove middle node, in case of there's no target
        node_copy = copy.copy(self.nodes)
        die_node = []
        for k,node in node_copy.iteritems():
            if (NODE_CMP(node, self.gene_root)):
                continue
            if (NODE_IN(node, self.gene_targets)):
                continue
            met_target = False
            for nei_edge in node['neighbors']:
                if (NODE_IN(nei_edge[1], self.gene_targets)):
                    met_target = True
                    break
            if (not met_target):
                die_node.append(node)
        for node in die_node:
            self.deleteNode(node)



    #
    # utilities (search)
    #
    def getNeighbors(self, genes):
        # gather id first,
        # as gathering element will cause infinite recursion error
        r_ids = []
        gene_ids = [e['id'] for e in genes]

        for gene in genes:
            for neighbor in gene['neighbors']:
                nnodeobj = neighbor[1]
                if ((nnodeobj not in r_ids) and (nnodeobj not in gene_ids)):
                    r_ids.append(nnodeobj['id'])

        return [self.nodes[rid.upper()] for rid in r_ids]

    def getRootNeighbors(self, dist=1):
        history_neighbors = []
        cur_neighbors = [self.gene_root]
        for i in range(dist):
            history_neighbors += cur_neighbors
            cur_neighbors = self.getNeighbors(cur_neighbors)
        return cur_neighbors



    #
    # utilities (network returning)
    #
    def getNetwork(self):   # returns network of root~target
        neighbor_deg = []
        neighbor_targets = self.gene_targets

        root_nei = self.getRootNeighbors()
        target_ids = [n['id'] for n in neighbor_targets]

        # get mid genes
        # cut genes if they're not in filtergenes
        if (len(self.filtergenes)):
            filtergene_ids = [n['id'] for n in self.filtergenes]
        else:
            filtergene_ids = None
        for nei in root_nei:
            # prevent direct-connection
            if (nei['id'] in target_ids):
                continue
            if (filtergene_ids and nei['id'] not in filtergene_ids):
                continue
            for nnei in nei['neighbors']:
                if (NODE_IN(nnei[1], neighbor_targets)):
                    neighbor_deg.append(nei)
                    break
        deg_ids = [n['id'] for n in neighbor_deg]

        # generate new network
        network = Network()
        total_nodes = (neighbor_deg+neighbor_targets+[self.gene_root,]) # before copying
        total_edges = []
        total_node_ids = [n['id'] for n in total_nodes]

        # get new network edge
        for nei_edge in self.gene_root['neighbors']:
            if (nei_edge[1]['id'] in deg_ids or nei_edge[1]['id'] in target_ids):
                total_edges.append(nei_edge)
        for nei in neighbor_deg:
            for nei_edge in nei['neighbors']:
                if (nei_edge[1]['id'] in target_ids):
                    total_edges.append(nei_edge)
        
        # generate node
        for node in total_nodes:
            new_node = copy.copy(node)
            new_node['neighbors'] = []
            GN = node['name'].upper()
            network.nodes[GN] = new_node
        # modify edge to make it real network
        for edge in total_edges:
            gn_source = edge[0]['name'].upper()
            gn_target = edge[1]['name'].upper()
            source = network.nodes[gn_source]
            target = network.nodes[gn_target]
            edge[0] = source
            edge[1] = target
            source['neighbors'].append(edge)
        network.edges = total_edges

        # set root & targets
        gn_root = self.gene_root['name']
        network.gene_root = network.nodes[gn_root.upper()]
        for g in self.gene_targets:
            gn_target = g['name']
            network.gene_targets.append(network.nodes[gn_target.upper()])

        return network

    # returns self-copying network object
    def copy(self):
        network = Network()
        # should not use deepcopy, as it's link reference will be broken
        #network.nodes = copy.deepcopy(self.nodes)
        #network.edges = copy.deepcopy(self.edges)
        network.nodes = copy.copy(self.nodes)
        for k,node in network.nodes.iteritems():
            node['neighbors'] = []
        network.edges = copy.copy(self.edges)
        for edge in network.edges:
            gn_source = edge[0]['name']
            gn_target = edge[1]['name']
            source = network.nodes[gn_source.upper()]
            target = network.nodes[gn_target.upper()]
            edge[0] = source
            edge[1] = target
            source['neighbors'].append(edge)
        gn_root = self.gene_root['name']
        network.gene_root = network.nodes[gn_root.upper()]
        for g in self.gene_targets:
            gn_target = g['name']
            network.gene_targets.append(network.nodes[gn_target.upper()])
        return network



"""
class RandomEdgeNetwork(Network):
    # generates random network to use
    def __init__(self):
        Network.__init__(self)

    def getRandomNetwork(self):
        # just connect edges randomly
        genes_met_by_root = []
        node_mid = []
        edges = []

        filtering = self.nodes_
        if (len(self.filtergene)):
            filtering = self.filtergene
        for gene in filtering:
            if (gene == self.gene_root):
                continue
            if (random.random() < self.edge_prob_):
                genes_met_by_root.append(gene)
        for target in self.gene_targets:    # direct meeting
            if (random.random() < self.edge_prob_):
                edges.append((self.gene_root, target))
        for gene in genes_met_by_root:
            met_target = 0
            for target in self.gene_targets:
                if (random.random() < self.edge_prob_):
                    edges.append((gene, target))
                    met_target += 1
            if (met_target > 0):
                node_mid.append(gene)
                edges.append((self.gene_root, gene))
        return node_mid, edges

    # make real random network, and return result.
    def _getNetwork(self):
        # start
        #self.saveNetwork()
        # generate random edge
        self.generateNetwork()
        # get DEGs with preset data
        a,b = Network.getNetwork(self)
        # fin
        #self.restoreNetwork()
        return a,b
"""


#
# utils
#
def getEdgeprob(net):
    netsize = len(net.nodes)
    edgesize = len(net.edges)
    return float(netsize) / (nodecnt*(nodecnt-1)/2)


# convert to cytoscape json file
# (so we don't need cyjson.py file anymore)
def convert2cytojs(j):
    def abs2(n):
        r = 1-abs(n)
        return r
        #    return 1 / (1 + math.exp(-(-0.5+abs(n)*10)))

    nodes = j['nodes']
    # 1. set 'exp' & 'parent' value for each node
    for node in nodes:
        node['data']['exp'] = abs2(node['data']['pval'])
        s_updown = 'up'
        if (node['data']['pval'] < 0):
            s_updown = 'down'
        # add updown class
        node['classes'] += ' ' + s_updown
        # now skip if node is parent or root
        # if 'level not exists', then you should check dumpJson-level parameter.
        if (node['data']['level'] != 1):
            continue
        # add updown parent for DEG nodes (not root/target)
        if (node['data']['type'] == ''):
            raise Exception("Error occured - node type unspecified")
        node['data']['parent'] = '%s_%s' % (node['data']['type'], s_updown)

    # 2. append parent node
    nodes.append({'data': {'id': 'miRNA_up', 'level':1}, 'classes': 'parent miRNA'})
    nodes.append({'data': {'id': 'miRNA_down', 'level':1}, 'classes': 'parent miRNA'})
    nodes.append({'data': {'id': 'mRNA_up', 'level':1}, 'classes': 'parent mRNA'})
    nodes.append({'data': {'id': 'mRNA_down', 'level':1}, 'classes': 'parent mRNA'})
    nodes.append({'data': {'id': 'TF_up', 'level':1}, 'classes': 'parent TF'})
    nodes.append({'data': {'id': 'TF_down', 'level':1}, 'classes': 'parent TF'})





#
# a little simple code
# for testing extraction network from root/target genes
#
def test():
    # expected: 170 mid gene nodes
    workfolder = 'WORK/20161103145910_757391'


    user_input = os.path.join(workfolder, "user_input.json")
    target_gene = os.path.join(workfolder, 'topTarget.txt')
    geneexp = os.path.join(workfolder, 'filtered_gene.txt')
    miRNAexp = os.path.join(workfolder, 'filtered_mirna.txt')
    
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

    # load network
    # TODO: make critical section here
    net = Network()
    net.loadFile('DATA/tf_network/mmu10_normal_sample.nonZero.topology', 'TF', True)
    print '1'
    net.loadFile('DATA/ppi_network/STRING_PPI_Mus_musculus_Symbol_sorted.over500.txt', 'PPI')
    print '2'
    net.loadFile('DATA/mirna_network/mmu_mirna_network.notNULL.txt', 'miRNA', True)
    print '3'

    # set parameter
    # TODO: process alias
    net.setRoot(gene_root)
    net.setTargets(gene_targets)
    #net.updateNeighbors() # (we wont generate network as we already generated all)
    net.setFiltergenes(filtergenes)
    

    # change some type into TFs
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
    #net.setNodetype(TFs, 'TF')


    # generate new network object, from current setting
    # and save
    print 'calculating & saving networks ...'
    net.status()

    stime = time.time()
    net_result = net.getNetwork()
    print '%.2f getNetwork' % (time.time()-stime)

    net_result.status()
    # load mRNA/miRNA node type
    with open(os.path.join(workfolder, 'filtered_gene.txt'),'r') as f:
        net_result.loadNodedata(f, 'mRNA')
    with open(os.path.join(workfolder, 'filtered_mirna.txt'),'r') as f:
        net_result.loadNodedata(f, 'miRNA')
    net_result.setNodetype(TFs, 'TF')   # do this later, as mRNA/miRNA overwraps

    j = net_result.dumpJson(True)
    convert2cytojs(j)
    with open(os.path.join(workfolder, 'cydata.json'), 'w') as f:
        json.dump(j, f, indent=4)
        #net_result.saveJson(f)



# basically - extracts edge information from nodes.
if (__name__ == '__main__'):
    # just for test purpose
    # should remove for real running
    test()
    exit()

    import argparse

    parser=argparse.ArgumentParser(
            usage='''\
    %(prog)s [options] workfolder TFnetwork PPInetwork miRNAnetwork
    example: %(prog)s workfolder -TFnetwork TFnetwork -PPInetwork PPInetwork -miRNAnetwork
    miRNAnetwork -oe out.txt
    ''')

    parser.add_argument('workfolder', type=str, help='working folder')
    parser.add_argument('-TFnetwork', required=False,
        default='DATA/tf_network/mmu10_normal_sample.nonZero.topology',
        help='TF network file')
    parser.add_argument('-PPInetwork', required=False,
        default='DATA/ppi_network/STRING_PPI_Mus_musculus_Symbol_sorted.over500.txt',
        help='PPI network file')
    parser.add_argument('-miRNAnetwork', required=False,
        default='DATA/mirna_network/mmu_mirna_network.notNULL.txt',
        help='miRNA network file')
    parser.add_argument('-o', dest='outfile', required=False, metavar='str',
        default=None,
        help='outfile (json, contains nodes/edges information)')
    """
    parser.add_argument('-oe', dest='outfile_edge', required=False, metavar='str', default=None, help='outfile edge')
    parser.add_argument('-on', dest='outfile_node', required=False, metavar='str', default=None, help='outfile node')
    parser.add_argument('-om', dest='outfile_meta', required=False, metavar='str', default=None, help='outfile metadata')
    """
    args=parser.parse_args()

    user_input = os.path.join(args.workfolder, "user_input.json")
    target_gene = os.path.join(args.workfolder, 'topTarget.txt')
    geneexp = os.path.join(args.workfolder, 'filtered_gene.txt')
    miRNAexp = os.path.join(args.workfolder, 'filtered_mirna.txt')
    
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
            gene=s[0]
            if gene == gene_root:
                continue
            gene_targets.add(gene)

    # read geneexp / miRNAexp
    # you may can filter gene (with threshold about 0.03)
    # but we won't, as original one didn't do so.
    with open(geneexp, 'r') as f:
        for line in f.readlines():
            g = line.split('\t')[0].strip()
            if (g == ''):
                continue
            filtergenes.append(g)
    with open(miRNAexp, 'r') as f:
        for line in f.readlines():
            g = line.split('\t')[0].strip()
            if (g == ''):
                continue
            filtergenes.append(g)

    #read TFnetwork
    net = Network()
    print 'network loading ...'
    net.loadFile(args.TFnetwork, 'TF', True)
    net.loadFile(args.PPInetwork, 'PPI', False)
    net.loadFile(args.miRNAnetwork, 'miRNA', True)
    print 'loading done.'
    print 'generating network ...'
    net.setRoot(gene_root)
    net.setTargets(gene_targets)
    net.setFiltergenes(filtergenes)
    #net.updateNeighbors()
    print 'generating done.'

    # return node/edge
    net_out = net.getNetwork()
    net_out.saveJson(args.outfile)
    """
    nodes, edges = net.getNetwork()
    if (args.outfile_edge):
        with open(args.outfile_edge,'w') as f:
            f.write('\n'.join([
                '\t'.join([str(v) for v in e])
                for e in set(edges)])
                )
    if (args.outfile_node):
        with open(args.outfile_node,'w') as f:
            f.write('\n'.join(nodes))
    if (args.outfile_meta):
        with open(args.outfile_meta,'w') as f:
            j = getMetadata(net)
            j['degcnt'] = len(nodes)
            json.dump(j, f)
    """
