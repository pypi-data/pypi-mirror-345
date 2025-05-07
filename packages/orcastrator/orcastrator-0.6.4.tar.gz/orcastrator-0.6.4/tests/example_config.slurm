#!/bin/bash
#SBATCH --job-name=example_config
#SBATCH --partition=normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1G
#SBATCH --time=12:00:00
#SBATCH --output=%x-%j.slurm.log
#SBATCH --error=%x-%j.slurm.err




echo "Job started at $(date)"
echo "Running on nodes: $SLURM_JOB_NODELIST"
echo "Using $SLURM_NTASKS tasks, $SLURM_CPUS_PER_TASK CPUs per task"

# Environment setup (adjust ORCA/OpenMPI paths if necessary)
# These defaults might not be suitable for all systems.
# Consider making these configurable in the TOML [slurm] section.
export ORCA_INSTALL_DIR="/soft/orca/orca_6_0_1_linux_x86-64_shared_openmpi416_avx2"
export OPENMPI_INSTALL_DIR="/soft/openmpi/openmpi-4.1.6"

export PATH="$ORCA_INSTALL_DIR:$OPENMPI_INSTALL_DIR/bin:$PATH"
export LD_LIBRARY_PATH="$ORCA_INSTALL_DIR/lib:$OPENMPI_INSTALL_DIR/lib:$LD_LIBRARY_PATH"
# For OpenMPI, ORCA often needs this to be set to the number of MPI tasks
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

echo "ORCA executable: $(which orca)"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
echo "OMP_NUM_THREADS: $OMP_NUM_THREADS"

# Run the orcastrator command
echo "Executing: orcastrator run /Users/freddy/Documents/Projects/orcastrator/tests/example_config.toml"
orcastrator run /Users/freddy/Documents/Projects/orcastrator/tests/example_config.toml

echo "Job finished at $(date)"
