# Artifact: Reshaping High Energy Physics Applications for Near-Interactive Execution Using TaskVine

## Description

This repository contains the scripts that generated the figures used within the paper in addition to scripts used to replicate 
experiments from the paper. There are two directories. First, the `paper_figures/` directory includes original logs used to generate 
the figures along with the scripts to generate them. Within each directory named `figure_X_FIGURE_NAME/` exists `logs/` and `graphs` directories,
containing the logs and the graphs generated respectively. Within each directory, exists at least one script named `plot*.py`. Running `python plot*.py`
generates the respective graph and writes the graph to the `graphs/` directory. In addition, there are extra graphs not used in the paper that are included in the `graphs` directory.
The second directory is named `experiments`. This directory contains scaled down experiments of the applications ran within the paper. 
In this directory, there are two main experiments. `DV3/` and `RS-TriPhoton/`. Detail on running these experiments is provided below:

## Executing Experiments

### Setting Up the Environment

The environments used to execute these applications are conda environments where instructions for installation can be found here: 
https://conda.io/projects/conda/en/latest/user-guide/install/index.html

Once Conda is installed the environment for the respective experiment can be created via the `env.yml` file located in each experiment's directory.
Within each experiment directory, execute the following command:

```
conda env create --name <ENVIRONMENT_NAME> --file=env.yml
```

This installs the environment needed to execute the environment, version numbers are shown within the YAML file:

Once installed, activate the environment with the following command:

```
conda activate <ENVIRONMENT_NAME>
```

To ensure distribution of the environment across workers within a cluster, we package the environment within a tarball using the following command:

```
poncho_package_create $CONDA_PREFIX <dv3-env|rstri-env>.tar.gz
```

This tarball is distributed along with worker binaries to ensure environments are available on remote execution sites.


### Running the Experiments

Within each experiment directory exists a `run.sh` script which will execute the experiments needed to generate the example logs. Executed like so:

```
./run.sh
```

After completion, logs for each run can be found within the directory `experiments/logs`

### Processing the Results

After completion of both experiments, the logs can be processed to generate graphs similar to those shown in the paper. This can be done like so for each plotting script:
 
```
python plotting_tools/plot_fig_X.py
```

A graph will then be generated within the `graphs/` directory.
More details on expected results and expected runtimes can be found within the pdf AD_SC24.pdf








