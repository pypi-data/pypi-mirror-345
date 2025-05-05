# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import argparse
from pathlib import Path
import subprocess
from orcastrator import SlurmBatchGenerator, create_slurm_script_from_toml

def cli():
    parser = argparse.ArgumentParser(description="Generate SLURM scripts for computational jobs")
    parser.add_argument("config", help="Path to TOML configuration file")
    parser.add_argument("--output", help="Output path for SLURM script")
    parser.add_argument("--pipeline", default="pipeline.py",
                       help="Pipeline script to run (default: pipeline.py)")
    parser.add_argument("--submit", action="store_true", help="Automatically submit the created slurm file to the queue")
    args = parser.parse_args()

    # Generate SLURM script
    output_path = args.output if args.output else Path(args.config).with_suffix(".slurm")

    try:
        script_path = create_slurm_script_from_toml(
            toml_path=args.config,
            pipeline_script=args.pipeline,
            output_path=output_path
        )
        print(f"Successfully created SLURM script: {script_path}")

        # Optionally, submit the job right away
        # subprocess.run(["sbatch", script_path])

    except Exception as e:
        print(f"Error creating SLURM script: {e}")
        return 1

    if args.submit:
        subprocess.run(["bash", script_path.resolve()])

    return 0

if __name__ == "__main__":
    exit(cli())

