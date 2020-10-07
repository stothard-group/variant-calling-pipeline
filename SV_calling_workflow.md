# Structural Variant Calling Workflow Overview

This document outlines the steps performed by the snakemake workflow
`svcalling.sm`. The input files are read alignment .bam files found in the 
directory `results/alignment/`. They can be produced separately, or as part of 
the Variant Calling snakemake workflow. This workflow uses 
[smoove](https://github.com/brentp/smoove) and 
[CNVnator](https://github.com/abyzovlab/CNVnator) to predict structural 
variants and copy number variants, respectively. The output files are .png 
files produced by [samplot](https://github.com/ryanlayer/samplot), which 
visualize the region surrounding each variant.

## Smoove Structural Variant Calling

### 0. Create .bai/.fai files if not present

**Rule: make_fai, make_bai**

If the index files for the reference genome fasta file or the {sample}.bam 
read alignment files do not exist, use samtools to generate them.

### 1. Call genotypes with Smoove

**Rule: smoove_call**

Call genotypes in each sample. 

### 2. Merge genotype calls

**Rule: smoove_merge**

Get the union of all sites across all samples as a single VCF file.

### 3. Genotyping

**Rule: smoove_genotype**

Genotype each sample at all sites in the merged file, and use the program 
[duphold](https://github.com/brentp/duphold) to add depth annotations.

### 4. Create a joint-called file

**Rule: smoove_paste**

Paste all single-sample VCFs with the same number of variants to get a single, 
squared, joint-called file.

### 5. Annotate

**Rule: smoove_annotate**

Annotate the variants with exons and UTRs that overlap from a GFF, and annotate 
high-quality heterozygotes. This is done using the file listed for 
`annotation_gff` in `config/svcalling.config.yaml`.

### 6. Filter variants

**Rule: smoove_filter**

Use SnpSift to filter the variants using the following criteria:
 - MSHQ > 3 for all SV types
 - DHFFC < 0.7 for deletions
 - DHFFC > 1.25 for duplications

Briefly, the `smoove annotate` function adds an SHQ (Smoove Het Quality) tag to 
every sample format. These values range from 1 to 4, where 1 is low quality and 
4 is high quality. A value of -1 is non-het. The MSHQ, or mean SHQ is a score 
added to the INFO field; the average SHQ for all heterozygous samples for that 
variant. The filtering thresholds used here are suggested on the 
[Smoove](https://github.com/brentp/smoove) project GitHub.

### 7. Plot Smoove results

**Rule: smoove_plot**

[Samplot](https://github.com/ryanlayer/samplot) is used to create image files 
for the region surrounding each SV, for each sample.

## CNVnator Copy Number Variant Detection

### 8. Run CNVnator

**Rule: cnvnator**

Because CNVnator relies on the ROOT data analysis framework, all CNVnator steps 
are contained in a single rule. These steps are:

 - Extract read mapping information from the *.bam alignment file
 - Generate a read depth histogram using the user-input partition value as the 
 bin size
 - Calculate statistics based on the histograms
 - Read density signal partitioning 
 - CNV calling and output of calls as *.txt file
 
The structure of the CNV calls output file,
 `results/cnvnator/{sample}.cnvnator.txt`, can be found on the 
 [CNVnator website](https://github.com/abyzovlab/CNVnator).
 
### 9. Export CNV calls to VCF file

**Rule: cnvnator_to_vcf**

CNV calls are exported as VCFs using the script `cnvnator2VCF.pl`.

### 10. Filter CNVnator VCF file

**Rule: cnvnator_filter**

SnpSift is used to filter the CNVnator results using the following criteria:
 - e-val1 < 0.05
 - eval-2 < 0.05
 - q0 < 0.5
 
### 11. Plot CNVs

**Rule: cnvnator_plot**

Use Samplot to plot the region surrounding each filtered CNV.

 


