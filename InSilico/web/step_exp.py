import net
import sys,os,json
import scipy.stats  # for entropy
import setting

# arg
workdir = sys.argv[1]
itercnt = int(sys.argv[2])




#
# load generated graph file
#
net_base = net.Network()
n_rootnei = 0
with open(os.path.join(workdir, 'cydata.json'),'r') as f:
    net_base.loadJson(f)
with open(os.path.join(workdir, 'cydata.json'),'r') as f:
    j = json.load(f)
    n_rootnei = j['root_nei_total_cnt']
net_base.gene_targets.sort(key=lambda x: abs(x['pval']))    # sort targets first
# load metadata of whole graph
# TODO: make data when netserver.py runs
with open('net_meta.json', 'r') as f:
    net_meta = json.load(f)






##
# input: arrayes
# output: p-value
#
def calcpv(samplearr, v):
    nNeg = 0    # elements smaller then me
    for sv in sorted(samplearr):
        if (sv >= v):
            break
        nNeg += 1
    pv = float(nNeg) / len(samplearr)
    if (pv > 0.5):
        pv = (1.0 - pv)
    return pv






def exp_network(net_base):
    #
    # gather network metadata first
    #
    n_mid = 0
    n_target = 0
    n_target_failed = 0
    for k,node in net_base.nodes.iteritems():
        if ('normal' in node['class']):
            n_mid += 1
        elif ('target' in node['class']):
            n_target += 1
            if (node['pval'] > setting.DEG_PVAL):
                n_target_failed += 1
    n_deg_per_target = [0] * n_target
    edge_encoded = []
    for edge in net_base.edges:
        i = 0
        for node in net_base.gene_targets:
            if (net.NODE_CMP(edge[1], node)):
                n_deg_per_target[i] += 1
                edge_encoded.append(i+1)
                break
            i += 1
    # append 0, if there's mid node that mets no targets (is it possible?)
    # -> len(target) * len(mid), so just append len(mid)-edcpded_edge
    if (n_mid > len(edge_encoded)):
        edge_encoded += [0] * (n_mid - len(edge_encoded))
    print n_deg_per_target




    #
    # pv calculation
    #


    # simulates how much middle DEGs will be generated
    # with base edge probability
    import random
    def calcRandomDEG(nodecnt, edgeprob):
        p = edgeprob
        r = 0           # connected mid-nodes
        r2 = 0          # connected target-nodes
        n_rootnei_sim = 0
        # simulate neighbor count of root (binominal distribution)
        """
        for i in range(nodecnt):
            if (random.random() < p):
                n_rootnei_sim += 1
        """
        #n_rootnei_sim = sum(scipy.stats.bernoulli.rvs(edgeprob, size=nodecnt))
        n_rootnei_sim = scipy.stats.binom.rvs(nodecnt, edgeprob)
        # only count indirect connection
        for i in range(n_rootnei_sim):
            if (random.random() < p):
                r += 1
        for i in range(r):
            if (random.random() < 1-pow(1-p,n_target)):
                r2 += 1
        """
        # direct - won't be used as it's not mid DEG
        for i in range(len(n_target)):
            if (random.random() < p):
                r2 += 1
        """
        return r2


    # in case of multiple targets (pvs)
    """
    r = []
    for i in range(itercnt):
        # only do DEG test for a single target
        r.append(selectEdge.randomDEG(meta, filtergenes, ["dummy",]))

    # do pvalue calculation for each targets
    pvs = []
    for k, degs in edges.iteritems():
        pvs.append(shuffle_test.calcpv(r, len(degs)))
    print pvs
    pv = sum(pvs) / float(len(pvs))
    """

    # in case of pv with whole graph
    r = []
    for i in range(itercnt):
        r.append(calcRandomDEG(net_meta['n_node'], net_meta['edgeprob']))
    pv = []
    #print sum(map(lambda x: 1 if x>n_mid else 0, r))
    pv = calcpv(r, n_mid)
    density = float(len(net_base.edges)) / (n_mid * n_target + n_mid)






    ##
    #
    #  Score Calculation
    #
    #
    
    # if target gene isn't DEG, then it's DEG count will be counted as 0.
    # (pv correction for invalid target gene)



    # ------

    # pv postfix(panelty) for empty edge
    def calc_entropy_default(pv):
        pv = (pv+n_target_failed)/(1+n_target_failed)
        return pv

    # pv postfix(panelty) using entropy
    def calc_entropy():
        pseudocnt = 0.01
        # this includes empty edge sets, also.
        n_dpt_pseudo = [x+pseudocnt for x in n_deg_per_target]

        #norm_degs = [d/float(sum(target_deg_cnts)) for d in target_deg_cnts]
        ent = scipy.stats.entropy(n_dpt_pseudo)
        max_ent = scipy.stats.entropy([1]*n_target)
        if (not max_ent):
            max_ent = 1
        # max entropy: bad case
        ent_panelty = ent/max_ent
        if (ent_panelty == 1):
            ent_panelty = 0
        return ent_panelty
        """
        panelty_score = -9999
        if (ent_panelty > 0):
            panelty_score = 1.2 - 1/ent_panelty
        score =  1 - (1 - pv) - panelty_score
        return score    # score is pv
        """

    # pv postfix using entropy - using object id
    # lower pv is good!
    def calc_entropy_id():
        max_ent = scipy.stats.entropy([1]*len(edge_encoded))
        if (not max_ent):
            max_ent = 1
        ent = scipy.stats.entropy(edge_encoded)
        # low(~= 1) entropy is bad
        ent_panelty = ent/max_ent
        return pv + (1.0-ent_panelty)

    entropy = calc_entropy()
    r = {'pv':pv, 'density': density, 'entropy':entropy}
    print r
    return r




net_base.status()

net_mRNA = net_base.copy()
net_miRNA = net_base.copy()
net_TF = net_base.copy()
net_mRNA.filterNodetype('mRNA')
net_miRNA.filterNodetype('miRNA')
net_TF.filterNodetype('TF')

net_mRNA.status()
net_miRNA.status()
net_TF.status()

# get entropy of each graph
r = []
r_base = exp_network(net_base)
r.append( r_base['pv'] )
r.append( r_base['entropy'] )
r.append( exp_network(net_mRNA)['entropy'] )
r.append( exp_network(net_miRNA)['entropy'] )
r.append( exp_network(net_TF)['entropy'] )



#
# update result json file
#
with open(os.path.join(workdir,'result.json'), 'r') as f:
    j = json.load(f)
with open(os.path.join(workdir,'result.json'), 'w') as f:
    j['exp'] = r
    json.dump(j, f)



"""
# just for temp purpose
j = net_TF.dumpJson()
net.convert2cytojs(j)
with open(os.path.join(workdir,'cydata.json'),'w') as f:
    json.dump(j, f, indent=4)
"""
