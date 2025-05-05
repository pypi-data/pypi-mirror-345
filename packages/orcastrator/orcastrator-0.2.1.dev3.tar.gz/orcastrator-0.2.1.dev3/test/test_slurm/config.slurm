#!/bin/bash
#SBATCH --job-name=orcastrator_job
#SBATCH --time=24
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --partition=normal
#SBATCH --mem-per-cpu=2GB

# Environment setup

# Execute the pipeline
uv run -v \
    /Users/freddy/Documents/Projects/orcastrator/test/test_slurm/test_pipeline.py \
    /Users/freddy/Documents/Projects/orcastrator/test/test_slurm/config.toml