# -----------
# processes standalone experiment
# returns result in 'output' directory
# -----------

import os, sys
import shutil
import task
import json

if (len(sys.argv) < 2+1):
    print("args: (hypo-file) (expname) (gn) (fp1) (fp2), file: (rootgene [tab] hypotheses) per line")
    print("+ requires [exp/work] folder")
    exit(0)

expname = sys.argv[2]
gn = 'E2f1'

if (len(sys.argv) > 3):
    gn = sys.argv[3]

# copy genefile
if (len(sys.argv) > 4):
    fp1 = sys.argv[4]
    fp2 = sys.argv[5]
else:
    # use default processed genes/mirna data.
    fp1 = 'WORK/20161103145910_757391/gene.txt'
    fp2 = 'WORK/20161103145910_757391/mirna.txt'
#    raise Exception('no miRNA / Gene network file specified.')
shutil.copyfile(fp1, os.path.join('exp', 'work', 'gene.txt'))
shutil.copyfile(fp2, os.path.join('exp', 'work', 'mirna.txt'))


r = []
disease = []
failed = 0
totals = 0

with open(sys.argv[1], 'r') as f:
    ls = filter(lambda x: len(x) > 0, f.readlines())
    totals = len(ls)
    print 'total: %d' % totals
    i = 0

    for l in ls:
        print '> %s' % l
        arg = l.split()
        #gn, hypo = arg[:2]
        hypo = l

        # prepare files/arguments to be executed
        task.createTask(
            'exp/work',
            gn,
            hypo,
			'BEST'
        )

        # remove DONE, ERROR file for clearing state
        def rmifex(p):
            if (os.path.exists(p)):
                os.remove(p)
        workpath = os.path.join('exp', 'work')
        rmifex(os.path.join(workpath, "DONE"))
        rmifex(os.path.join(workpath, "ERROR"))

        # execute shell script
        os.system('./run_method_log.sh exp/work filtering BEST')

        # check is experiment success
        if (os.path.exists(os.path.join('exp', 'work', 'ERROR'))):
            print 'result failed'
            failed += 1
            continue

        # store result
        with open('exp/work/result.json', 'r') as f:
            j = json.load(f)
            r.append(j['exp'])
        disease.append(l)

        i += 1
        print "Progress - (%d / %d)" % (i, totals)
        print '---------------------\n\n'


# write TOTAL results
with open('exp/result_%s.txt' % expname, 'w') as f:
    for l in r:
        f.write('%s\n' % '\t'.join([str(x) for x in l]))
with open('exp/result_%s_disease.txt' % expname, 'w') as f:
    for l in disease:
        f.write('%s\n' % l)

print 'done. (failed %d / total %d)' % (failed, totals)
