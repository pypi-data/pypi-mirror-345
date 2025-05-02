#!/bin/bash

logdir=<data_dir>/logs
mkdir -p $logdir/$2
cd $logdir/$2

sbatch --export=$4 -t $5 --parsable <install_dir>/workflows/$3/main.slurm $1
