import sys
from pathlib import Path
from typing import List, Optional

import click

try:
    import toml  # type: ignore
except ModuleNotFoundError:
    import tomllib as toml

from orcastrator.pipelines import run_opt_freq_sp

# apollo
DEFAULT_ORCA_DIR = "/soft/orca/orca_6_0_1_linux_x86-64_shared_openmpi416_avx2"
DEFAULT_OPENMPI_DIR = "/soft/openmpi/openmpi-4.1.6"


@click.group()
def cli():
    """Orcastrator CLI - orchestrate ORCA calculations."""
    pass


@cli.command()
@click.argument(
    "config_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--slurm",
    is_flag=True,
    help="Generate a SLURM batch script instead of running the calculation",
)
@click.option(
    "--slurm-output",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output path for the SLURM script (default: config_file.slurm)",
)
def run(config_file: Path, slurm: bool, slurm_output: Optional[Path]):
    """Run a calculation pipeline defined in a TOML config file."""
    try:
        config = toml.loads(config_file.read_text())
        validate_config(config)

        parent_dir = config_file.parent / Path(config["general"]["output_dir"])
        scratch_base_dir = Path(
            config["general"].get("scratch_dir", parent_dir / "scratch")
        )
        cpus = config["general"].get("cpus", 1)
        mem_per_cpu_gb = config["general"].get("mem_per_cpu_gb", 1)
        overwrite = config["general"].get("overwrite", False)
        keep_scratch = config["general"].get("keep_scratch", False)

        # Extract calculation details
        charge = config["molecule"]["charge"]
        mult = config["molecule"]["multiplicity"]
        xyz_file = config_file.parent / Path(config["molecule"]["xyz_file"])

        # Extract keywords for each step
        keywords: List[List[str]] = []
        for step in ["optimization", "frequency", "single_point"]:
            if step in config:
                step_keywords = config[step].get("keywords", [])
                keywords.append(step_keywords)
            else:
                # If a step is missing, use the previous step's keywords
                if keywords:
                    keywords.append(keywords[-1])
                else:
                    raise ValueError(
                        f"Missing section for {step} and no previous keywords to use"
                    )

        if slurm:
            # Generate SLURM script instead of running the calculation
            slurm_output = slurm_output or config_file.with_suffix(".slurm")
            slurm_script = generate_slurm_script(config_file=config_file, config=config)
            slurm_output.write_text(slurm_script)
            click.echo(f"SLURM script generated at {slurm_output}")
        else:
            # Run the pipeline
            click.echo(f"Running opt-freq-sp pipeline with config from {config_file}")
            run_opt_freq_sp(
                parent_dir=parent_dir,
                charge=charge,
                mult=mult,
                xyz_file=xyz_file,
                keywords=keywords,
                cpus=cpus,
                mem_per_cpu_gb=mem_per_cpu_gb,
                scratch_base_dir=scratch_base_dir,
                overwrite=overwrite,
                keep_scratch=keep_scratch,
            )
            click.echo("Pipeline completed successfully")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


def generate_slurm_script(config_file: Path, config: dict) -> str:
    """Generate a SLURM batch script for the calculation."""
    # Extract SLURM settings or use defaults
    slurm_config = config.get("slurm", {})
    job_name = slurm_config.get("job_name", config_file.name)
    partition = slurm_config.get("partition", "normal")
    nodes = slurm_config.get("nodes", 1)
    ntasks = slurm_config.get("ntasks", 1)
    cpus = config["general"].get("cpus", 1)
    mem_per_cpu_gb = f"{config['general'].get('mem_per_cpu_gb', 1)}GB"
    time = f"{slurm_config.get('time_h', 24)}:00:00"

    # Additional SLURM options
    account = slurm_config.get("account", None)
    account_line = f"#SBATCH --account={account}" if account else ""

    email = slurm_config.get("email", None)
    email_line = f"#SBATCH --mail-user={email}" if email else ""
    email_type = slurm_config.get("email_type", "END,FAIL")
    email_type_line = f"#SBATCH --mail-type={email_type}" if email else ""

    # Create the SLURM script
    script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --partition={partition}
#SBATCH --nodes={nodes}
#SBATCH --ntasks={ntasks}
#SBATCH --cpus-per-task={cpus}
#SBATCH --mem-per-cpu={mem_per_cpu_gb}
#SBATCH --time={time}
{account_line}
{email_line}
{email_type_line}
#SBATCH --output=%x-%j.slurm_log
#SBATCH --error=%x-%j.slurm_log


# Set up environment
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export ORCA="{DEFAULT_ORCA_DIR}"
export OPENMPI="{DEFAULT_OPENMPI_DIR}"
export PATH="$ORCA:$OPENMPI/bin:$PATH"
export LD_LIBRARY_PATH="$ORCA/lib:$OPENMPI/lib64:$LD_LIBRARY_PATH"

# Run the orcastrator calculation
uvx orcastrator run {config_file.resolve()}

echo "Job finished at $(date)"
"""
    return script


def validate_config(config: dict) -> None:
    """Validate that the configuration has all required sections and fields."""
    # Check for required sections
    required_sections = ["general", "molecule"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required section '{section}' in config file")

    # Check general section
    required_general = ["output_dir"]
    for field in required_general:
        if field not in config["general"]:
            raise ValueError(f"Missing required field '{field}' in [general] section")

    # Check molecule section
    required_molecule = ["charge", "multiplicity", "xyz_file"]
    for field in required_molecule:
        if field not in config["molecule"]:
            raise ValueError(f"Missing required field '{field}' in [molecule] section")

    # At least one of the computational sections must be present
    if not any(
        step in config for step in ["optimization", "frequency", "single_point"]
    ):
        raise ValueError(
            "At least one of [optimization], [frequency], or [single_point] sections must be present"
        )


@cli.command()
def example_config():
    """Generate an example configuration file."""
    example = """
# Orcastrator Configuration File

[general]
output_dir = "calculations"     # Directory for calculation outputs
cpus = 1                        # Number of CPU cores
mem_per_cpu_gb = 1              # RAM per CPU core in GB
scratch_dir = "scratch"         # Scratch directory (optional)
overwrite = false               # Whether to overwrite existing calculations
keep_scratch = false            # Whether to keep scratch directories

[molecule]
charge = 0                      # Molecular charge
multiplicity = 1                # Spin multiplicity
xyz_file = "molecule.xyz"       # Path to input XYZ file

[optimization]
keywords = ["B3LYP", "def2-SVP", "D3BJ"]  # Keywords for optimization

[frequency]
keywords = ["B3LYP", "def2-SVP", "D3BJ"]  # Keywords for frequency calculation

[single_point]
keywords = ["B3LYP", "def2-TZVP", "D3BJ", "RIJCOSX"]  # Keywords for single point

# SLURM configuration for HPC jobs
[slurm]
# cpus_per_task are read from [general.cpus]
# mem_per_cpu is read from [general.mem_per_cpu_gb]
account = "project01234"       # (Optional) Accounting
job_name = "orcastrator"       # (Optional) Name of the SLURM job
time_h = 24                    # (Optional) Maximum wall time in hours
partition = "normal"           # (Optional) SLURM partition/queue to use
nodes = 1                      # (Optional) Number of nodes to request
ntasks = 1                     # (Optional) Number of tasks
account = "myaccount"          # (Optional) Account to charge
email = "user@example.com"     # (Optional) Email for notifications
email_type = "END,FAIL"        # (Optional) When to send emails
"""
    click.echo(example)


if __name__ == "__main__":
    cli()
