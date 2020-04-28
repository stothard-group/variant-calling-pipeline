# Variant Calling Workflow Overview

This document outlines the steps performed by the snakemake workflow 
`VariantCalling.sm`. The input files are raw fastq files created from a 
multiplexed HiSeq sequencing run. The final output files are .bam mapped read 
files for each sample, and filtered SNP and Indel VCF files. Although files are 
processed generally in the order described here, some rules may be executed 
concurrently, e.g. fastqc_raw and split.

## Read Mapping

### 1. Run FastQC on raw data
**Rule: fastqc_raw**

The program FastQC is run on all input read files.

### 2. Split files for faster processing
**Rule: split**

Raw fastq files are split into user-defined chunks using the partition.sh 
script as part of BBMap. Files are normally split so that resulting files 
contain fewer than 100 million reads.

### 3. Run Trimmomatic on split files
**Rule: trimmomatic**

Each split file is trimmed using the Trimmomatic program.

### 4. Run FastQC on trimmed data
**Rule: fastqc_trimmed**

The program FastQC is run on the trimmed read part files.

### 5. Map reads to the reference genome
**Rule: bwa_map**

BWA is used to map the trimmed reads to the reference genome. Read group 
information is parsed from the file names. 

### 6. Sort and index bam files
**Rule: sam_to_sorted_bam**

Bam files are coordinate-sorted and indexed using Picard SortSam.

### 7. Merge bam files by sample
**Rule: merge_bam**

Bam files generated from part of the trimmed fastq files are merged using 
Picard MergeSamFiles. Note that multiplexed samples are still separate.

### 8. Aggregate and deduplicate samples
**Rule: agg_and_dedup**

Picard MarkDuplicates is used to combine bam files from the same sample and 
mark suspected read duplicates. 

**NOTE: This step must be complete for all files before beginning the next steps**

### 9. Check for correct merge
**Rule: check_merge**

A custom script (bam_checker.py) ensures that the merged bam files contain the 
same number of reads as the contributing input files. 

### 10. Build bam index
**Rule: build_bai**

Create bam index for merged bam files with Picard BuildBamIndex.

### 11. Base Recalibration
**Rule: counts1_for_BQSR**

Generates a recalibration report for each bam file with GATK BaseRecalibrator.

**Rule: base_recal**

Performs recalibration with GATK PrintReads. 

**Rule: counts2_for_BQSR**

Generates a second report on the recalibrated bam files.

### 12. Statistics on bam files
**Rule: analyze_covariates**

Generates plots in R using pre- and post-recalibrated bam files, with GATK 
AnalyzeCovariates.

**Rule: bam_stats**

Calculates basic statistics on recalibrated files with samtools flagstat.

**Rule: depth_of_coverage**

Generates coverage statistics with GATK DepthOfCoverage.

## Variant Calling

### 13. Divide contigs for batch processing
**Rule: split_contigs_list**

Creates a set of files where in file contains the names of a number of contigs 
determined by the user in the config file. This allows contig analyses to be 
performed on a set of e.g. 100 contigs at a time, rather than running 
individual cluster jobs for each contig.

### 14. Run haplotype caller on contigs
**Rule: haplotype_caller_contigs**

Runs GATK Haplotype caller on the chunks of contigs defined in the previous 
step.

### 15. Merge GVCF files for contigs
**Rule: merge_gvcf_contigs**

Combines .g.vcf files for all contig chunks into a single .g.vcf file for each 
 sample with 
GATK CombineGVCFs.

### 16. Run haplotype caller on chromosomes
**Rule: haplotype_caller_chrs**

Runs GATK HaplotypeCaller on each chromosome.

### 17. Validate the .g.vcf file for chromsome 1
**Rule: validate_vcf**

Runs GATK ValidateVariants on the .g.vcf file for chromosome 1, as a spot check 
for correct vcf file generation.

### 18. Genotype chromosomes and contigs
**Rule: genotype_chrs**

**Rule: genotype_contigs**

Runs GATK GenotypeVCFs on the .g.vcf files for each chromosome and the combined 
contigs, per sample.

### 19. Extract SNPs from chromosomes and contigs
**Rule: extract_snps_chrs**

**Rule: extract_snps_contigs**

Extract SNPs for each chromosome and the contigs, per sample, using GATK 
SelectVariants.

### 20. Filter SNPs from chromosomes and contigs
**Rule: filter_snps_chrs**

**Rule: filter_snps_contigs**

Filter SNPs using GATK VariantFiltration.

### 21. Concatenate chromosome and contig SNP VCF files
**Rule: cat_snps**

Use the CatVariants classpath to combine the chromosome and contig SNP VCFs.

### 22. Extract indels from chromosomes and contigs
**Rule: extract_indels_chrs**

**Rule: extract_indels_contigs**

Extract indels for each chromosome and the contigs, per sample, using GATK 
SelectVariants.

### 23. Filter indels from chromosomes and contigs
**Rule: filter_indels_chrs**

**Rule: filter_indels_contigs**

Filter indels using GATK VariantFiltration.

### 24. Concatenate chromosome and contig indel VCF files
**Rule: cat_indels**

Use the CatVariants classpath to combine the chromosome and contig Indel VCFs.

