# stop on any error.
set -ueo pipefail

# Store bam files here.
CPUS=8

# The hisat index name.
IDX=/home/jung/refs/barley_ASM32608v1_ht2_ref

# Keep track of what the aligners printed out.
RUNLOG=runlog.txt

echo "Run started by 'whoami' on 'date'" > $RUNLOG

# HISAT2 run on PE samples.
for SAMPLE in $(cat sample.txt)
do
 R1=/home/jung/sccbf/barley/fastq/${SAMPLE}_1.fastq
 R2=/home/jung/sccbf/barley/fastq/${SAMPLE}_2.fastq
 BAM=/home/jung/sccbf/barley/bam/${SAMPLE}.bam
 SUMMARY=/home/jung/sccbf/barley/fastq/${SAMPLE}_summary.txt

 echo "Running HISAT2 on paired end: $SAMPLE"
 hisat2 -p $CPUS --dta -x $IDX -1 $R1 -2 $R2 | samtools sort > $BAM 2> $RUNLOG
done
