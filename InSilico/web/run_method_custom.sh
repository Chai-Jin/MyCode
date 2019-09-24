#
# runs when custom gene applied.
# don't rerun DEG/BEST gene generator
#

./run_method_1.sh $1 'target' 2>&1 | tee $1/log.txt
