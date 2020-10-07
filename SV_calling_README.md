# Structural Variant Calling Workflow

This pipeline uses the read mapping files produced by the 
[Read Mapping and Variant Calling pipeline](README.md) to detect structural 
variants, and produces image files of each SV region. It is designed to work on 
Compute Canada clusters.

**SECTIONS**

[Setup](#setup)

[Edit Config File](#edit-config-file)

[Running the Structural Variant Calling workflow](#running-the-SV-calling-workflow)


## Setup

Requirements:
- Python 2.7 (CNVnator requires Python 2)
- Python 3.7+ (This workflow was developed and tested with Python v. 3.7)
- Java SE Development Kit 8, Update 121 (1.8.0_121)+

## Required programs to run the workflow

These programs must be in your path or specified in the file `config/sv_calling.config.yaml`:

 - [smoove >= 0.2.5](https://github.com/brentp/smoove)
 - [SnpSift >= 4.3t](https://pcingola.github.io/SnpEff/) (The path to SnpSift.jar must be specified in the `config/sv_calling.config.yaml`
 configuration file)
 - [samplot](https://github.com/ryanlayer/samplot)

All other programs called by the workflow are loaded as software modules.

 
## Edit Config File

The file `config/sv_calling.config.yaml` controls all configurable options 
relating to the workflow itself. For each rule within the snakemake file found in 
`workflow/svcalling.sm`, there are thread and resource specifications which can be 
edited according to your setup. 

All rules in the workflow are designed to run on a single node of a cluster 
with up to 16Gb RAM, with the exception of the local rules listed at the top of 
the `workflow/svcalling.sm` file. 

Cluster configuration values are listed for each rule and specify the 
following slurm options:
- threads: 1 # Number of threads to use for each job; should be equal to or less than cores
- resources:
	- cores = 1,  # Number of cpus available, or that will be requested from the scheduler
	- runtime = 120,  # Requested walltime in minutes
	- mem_mb = 4000,  # Requested memory in MB

#### Add user-specific files to the reference_files directory

The following files must be added to the `resources/reference_files` directory.
File names should be specified in `config/svcalling.config.yaml`:

- reference genome in Fasta format
- fai index file
- GFF file containing gene feature information for smoove annotation

## Running the SV calling workflow

### Input files

The workflow expects read mapping (*.bam) files in the directory 
`results/alignment/`. These are created in the process of variant calling using 
the main Variant Calling snakemake workflow. The SV calling workflow can be run 
on any alignment files without running the main workflow, as long as they are 
found in the `results/alignment/` directory. 
 
### Output files

Output files will be generated within subdirectories of `results`. The final 
*.png image files will be found in `results/smoove/{sample name}/plots/` and 
`results/cnvnator/{sample name}/plots/`. For more information on the SV calling 
workflow, see the [SV Calling Workflow](#fill-in)

### Parameters

In the configuration file `config/svcalling.config.yaml`, the option `partition` 
controls the size of partitions used for CNVnator. From the [CNVnator paper by 
Abyzov _et al._](https://genome.cshlp.org/content/21/6/974)

> For the calculation of the RD signal, CNVnator divides the whole genome into 
nonoverlapping bins of equal size and uses the count of mapped reads within 
each bin as the RD signal. It then partitions the generated signal into 
segments with presumably different underlying CNs. Putative CNVs are predicted 
by applying statistical significance tests to the segments. 

Thus, the partition value allows the user to detect CNVs in various sizes. Note 
that decreasing the partition size will likely require an increase in requested 
runtime and memory for the rule `cnvnator`.

For information on parameters used for filtering, see the 
[SV Calling Workflow](https://github.com/stothard-group/variant-calling-pipeline/blob/master/SV_calling_workflow.md).

## Running the SV calling workflow

If you do not have a slurm profile, [set one up here](https://github.com/stothard-group/variant-calling-pipeline/blob/master/slurm_setup.md).

The workflow can now be run with the following command:

```
snakemake --snakefile svcalling.sm --profile slurm
```
