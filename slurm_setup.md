# SLURM Scheduler Profile Setup for Snakemake

This guide will help you to set up a slurm profile for running the 
svcalling.sm workflow. It is based on 
[this post](http://bluegenes.github.io/Using-Snakemake_Profiles/) by Tessa Pierce.

#### 1. Install `cookiecutter`

`pip install cookiecutter`

#### 2. Create a .config directory and add the slurm profile

```
mkdir -p ~/.config/snakemake
cd ~/.config/snakemake
cookiecutter https://github.com/Snakemake-Profiles/slurm.git
```

#### 3. Edit the config.yaml file to your preferred slurm options
```
vi ~/.config/snakemake/slurm/config.yaml
```

You can add or change options here; some that may be useful to add are:

 - jobs: 10
 - keep-going: True
 - rerun-incomplete: True
 - printshellcmds: True
 
#### 4. Set a default resource configuration

```
vi ~/.config/snakemake/slurm/cluster_config.yml
```

Add the following to this file:

```
__default__:
    account: your_acct_name # your hpc account
    time: 360 # default time (minutes)
    nodes: 1
    ntasks: 1
    mem: 4000m # default memory
```

All default values will be applied by snakemake, unless overwritten by the 
workflow.

#### 5. Edit the `CLUSTER_CONFIG` variable in `slurm-submit.py`

```
vi ~/.config/snakemake/slurm/slurm-subit.py
CLUSTER_CONFIG = "~/.config/snakemake/slurm/cluster_config.yml"
```

The svcalling.sm workflow can now be run with 
`snakemake --snakefile svcalling.sm --profile slurm`