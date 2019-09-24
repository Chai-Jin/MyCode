#
# processes uploaded file
# process limma
# - .zip -> .txt (microarray)
# - .txt (microarray)
#
# process deseq2
# - .txt (miRNA)
#
# finally, get foldchange data (per gene)
#

import DEG.raw as raw
import DEG.deg as deg
import shutil
import re
import sys, os, json

work_base = sys.argv[1]
TEMP_DIR = "TEMP/"


##
# process gene synonym
#
with open('DATA/gene_synonyms.txt','r') as f:
    ls = filter(lambda x: len(x)>0, f.readlines())
    syno = {}
    for l in ls[1:]:
        args = l.split('\t')
        gn = args[2]
        syno[gn] = gn
        ss = args[4].split('|')
        for s in ss:
            syno[s] = gn
with open(os.path.join(work_base,'user_input.json'),'r') as f:
    j = json.load(f)
keyword = j['keyword1']
if (keyword not in syno):
    raise Exception("Improper genename - that genename isn't registered in database.")
j['keyword1'] = keyword
with open(os.path.join(work_base,'user_input.json'),'w') as f:
    json.dump(j, f)


##
# desc:
# if CEL archive, process it to microarray.
# if microarray or RNA_seq,
# then get fold_change between WT and Exp series.
#  
#
# series: series information [0,1 array (0: WT, 1: Exp)]
# control: WT CEL file/WT col name array
# - (if control is none, series is required)
# - (both none, then exception.)
#
def process(inputfn, outfn, action="micro", series=None, control=None, exp=None):
    if (series == None and control == None):
        raise Exception('both series and control cannot be none')

    # 1. process CEL file into microarray (if necessary)
    # and process with limma
    if (action == "archive"):
        print 'unzipping CEL archive file ...'
        raw.unzip_archive(os.path.join(work_base,inputfn), os.path.join(work_base,'RAW'))
        inputfn = os.path.join(work_base,'RAW')+'/'
        action = "cel"
    if (action == "cel"):
        _inputfn = os.path.join(TEMP_DIR, "temp.microarray.txt")
        raw.process_cel(inputfn, _inputfn)
        inputfn = _inputfn
        action = "micro"
    # 2.
    # if microarray, process lmfit
    # elif miRNA, process deseq2
    print 'fn: %s' % inputfn
    if (action == 'micro'):
        if (series):
            deg.process_by_series(inputfn,series,'A','B','limma',outfn)
        else:
            deg.process(inputfn,control,exp,'limma',outfn)
    elif (action == 'RNAseq'):
        if (series):
            deg.process_by_series(inputfn,series,'A','B','deseq2',outfn)
        else:
            deg.process(inputfn,control,exp,'deseq2',outfn)
    else:
        raise Exception('Unexpected file format')


# get json data
arg_fn = os.path.join(work_base,'user_input.json')
with open(arg_fn, 'r') as f:
    arg = json.load(f)
mRNA_fn = arg['genefn']
miRNA_fn = arg['mirnafn']

"""
# load series data
def get_series(s):
    return [int(e) for e in s.strip().split(',')]
mRNA_series = get_series(arg['gene_series'])
miRNA_series = get_series(arg['mirna_series'])

# and process them
process(mRNA_fn, os.path.join(work_base,'gene.txt'), mRNA_series)
process(miRNA_fn, os.path.join(work_base,'mirna.txt'), miRNA_series)
"""
# load series data
def get_series(s):
    r = [e.strip() for e in re.split(',|\n|\t', s.strip())]
    r = filter(lambda x: len(x)>0, r)
    return r
t = arg['gene_ctrl']
if (t.find("||") >= 0):
    t1,t2 = t.split("||",2)
    mRNA_ctrl = get_series(t1)
    mRNA_exp = get_series(t2)
else:
    mRNA_ctrl = get_series(t)
    mRNA_exp = None
t = arg['mirna_ctrl']
if (t.find("||") >= 0):
    t1,t2 = t.split("||",2)
    miRNA_ctrl = get_series(t1)
    miRNA_exp = get_series(t2)
else:
    miRNA_ctrl = get_series(t)
    miRNA_exp = None


# and process them
process(
    os.path.join(work_base, mRNA_fn),
    os.path.join(work_base,'gene.txt'),
    arg['gene_type'],
    None,
    mRNA_ctrl,
    mRNA_exp
    )
process(
    os.path.join(work_base, miRNA_fn),
    os.path.join(work_base,'mirna.txt'),
    arg['mirna_type'],
    None,
    miRNA_ctrl,
    miRNA_exp
    )

# -- DONE --
print 'uploaded data processed successfully.'
