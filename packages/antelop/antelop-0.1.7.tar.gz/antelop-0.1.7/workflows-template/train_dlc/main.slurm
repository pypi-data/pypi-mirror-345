#!/bin/bash

#SBATCH --job-name=train_dlc_master
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1

# add alternatives to path
export PATH=/usr/sbin:$PATH

# JAVA
JAVA=$(alternatives --display java | awk '/family java-17/ { print $1}')
JAVA_HOME=${JAVA%%/bin/java}
export PATH=${JAVA%%/java}:$PATH

# Nextflow
export PATH=<install_dir>/bin/nextflow:$PATH

# Nextflow cache
export NXF_HOME=<data_dir>/nfx_home

# print key to disk
echo "Key for this job: $1"

# run job
nextflow run <install_dir>/workflows/train_dlc/main.nf --key $1
