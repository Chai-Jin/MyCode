#!/bin/sh

WORKPATH="$1"
echo "Shell script of processing $1 (argument: $2)"

#
# for error handling
#
proc() {
	$1
	if [ $? -ne 0 ]; then
		echo "Error occured during processing $WORKPATH"
		echo -e "$2" > $WORKPATH/ERROR
		exit 1
	fi
}


touch $1/DONE
rm $1/DONE

if [ "$2" == "upload" ]; then
	proc "python step0_uploadfile.py $1" "Error occured during processing input file.\nDidn't you input any unicode character in filename, or wrong type of input file?"

	proc "python step1_1.py $1" "Error occured during filtering gene/mirna (from input DEG rocessed file)."
elif [ "$2" == "filtering" ]; then
	echo 'do only filtering'
	proc "python step1_1.py $1" "Error occured during filtering gene/mirna (from input DEG rocessed file)."
else
	echo 'ignore uploading file processing(Rscript); flag not -upload-.'
fi

if [ "$3" == "customtarget" ]; then
	echo "-customtarget- mode detected, so won't fetch gene from BEST."
elif [ "$3" == "BEST" ]; then
	proc "python step_find_best_genes.py $1" "Error occured during finding genes from BEST."

	proc "python step_filter_best_genes.py $1" "Error occured during filtering genes from BEST."

	#python step_find_edges.py $1 $1/topPositive.txt $1/topPositiveNetwork.json.txt

	#python step_find_edges.py $1 $1/topNegative.txt $1/topNegativeNetwork.json.txt

	#python selectEdge.py $1
elif [ "$3" == "KEGG" ]; then
    proc "python step_pathway.py $1" "Error occured during finding genes from KEGG DB."

	proc "python step_filter_best_genes.py $1" "Error occured during filtering genes."
fi


#
# belows are common procedure
#

proc "python step_sort_filtered_best_genes.py $1" "Error occured during sorting/extracting target genes."
#cat $1/topNegative.txt > $1/topTarget.txt
#echo '' >> $1/topTarget.txt
#cat $1/topPositive.txt >> $1/topTarget.txt
#echo '' >> $1/topTarget.txt
#cat $1/topCustom.txt >> $1/topTarget.txt

#cat $1/topAbsolute.txt > $1/topTarget.txt
cat $1/topNegative.txt > $1/topTarget.txt
echo '' >> $1/topTarget.txt
cat $1/topPositive.txt >> $1/topTarget.txt
echo '' >> $1/topTarget.txt
cat $1/topCustom.txt >> $1/topTarget.txt


#proc "python selectEdge.py $1/user_input.json $1/topTarget.txt $1/filtered_gene.txt $1/filtered_mirna.txt -o $1/edges.txt" "Error occured during Edge-Selecting process."
#proc "python selectEdge2.py $1 -oe $1/edges.txt -om $1/se_meta.json" "Error occured during Edge-Selecting process."
proc "python netclient.py $1" "Error occured during Network calculating process."

#proc "python step_graph.py $1" "Error occured during generating graph data.\nDidn't you input root gene as invalid one?"

proc "python step_result.py $1" "Error occured during processing result.\nAsk for administrator if same problem occurs."

proc "python step_exp.py $1 5000" "Error occured during simulating experiment.\nAsk for administrator if same problem occurs."

#cat $1/filtered_mirnas.txt | sort -rnk4 | head -10 > $1/sub_result_mirna.txt
#cat $1/filtered_genes.txt | sort -nk4 | head -100 > $1/sub_result_gene1.txt
#cat $1/filtered_genes.txt | sort -rnk4 | head -100 > $1/sub_result_gene2.txt


#
# finished all task
#
touch $1/DONE
exit 0
