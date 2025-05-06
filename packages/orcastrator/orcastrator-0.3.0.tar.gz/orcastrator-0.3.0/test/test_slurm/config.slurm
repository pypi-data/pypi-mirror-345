#!/bin/bash
#SBATCH --job-name=orcastrator_job
#SBATCH --time=24
#SBATCH --cpus-per-task=16
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=2GB

# Environment setup

# Execute the pipeline
uv run -v -m orcastrator.pipeline_runner /Users/freddy/Documents/Projects/orcastrator/test/test_slurm/config.toml
