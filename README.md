# Read Mapping and Variant Calling Pipeline

#### According to the specifications of the 1000 Bulls Genome Project, Run 8 Revision 20191101

For details, see 
[1000bullsGATK3.8pipelineSpecifications_Run8_Revision_20191101](1000bullsGATK3.8pipelineSpecifications_Run8_Revision_20191101.docx)

For the related SV calling workflow, see [the SV calling README document](SV_calling_README.md)

**SECTIONS**

[Installation](#installation)

[Setup](#setup)

[Edit Config Files](#edit-config-files)

[Running the Variant Calling workflow](#running-the-variant-calling-workflow)


## Installation

Download the repository and un-tar the software directory:

```
git clone https://github.com/stothard-group/variant_calling_pipeline.git

tar -xzvf software_variant_calling.tar.gz
```

## Setup

Requirements:
- Python 3.7+ (This workflow was developed and tested with Python v. 3.7)
- setuptools
- cython
- gcc 7.3

Install the following python modules using pip:
- pysam>=0.15.4
- pandas>=0.24.1
- numpy>=1.12.0

Or run the setup.py script to install the required modules:

`python setup.py install`


## Required programs to run the workflow

The following must be in your path:

- R (This workflow was developed and tested with R v. 3.6.1)
- Java SE Development Kit 8, Update 192 (1.8.0_192)

These programs must either be in your path, or must be specified in 
the file `config/variant_calling.config.yaml`:

- BWA 0.7.17
- FastQC >= 0.11.7
- Trimmomatic ~=0.36
- samtools >= 1.8
- picard == 2.18
- GenomeAnalysisTK == 3.8-1-0-gf15c1c3ef

Note: This specific version of GATK is required by the 1000 Bulls Run 8 
specifications. Other minor versions of GATK v.3 may be compatible, but 
GATK v.4 is incompatible with this workflow. 

The following R libraries are required:

- caTools
- ggplot2
- gplots
- gsalib
- reshape

These can be installed in the R shell with 

`install.packages(c('caTools','ggplot2','gplots','gsalib','reshape'))`


## Edit Configuration

The file `config/variant_calling.config.yaml` controls all configurable options 
relating to the workflow itself. For each rule within the snakemake file found in 
`workflow/snakemake`, there are thread and resource specifications which can be 
edited according to your setup. 

All rules in the workflow are designed to run on a single node of a cluster 
with up to 30 CPUs 
and 100Gb RAM, with the exception of the local rules listed at the top of the 
`workflow/snakemake` file. 

Cluster configuration values are listed for each rule and specify the 
following slurm options:
- threads: 1 # Number of threads to use for each job; should be equal to or less than cores
- resources:
	- cores = 1,  # Number of cpus available, or that will be requested from the scheduler
	- runtime = 120,  # Requested walltime in minutes
	- mem_mb = 4000,  # Requested memory in MB

#### Add user-specific files to the reference_files directory

The following files must be added to the `resources/reference_files` directory.
File names should be specified in `variant_calling.config.yaml`:

- reference genome in Fasta format
- fai index file
- BWA index files (.amb, .ann, .bwt, .pac, .sa)
- Picard sequence dictionary file (.dict) **
- file containing a list of all contig names in the reference 
genome, one item per line
- vcf file containing known variants for base quality score recalibration

For *Bos taurus* ARS-UCD1.2_Btau5.0.1Y, some of these files can downloaded from 
[1000bullgenomes.com](http://www.1000bullgenomes.com/).

\** The *.dict file can be generated using Picard. Navigate to the 
`resources/reference_files/` directory and run:

```
 java -jar picard.jar CreateSequenceDictionary \ 
      R=reference.fasta \ 
      O=reference.dict
```


## Running the Variant Calling workflow

### Input files

The workflow expects paired-end fastq files as inputs, within a directory 
in `variant_calling`. The relative path to this directory should be specified 
in the `variant_calling.config.yaml` file.


#### Note on sequence filenames
This workflow was designed for sequence files named as follows:

`HI.{1}.{2}.NEBNext_Index_{3}.{4}_R[1,2].fastq.gz`

1. Four digit Sequencer ID 
2. Three digit Flowcell ID
3. Barcode
4. Sample ID

Pipeline modification is required to support filenames that deviate from this 
convention.

### Output files

Output files will be generated within subdirectories of `results`. The final 
VCF files will be generated in `results/snps_indels/`. For more information on 
the contents of other output directories, see the [Workflow Readme](https://github.com/stothard-group/variant-calling-pipeline/blob/master/VariantCallingWorkflow.md).

#### Command line options

Resource allocations are given within each rule, and it is strongly 
recommended that users create or use a snakemake profile to run the workflow.

For example, if you have a [slurm profile](https://github.com/Snakemake-Profiles/slurm), 
you can run snakemake with the following command:
```
snakemake --profile slurm
```

[This guide](https://github.com/stothard-group/variant-calling-pipeline/blob/master/slurm_setup.md) 
can be used to set up a slurm profile. Other profiles can be found [here](https://github.com/snakemake-profiles/doc)