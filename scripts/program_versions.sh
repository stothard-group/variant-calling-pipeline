#!/bin/bash



module load nixpkgs/16.09; module load gcc/7.3.0; module load python/3.7; module load fastqc; module load bwa;  module load r/3.6.1; module load java/1.8.0_192 ; module load samtools/1.10 ; module load bcftools

echo "FastQC, bcftools, samtools, bwa versions: "
module list # fastqc
wait 5


module purge

module load StdEnv/2020 python/3.9

echo "MultiQC version: "
multiqc --version

module purge
wait 5
echo "BBMap script partition.sh version: "
partition.sh


# picard get path from config file
module load java/1.8.0_192
configfile=$1
while read -r line; do
  if [[ $line == picard* ]] ;
  then
    picard=${line/picard: /""}
  fi
  if [[ $line == gatk* ]] ;
  then
    gatk=${line/gatk: /""}
  fi
done < "$configfile"

echo "Picard version: "
java -Xmx200m -jar $picard SortVcf --version
echo "GATK version: "
java -Xmx200m -jar $gatk -T VariantFiltration --version
