# Read Mapping and Variant Calling Pipeline

#### According to the specifications of the 1000 Bulls Genome Project, Run 8 Revision 20191101

For details, see 
[1000bullsGATK3.8pipelineSpecifications_Run8_Revision_20191101](1000bullsGATK3.8pipelineSpecifications_Run8_Revision_20191101.docx)

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
- Python 3 (This workflow was developed and tested with Python v. 3.7)
- R (This workflow was developed and tested with R v. 3.6.1)
- Java SE Development Kit 8, Update 192 (1.8.0_192)


#### Compute Canada Setup

1. Load Python
	
	`module load python/3.7`
	
2. Install the following python modules:

	`pip install pandas pysam --user`

3. Install the following R libraries:
	
	```
	module load r/3.6.1
	R	
	```
	In the R console, look for **caTools**, **ggplot2**, and **gplots** using 
	`installed.packages()`. If these libraries are not included in the list, 
	install them:
	```
	install.packages(c('caTools','ggplot2','gplots'))
	q()
	```
	Be sure to save changes to the workspace upon exiting R.

## Edit Config Files

Two files control all configurable options in this workflow:
`variant_calling.config.yaml` and `variant_calling.clusterconfig.yaml`. Edit 
these files according to your setup. 

All rules in the workflow are designed to run on a single node of a cluster 
with up to 30 CPUs 
and 100Gb RAM, with the exception of the local rules listed at the top of the 
VariantCalling.sm file. 

Values in the clusterconfig.yaml file are listed for each rule and specify the 
following slurm options:
- n: cpus-per-task (-c)
- time: time, format 0-00:00:00 (--time)
- pmem: total memory, all values in mb (--mem)

#### Add user-specific files to the reference_files directory
The latest reference files should be used. For *Bos taurus* 
ARS-UCD1.2_Btau5.0.1Y, these can be found at [1000bullgenomes.com](http://www.1000bullgenomes.com/).

For any other genome, add the following files to the `reference_files` 
directory specified in the config file:
- reference genome in Fasta format
- fai index file
- BWA index files (.amb, .ann, .bwt, .pac, .sa)
- Picard sequence dictionary file (.dict)
- file containing a list of all chromosome and contig names in the reference 
genome, with the filename {reference_genome}.fa.NAMES

## Running the Variant Calling workflow

There are two parts that make up the Variant Calling workflow. The steps that 
are completed when running the workflow are controlled by commenting or 
uncommenting the inputs within `rule final`. Because it is imperative that all 
bam files have been merged properly before this second step, the subsequent 
inputs are initially commented out. Once this workflow has been run until the 
midway completion point (no new jobs are created), uncomment the second set of 
steps. If for some reason the bam merge step was unsuccessful, the workflow 
will hang and the file {sample_name}_incorrect.txt will be created in the 
{output_dir}/alignment/ directory.

#### Note on sequence filenames
This workflow was designed for sequence files named as follows:

`HI.{1}.{2}.NEBNext_Index_{3}.{4}_R[1,2].fastq.gz`

1. Four digit Sequencer ID 
2. Three digit Flowcell ID
3. Barcode
4. Sample ID

Pipeline modification is required to support filenames that deviate from this 
convention.

#### Command line options

Once the appropriate changes are made to the config files and workflow file, 
VariantCalling.sm, execute the workflow using the following command:

```
snakemake --snakefile VariantCalling.sm \
--cluster-config VariantCalling.clusterconfig.yaml \
--cluster "sbatch -N 1 -c {cluster.n} --mem={cluster.pmem} \
--time={cluster.time} --account={rrg-stothard-ac}" --rerun-incomplete \
--printshellcmds -j 10
```

The `-j 10` option will run up to 10 jobs at a time. Add the option --dry-run 
to check that the workflow is setup properly prior to executing jobs. 

If the workflow is unexpectedly interrupted (e.g. by logging out of the 
cluster), remove the hidden snakemake directory before starting a new run with 
`rm -r .snakemake`. 
