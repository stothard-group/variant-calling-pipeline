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

### Installing programs to run the workflow in an HPC environment

If the workflow is being used in a High Performance Computing environment such 
as Compute Canada, it is recommended that the following Docker containers are 
downloaded and made into Singularity image files. When running the workflow, 
you must also use the --use-singularity flag. 

 - [smoove](https://hub.docker.com/r/brentp/smoove/) as the image file `smoove.sif`
 - [cnvnator](https://hub.docker.com/r/chrishah/cnvnator-docker) as the image 
   file `cnvnator.sif` 
 - [samplot](https://hub.docker.com/r/dceoy/samplot) as the image file `samplot.sif`
   
To create these images using Singularity, run the following command:

`singularity build myimage.sif docker://docker_image`

The images should be stored in the working directory.

The program SnpSift is also required, and the path to the SnpSift.jar file must 
be specified in `config/svcalling.config.yaml`:

- [SnpSift >= 4.3t](https://pcingola.github.io/SnpEff/)
  
### Installing programs to run the workflow in other environments
The following programs and all of their dependencies must be in your path:

 - [smoove >= 0.2.5](https://github.com/brentp/smoove)
 - [samplot](https://github.com/ryanlayer/samplot)
 - [cnvnator](https://github.com/abyzovlab/CNVnator)

The path to the SnpSift.jar file must be specified in 
`config/svcalling.config.yaml`:

- [SnpSift >= 4.3t](https://pcingola.github.io/SnpEff/)

 
## Edit Config File

The file `config/sv_calling.config.yaml` controls all configurable options 
relating to the workflow itself. Note that if java is not in your path, you will 
 need to specify the path to the executable in this file.

For each rule within the snakemake file found in 
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

### HPC clusters
If you do not have a slurm profile, [set one up here](https://github.com/stothard-group/variant-calling-pipeline/blob/master/slurm_setup.md).

The workflow can be run with the following command:

```
snakemake --snakefile svcalling.sm --profile slurm --use-singularity \
--singularity-args "-B /paths/to/dirs/needed/by/programs/"
```

To run the workflow without a slurm profile, use:

```
snakemake --snakefile svcalling.sm --cluster "sbatch -N 1 -c {threads} \
--mem={resources.mem_mb} --time={resources.runtime} --account=account_name" \
--use-singularity --singularity-args "-B /paths/to/dirs/needed/by/programs/"
```

### Usage on other platforms
```
snakemake --snakefile svcalling.sm 
```
