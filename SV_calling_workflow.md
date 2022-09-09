# Structural Variant Calling Workflow Overview

This document outlines the steps performed by the snakemake workflow
`svcalling.sm`. The input files are read alignment .bam files found in the 
directory `results/alignment/`. They can be produced separately, or as part of 
the Variant Calling snakemake workflow. This workflow uses 
[smoove](https://github.com/brentp/smoove), [Pindel](https://gmt.genome.wustl.edu/packages/pindel/), and [Manta](https://github.com/Illumina/manta) as the main SV calling tools. There are also auxiliary rules that run other SV calling programs, such as [CNVnator](https://github.com/abyzovlab/CNVnator), [Breakdancer](https://github.com/genome/breakdancer), [Delly](https://github.com/dellytools/delly), and [GridSS](https://github.com/PapenfussLab/gridss). The output file is `SV.vcf.gz`, containing Pindel and Manta insertions and deletions.

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

### 7. Generate config file for Breakdancer

**Rule breakdancer_cfg**

Creates tab delimited file required by Breakdancer using the tool's bam2cfg.pl script.

### 8. Generate config file for Pindel

**Rule pindel_config**

Uses the Breakdancer config file generated in step 7 to write file name, mean insert size, and sample name information to a text file for Pindel.

### 9. Run Pindel

**Rule pindel**

Run pindel on all samples in config file.

### 10. Filter pindel results

**Rule pindel_filter**

Uses statistics information generated in the Variant Calling workflow to calculate average coverage. If the Variant Calling workflow was not run, then a stats file must be provided with the name {sample}.bam.depth.sample_summary, after running GATK DepthOfCoverage. See the Variant Calling Workflow rule depth_of_coverage for more information. Average coverage and chromosome length information is used to filter SVs from Pindel.

### 11. Merge pindel types

**Rule merge_pindel_types**

Picard MergeVCFs is used to merge files with different types of SVs from Pindel.

### 12. Merge Pindel results across chromosomes

**Rule pindel_merge**

Use bcftools concat to concatenate pindel results from different chromosomes.

### 13. Compress chromosome statistics file for Manta

**Rule bgzip_chromstats**

Compress a given bed file containing chromosome positions for all chromosomes to be analyzed. 

### 14. Prepare Manta config file

**Rule manta_config**

Generate Manta PyFlow with the configManta.py script. 

### 15. Run Manta

**Rule manta**

Run Manta via PyFlow.

### 16. Extract deletions from Manta and Pindel

**Rule split_manta**

Use bcftools to extract deletion (DEL) and insertion (INS) SVs from Manta output.

**Rule msample_split**

Split Manta insertions into separate files by sample.

**Rule split_pindel**

Use bcftools to extract insertion (INS) SVs from pindel output.

**Rule psample_split**

Split Pindel insertions into separate files by sample.

### 17. Combine Manta and Pindel insertions

The program [SURVIVOR](https://github.com/fritzsedlazeck/SURVIVOR) is used to merge Manta and Pindel insertions. A maximum allowed distance of 1000bp is used. Calls can be supported by either program, but must be of the same type and at least 30bp long.

### 18. Concatenate insertion results across samples

**Rule sur_merge**

Use bcftools to merge the output of SURVIVOR across samples.

### 19. Merge insertions and deletions

**Rule final_merge**

Use bcftools to merge the merged insertion SVs and Manta deletion SVs.

## Auxiliary rules


### 20. Run CNVnator

**Rule cnvnator**

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
 
### 21. Export CNV calls to VCF file

**Rule cnvnator_to_vcf**

CNV calls are exported as VCFs using the script `cnvnator2VCF.pl`.

### 22. Filter CNVnator VCF file

**Rule cnvnator_filter**

SnpSift is used to filter the CNVnator results using the following criteria:
 - e-val1 < 0.05
 - eval-2 < 0.05
 - q0 < 0.5
 
### 23. Run Breakdancer

**Rule breakdancer**

Run Breakdancer on samples using config file. 

### 24. Generate vcf files

**Rule breakdancer2vcf**

Use the breakdancer2vcf utility to generate VCF files from Breakdancer output.

### 25. Process reference for GRIDSS

**Rule gridss_reference**

Use GridSS setupreference to process the reference genome.

### 26. Preprocess sample bam files

**Rule gridss_preprocess**

Create assembly using reference and samples.

### 27. Variant calling with GridSS

**Rule gridss_call**

Call variants with GridSS.

### 28. Call variants with Delly

**Rule delly_call_1**

Perform per-sample SV calling with Delly.

### 29. Merge Delly calls

**Rule delly_merge**

Create a joint call file with Delly merge.

### 30. Re-call SVs from merged file

**Rule delly_call_2**

Perform SV called on the merged Delly file with all samples. 

### 31. Genotype second Delly calls

**Rule delly_joint**

Use bcftools to create a joint genotyped file of Delly SVs.

### 32. Filter Delly calls

**Rule delly_filter**

Filter SV calls using Delly.

**Rule bcf_to_vcf**

Convert filtered Delly call file to VCF format.

### Plot Smoove and CNVNator SVs

**Rule smoove_plot**

**Rule cnvnator_plot**

Use [Samplot](https://github.com/ryanlayer/samplot) to plot the images of SVs predicted by Smoove and CNVNator.
