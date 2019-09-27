# stop on any error.
set -ueo pipefail

# Store bam files here.
CPUS=8

# The hisat index name.
IDX=/data/Public/refs/ht2_ref/mm10/genome

# Keep track of what the aligners printed out.
RUNLOG=runlog.txt

echo "Run started by 'whoami' on 'date'" > $RUNLOG

# HISAT2 run on PE samples.
for SAMPLE in $(cat sample.txt)
do
 R1=/data/project/chaijin/PSMD5/fastq/${SAMPLE}_1.fastq
 R2=/data/project/chaijin/PSMD5/fastq/${SAMPLE}_2.fastq
 BAM=/data/project/chaijin/PSMD5/fastq/bam/${SAMPLE}.bam
 SUMMARY=/data/project/chaijin/PSMD5/fastq/${SAMPLE}_summary.txt

 echo "Running HISAT2 on paired end: $SAMPLE"
 hisat2 -p $CPUS --dta -x $IDX -1 $R1 -2 $R2 | samtools sort > $BAM 2> $RUNLOG
done
