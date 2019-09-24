# run_method_1.sh with log

./run_method_1.sh $1 $2 $3 2>&1 | tee $1/log.txt
