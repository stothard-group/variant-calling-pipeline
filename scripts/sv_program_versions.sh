#!/bin/bash


module load singularity

echo "Samtools version: "
singularity run -B /home -B /scratch smoove.sif samtools --version

echo "Smoove version: "

singularity run -B /home -B /scratch smoove.sif smoove

module load java

# SnpSift get path from config file
configfile=$1
while read -r line; do
  if [[ $line == snpsift_executable* ]] ;
  then
    snpsift1=${line/snpsift_executable: \"/""}
    snpsift2=${snpsift1/\"/""}
  fi
  if [[ $line == survivor* ]] ;
  then
    survivor1=${line/survivor: \"/""}
    survivor2=${survivor1/\"/""}
  fi
done < "$configfile"

echo "SnpSift version: "
java -Xmx200m -jar $snpsift2

module load StdEnv/2020
module load pindel

echo "Pindel version: "
pindel -h

module purge
module load bcftools
echo "bcftools version: "
bcftools -v

module load java picard
echo "Picard version: "

java -Xmx200m -jar $EBROOTPICARD/picard.jar MergeVcfs --version

module load StdEnv/2020 gcc/9.3.0 openmpi/4.0.3
module load manta
echo "Manta version: "
configManta.py --version

echo "SURVIVOR version: "
$survivor2


module load singularity

singularity run -B /home -B /scratch cnvnator.sif cnvnator

module purge
module load nixpkgs/16.09  gcc/7.3.0
module load perl samtools breakdancer
echo "Breakdancer version: "
breakdancer-max

module load delly boost bcftools
echo "Delly version: "
delly

module load singularity
echo "Samplot version: "
singularity run -B /home -B /scratch samplot.sif -v