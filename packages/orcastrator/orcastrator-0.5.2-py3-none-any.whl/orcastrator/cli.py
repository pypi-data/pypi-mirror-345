import logging
import sys
from pathlib import Path
from typing import List, Optional

import click

try:
    import toml  # type: ignore
except ModuleNotFoundError:
    import tomllib as toml

from orcastrator.logger import logger, setup_logger
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
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity (can be used multiple times for more detail)",
)
def run(config_file: Path, slurm: bool, slurm_output: Optional[Path], verbose: int):
    """Run a calculation pipeline defined in a TOML config file."""
    # Set up the logger
    log_file = config_file.with_suffix(".log")

    # Determine console log level based on verbosity
    console_level = logging.WARNING
    if verbose == 1:
        console_level = logging.INFO
    elif verbose >= 2:
        console_level = logging.DEBUG

    # Configure logger
    setup_logger(log_file=log_file, level=logging.DEBUG, console_level=console_level)

    logger.info(f"Starting Orcastrator run with config file: {config_file}")
    logger.debug(f"Log file location: {log_file}")

    try:
        logger.debug("Loading configuration file")
        config = toml.loads(config_file.read_text())
        logger.debug("Validating configuration")
        validate_config(config)

        parent_dir = config_file.parent / Path(config["general"]["output_dir"])
        scratch_base_dir = Path(
            config["general"].get("scratch_dir", parent_dir / "scratch")
        )
        cpus = config["general"].get("cpus", 1)
        mem_per_cpu_gb = config["general"].get("mem_per_cpu_gb", 1)
        overwrite = config["general"].get("overwrite", False)
        keep_scratch = config["general"].get("keep_scratch", False)

        logger.info(f"Output directory: {parent_dir}")
        logger.info(f"Scratch directory: {scratch_base_dir}")
        logger.info(f"Using {cpus} CPU(s) with {mem_per_cpu_gb}GB per CPU")
        logger.debug(f"Overwrite existing: {overwrite}")
        logger.debug(f"Keep scratch: {keep_scratch}")

        # Extract keywords for each step
        keywords: List[List[str]] = []
        for step in ["optimization", "frequency", "single_point"]:
            if step in config:
                step_keywords = config[step].get("keywords", [])
                keywords.append(step_keywords)
                logger.debug(f"{step.capitalize()} keywords: {step_keywords}")
            else:
                # If a step is missing, use the previous step's keywords
                if keywords:
                    keywords.append(keywords[-1])
                    logger.debug(
                        f"{step.capitalize()} step not defined, using previous keywords"
                    )
                else:
                    logger.error(
                        f"Missing section for {step} and no previous keywords to use"
                    )
                    raise ValueError(
                        f"Missing section for {step} and no previous keywords to use"
                    )

        if slurm:
            # Generate SLURM script instead of running the calculation
            slurm_output = slurm_output or config_file.with_suffix(".slurm")
            logger.info(f"Generating SLURM script at {slurm_output}")
            slurm_script = generate_slurm_script(config_file=config_file, config=config)
            slurm_output.write_text(slurm_script)
            logger.info("SLURM script generated successfully")
            click.echo(f"SLURM script generated at {slurm_output}")
        else:
            # Handle multiple molecules if present, otherwise fall back to single molecule
            if "molecules" in config:
                logger.info(f"Found {len(config['molecules'])} molecules to process")
                for idx, molecule in enumerate(config["molecules"], 1):
                    logger.info(
                        f"Processing molecule {idx}/{len(config['molecules'])}: {molecule['name']}"
                    )
                    molecule_dir = parent_dir / molecule["name"]
                    molecule_dir.mkdir(parents=True, exist_ok=True)

                    process_molecule(
                        molecule=molecule,
                        molecule_dir=molecule_dir,
                        keywords=keywords,
                        cpus=cpus,
                        mem_per_cpu_gb=mem_per_cpu_gb,
                        scratch_base_dir=scratch_base_dir,
                        overwrite=overwrite,
                        keep_scratch=keep_scratch,
                        config_file_parent=config_file.parent,
                    )
                logger.info("All molecules processed successfully")
            else:
                # Single molecule approach (existing behavior)
                process_single_molecule(
                    config=config,
                    parent_dir=parent_dir,
                    keywords=keywords,
                    cpus=cpus,
                    mem_per_cpu_gb=mem_per_cpu_gb,
                    scratch_base_dir=scratch_base_dir,
                    overwrite=overwrite,
                    keep_scratch=keep_scratch,
                    config_file_parent=config_file.parent,
                )

            click.echo("Pipeline completed successfully")

    except Exception as e:
        logger.exception(f"Error during execution: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        click.echo(f"See log file for details: {log_file}", err=True)
        sys.exit(1)


def process_molecule(
    molecule: dict,
    molecule_dir: Path,
    keywords: List[List[str]],
    cpus: int,
    mem_per_cpu_gb: int,
    scratch_base_dir: Path,
    overwrite: bool,
    keep_scratch: bool,
    config_file_parent: Path,
):
    """Process a single molecule from the molecules array."""
    logger.info(f"Processing molecule: {molecule['name']}")

    # Extract molecule details
    charge = molecule["charge"]
    mult = molecule["mult"]
    xyz_file = config_file_parent / Path(molecule["xyz_file"])

    logger.info(f"Molecule: {molecule['name']}, charge={charge}, mult={mult}")
    logger.info(f"Reading geometry from: {xyz_file}")

    # Create molecule-specific scratch directory
    molecule_scratch_dir = scratch_base_dir / molecule["name"]

    # Run the pipeline
    logger.info(f"Running opt-freq-sp pipeline for {molecule['name']}")
    run_opt_freq_sp(
        parent_dir=molecule_dir,
        charge=charge,
        mult=mult,
        xyz_file=xyz_file,
        keywords=keywords,
        cpus=cpus,
        mem_per_cpu_gb=mem_per_cpu_gb,
        scratch_base_dir=molecule_scratch_dir,
        overwrite=overwrite,
        keep_scratch=keep_scratch,
    )
    logger.info(f"Pipeline for {molecule['name']} completed successfully")


def process_single_molecule(
    config: dict,
    parent_dir: Path,
    keywords: List[List[str]],
    cpus: int,
    mem_per_cpu_gb: int,
    scratch_base_dir: Path,
    overwrite: bool,
    keep_scratch: bool,
    config_file_parent: Path,
):
    """Process a single molecule from the molecule section."""
    # Extract calculation details
    charge = config["molecule"]["charge"]
    mult = config["molecule"]["mult"]
    xyz_file = config_file_parent / Path(config["molecule"]["xyz_file"])

    logger.info(f"Molecule: charge={charge}, mult={mult}")
    logger.info(f"Reading geometry from: {xyz_file}")

    # Run the pipeline
    logger.info("Running opt-freq-sp pipeline")
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
    logger.info("Pipeline completed successfully")


def validate_config(config: dict) -> None:
    """Validate that the configuration has all required sections and fields."""
    logger.debug("Validating configuration file")

    # Check for required general section
    if "general" not in config:
        logger.error("Missing required section 'general' in config file")
        raise ValueError("Missing required section 'general' in config file")

    # Check general section
    required_general = ["output_dir"]
    for field in required_general:
        if field not in config["general"]:
            logger.error(f"Missing required field '{field}' in [general] section")
            raise ValueError(f"Missing required field '{field}' in [general] section")

    # Check for either single molecule or multiple molecules
    if "molecule" not in config and "molecules" not in config:
        logger.error("Missing both 'molecule' and 'molecules' sections in config file")
        raise ValueError(
            "Either a 'molecule' section or 'molecules' array must be present"
        )

    # Validate single molecule if present
    if "molecule" in config:
        validate_molecule_section(config["molecule"])

    # Validate multiple molecules if present
    if "molecules" in config:
        if not isinstance(config["molecules"], list):
            logger.error("The 'molecules' entry must be an array of molecule objects")
            raise ValueError(
                "The 'molecules' entry must be an array of molecule objects"
            )

        if not config["molecules"]:
            logger.error("The 'molecules' array is empty")
            raise ValueError("The 'molecules' array cannot be empty")

        for idx, molecule in enumerate(config["molecules"]):
            if "name" not in molecule:
                logger.error(f"Missing 'name' field in molecule at index {idx}")
                raise ValueError(
                    f"Each molecule must have a 'name' field (missing in molecule at index {idx})"
                )
            validate_molecule_section(molecule, is_array_item=True)

    # At least one of the computational sections must be present
    if not any(
        step in config for step in ["optimization", "frequency", "single_point"]
    ):
        logger.error("No computational sections found in config")
        raise ValueError(
            "At least one of [optimization], [frequency], or [single_point] sections must be present"
        )

    logger.debug("Configuration validation successful")


def validate_molecule_section(molecule: dict, is_array_item: bool = False) -> None:
    """Validate a molecule section or a molecule item in the molecules array."""
    section_name = (
        "molecule"
        if not is_array_item
        else f"molecule '{molecule.get('name', '<unnamed>')}'"
    )

    required_fields = ["charge", "mult", "xyz_file"]
    for field in required_fields:
        if field not in molecule:
            logger.error(f"Missing required field '{field}' in {section_name} section")
            raise ValueError(
                f"Missing required field '{field}' in {section_name} section"
            )


def generate_slurm_script(config_file: Path, config: dict) -> str:
    """Generate a SLURM batch script for the calculation."""
    logger.debug("Generating SLURM batch script")

    # Extract SLURM settings or use defaults
    slurm_config = config.get("slurm", {})
    job_name = slurm_config.get("job_name", config_file.name)
    partition = slurm_config.get("partition", "normal")
    nodes = slurm_config.get("nodes", 1)
    ntasks = slurm_config.get("ntasks", 1)
    cpus = config["general"].get("cpus", 1)
    mem_per_cpu_gb = f"{config['general'].get('mem_per_cpu_gb', 1)}GB"
    time = f"{slurm_config.get('time_h', 24)}:00:00"

    logger.debug(f"SLURM job name: {job_name}")
    logger.debug(f"SLURM partition: {partition}")
    logger.debug(f"SLURM nodes: {nodes}")
    logger.debug(f"SLURM tasks: {ntasks}")
    logger.debug(f"SLURM CPUs: {cpus}")
    logger.debug(f"SLURM memory: {mem_per_cpu_gb}")
    logger.debug(f"SLURM time: {time}")

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
# ORCA uses 'ntasks' CPU cores and one core per task
#SBATCH --ntasks={cpus}
#SBATCH --cpus-per-task={ntasks}
#SBATCH --mem-per-cpu={mem_per_cpu_gb}
#SBATCH --time={time}
#SBATCH --output=%x-%j.slurm_log
#SBATCH --error=%x-%j.slurm_log
{account_line}
{email_line}
{email_type_line}


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


@cli.command()
def example_config():
    """Generate an example configuration file."""
    example = """
    # Orcastrator Configuration File

    [general]
    output_dir = "calculations"     # Directory for calculation outputs
    cpus = 1                        # Number of CPU cores
    mem_per_cpu_gb = 1              # RAM per CPU core in GB
    scratch_dir = "/scratch"        # Scratch directory (optional)
    overwrite = false               # Whether to overwrite existing calculations
    keep_scratch = false            # Whether to keep scratch directories

    # Single molecule approach (alternative to [[molecules]] array)
    # [molecule]
    # charge = 0                    # Molecular charge
    # mult = 1                      # Spin multiplicity
    # xyz_file = "molecule.xyz"     # Path to input XYZ file

    # Multiple molecules approach (preferred for multiple species)
    [[molecules]]
    name = "fe_cy_m2"               # Name of the molecule (used for directory naming)
    xyz_file = "initial_xyz_files/fe_cy.xyz"  # Path to input XYZ file
    charge = 1                      # Molecular charge
    mult = 2                # Spin multiplicity

    [[molecules]]
    name = "fe_cy_m4"
    xyz_file = "initial_xyz_files/fe_cy.xyz"
    charge = 1
    mult = 4

    [[molecules]]
    name = "fe_cy_m6"
    xyz_file = "initial_xyz_files/fe_cy.xyz"
    charge = 1
    mult = 6

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
