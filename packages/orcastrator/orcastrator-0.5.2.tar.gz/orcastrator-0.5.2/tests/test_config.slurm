#!/bin/bash
#SBATCH --job-name=test_config.toml
#SBATCH --partition=normal
#SBATCH --nodes=1
# ORCA uses 'ntasks' CPU cores and one core per task
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1GB
#SBATCH --time=24:00:00
#SBATCH --output=%x-%j.slurm_log
#SBATCH --error=%x-%j.slurm_log





# Set up environment
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export ORCA="/soft/orca/orca_6_0_1_linux_x86-64_shared_openmpi416_avx2"
export OPENMPI="/soft/openmpi/openmpi-4.1.6"
export PATH="$ORCA:$OPENMPI/bin:$PATH"
export LD_LIBRARY_PATH="$ORCA/lib:$OPENMPI/lib64:$LD_LIBRARY_PATH"

# Run the orcastrator calculation
uvx orcastrator run /Users/freddy/Documents/Projects/orcastrator/tests/test_config.toml

echo "Job finished at $(date)"
