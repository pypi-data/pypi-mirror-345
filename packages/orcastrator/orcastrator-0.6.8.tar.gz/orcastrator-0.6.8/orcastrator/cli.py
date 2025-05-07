import logging
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click

try:
    import toml  # type: ignore
except ModuleNotFoundError:
    import tomllib as toml  # Python 3.11+

from orcastrator.calculation import Calculation
from orcastrator.logger import (  # Assuming logger is the getLogger instance
    logger,
    setup_logger,
)

# apollo specific defaults - consider making these configurable or removing if not general
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
    help="Generate a SLURM batch script and submit it with sbatch",
)
@click.option(
    "--slurm-output",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output path for the SLURM script (default: config_file.slurm)",
)
@click.option(
    "--no-submit",
    is_flag=True,
    help="When used with --slurm, generate the script but don't submit with sbatch",
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity (can be used multiple times for more detail)",
)
def run(
    config_file: Path,
    slurm: bool,
    slurm_output: Optional[Path],
    no_submit: bool,
    verbose: int,
):
    """Run a calculation pipeline defined in a TOML config file."""
    overall_start_time = time.time()  # Start overall timing
    log_file = config_file.with_suffix(".log")

    console_level = logging.WARNING
    if verbose == 1:
        console_level = logging.INFO
    elif verbose >= 2:
        console_level = logging.DEBUG
    setup_logger(log_file=log_file, level=logging.DEBUG, console_level=console_level)

    logger.info(f"Starting Orcastrator run with config file: {config_file}")
    logger.debug(f"Log file location: {log_file}")

    try:
        logger.debug("Loading configuration file")
        config = toml.loads(config_file.read_text())
        logger.debug("Validating configuration")
        validate_config(config)

        # General settings
        general_config = config["general"]
        base_output_dir = config_file.parent / Path(general_config["output_dir"])
        scratch_base_dir_config = general_config.get("scratch_dir")

        # If scratch_dir is absolute, use it. Otherwise, relative to base_output_dir.
        if scratch_base_dir_config:
            scratch_base_dir = Path(scratch_base_dir_config)
            if not scratch_base_dir.is_absolute():
                scratch_base_dir = (
                    config_file.parent / scratch_base_dir_config
                ).resolve()
        else:
            # Default scratch inside each molecule's output directory if not specified globally
            # This will be handled per molecule later. For now, set to None.
            scratch_base_dir = None

        cpus = general_config.get("cpus", 1)
        mem_per_cpu_gb = general_config.get(
            "mem_per_cpu_gb"
        )  # Optional, None if not set
        overwrite = general_config.get("overwrite", False)
        keep_scratch = general_config.get("keep_scratch", False)

        logger.info(f"Base output directory: {base_output_dir}")
        if scratch_base_dir:
            logger.info(f"Global scratch base directory: {scratch_base_dir}")
        else:
            logger.info(
                "Scratch directory will be per molecule or per calculation step."
            )
        logger.info(f"Using {cpus} CPU(s)")
        if mem_per_cpu_gb:
            logger.info(f"Using {mem_per_cpu_gb}GB RAM per CPU")
        logger.debug(f"Overwrite existing: {overwrite}")
        logger.debug(f"Keep scratch: {keep_scratch}")

        pipeline_steps = config.get("pipeline", [])
        if not pipeline_steps:
            logger.error("No 'pipeline' steps defined in the configuration.")
            raise ValueError(
                "The 'pipeline' section is missing or empty in the config file."
            )

        if slurm:
            slurm_output_path = slurm_output or config_file.with_suffix(".slurm")
            logger.info(f"Generating SLURM script at {slurm_output_path}")
            slurm_script_content = generate_slurm_script(
                config_file=config_file, config=config
            )
            slurm_output_path.write_text(slurm_script_content)
            logger.info("SLURM script generated successfully")

            if not no_submit:
                # Submit the script using sbatch
                import subprocess

                logger.info(f"Submitting SLURM script with sbatch: {slurm_output_path}")
                try:
                    result = subprocess.run(
                        ["sbatch", str(slurm_output_path)],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    # Extract and display the job ID from the sbatch output
                    # Typical output is "Submitted batch job 123456"
                    job_id = result.stdout.strip().split()[-1]
                    logger.info(f"Job submitted successfully with ID: {job_id}")
                    click.echo(f"SLURM job submitted with ID: {job_id}")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to submit job: {e}")
                    logger.error(f"STDOUT: {e.stdout}")
                    logger.error(f"STDERR: {e.stderr}")
                    click.echo(f"Error submitting job: {e}", err=True)
                    raise RuntimeError(f"Failed to submit SLURM job: {e}")
            else:
                click.echo(
                    f"SLURM script generated at {slurm_output_path} (not submitted due to --no-submit)"
                )
        else:
            molecules_to_process = []

            # Check for molecule section first
            if "molecule" in config:
                # Check if molecule section contains xyz_dir
                if "xyz_dir" in config["molecule"]:
                    xyz_dir_path = config_file.parent / Path(
                        config["molecule"]["xyz_dir"]
                    )
                    logger.info(f"Processing XYZ files from directory: {xyz_dir_path}")

                    if not xyz_dir_path.exists() or not xyz_dir_path.is_dir():
                        logger.error(
                            f"XYZ directory not found or not a directory: {xyz_dir_path}"
                        )
                        raise ValueError(
                            f"XYZ directory not found or not a directory: {xyz_dir_path}"
                        )

                    # Get default charge and mult if provided in the molecule section
                    default_charge = config["molecule"].get("charge")
                    default_mult = config["molecule"].get("mult")

                    if default_charge is not None or default_mult is not None:
                        logger.info(
                            "Using fallback defaults from [molecule] section: "
                            + f"charge={default_charge if default_charge is not None else 'not set'}, "
                            + f"mult={default_mult if default_mult is not None else 'not set'}"
                        )

                    molecules_to_process = scan_xyz_directory(
                        xyz_dir_path,
                        default_charge=default_charge,
                        default_mult=default_mult,
                    )

                    if not molecules_to_process:
                        logger.error(
                            f"No valid XYZ files found in directory: {xyz_dir_path}"
                        )
                        raise ValueError(
                            f"No valid XYZ files found in directory: {xyz_dir_path}"
                        )

                # If not using xyz_dir, it's a single molecule definition
                elif all(
                    key in config["molecule"] for key in ["xyz_file", "charge", "mult"]
                ):
                    single_mol = config["molecule"]
                    if "name" not in single_mol:
                        single_mol["name"] = config_file.stem
                    molecules_to_process = [single_mol]
                else:
                    logger.error(
                        "Invalid molecule section: must contain either xyz_dir or (xyz_file, charge, mult)"
                    )
                    raise ValueError("Invalid molecule section configuration")

            # Check for molecules array as another option
            elif "molecules" in config:
                molecules_to_process = config["molecules"]

            if not molecules_to_process:
                logger.error(
                    "No molecules defined. Use either [molecule] with xyz_dir or xyz_file, or [[molecules]] array."
                )
                raise ValueError("No molecules found in the configuration.")

            logger.info(f"Found {len(molecules_to_process)} molecule(s) to process.")
            for idx, molecule_config in enumerate(molecules_to_process, 1):
                mol_name = molecule_config["name"]
                logger.info(
                    f"Processing molecule {idx}/{len(molecules_to_process)}: {mol_name}"
                )

                # Per-molecule output directory
                molecule_output_dir = base_output_dir / mol_name
                molecule_output_dir.mkdir(parents=True, exist_ok=True)

                # Per-molecule scratch directory (if global scratch_base_dir is set)
                # If scratch_base_dir is None, Calculation will use its parent_dir / "scratch_for_molecule"
                molecule_specific_scratch_base = None
                if scratch_base_dir:
                    molecule_specific_scratch_base = scratch_base_dir / mol_name
                    molecule_specific_scratch_base.mkdir(parents=True, exist_ok=True)

                process_molecule_pipeline(
                    molecule_config=molecule_config,
                    molecule_output_dir=molecule_output_dir,  # This is the parent_dir for Calculations
                    pipeline_steps=pipeline_steps,
                    cpus=cpus,
                    mem_per_cpu_gb=mem_per_cpu_gb,
                    scratch_base_dir_for_molecule=molecule_specific_scratch_base,  # Pass this to Calculation
                    overwrite=overwrite,
                    keep_scratch=keep_scratch,
                    config_file_parent=config_file.parent,
                )
            logger.info("All molecules processed successfully.")
            overall_elapsed_time = time.time() - overall_start_time
            logger.info(
                f"Total runtime: {overall_elapsed_time:.2f} seconds ({format_time(overall_elapsed_time)})"
            )
            click.echo(
                f"Pipeline completed successfully in {format_time(overall_elapsed_time)}"
            )

    except Exception as e:
        # Calculate time even on error
        overall_elapsed_time = time.time() - overall_start_time
        logger.exception(
            f"Error during execution after {format_time(overall_elapsed_time)}: {str(e)}"
        )
        click.echo(
            f"Error after {format_time(overall_elapsed_time)}: {str(e)}", err=True
        )
        if log_file:  # Check if log_file was defined
            click.echo(f"See log file for details: {log_file}", err=True)
        sys.exit(1)


def process_molecule_pipeline(
    molecule_config: dict,
    molecule_output_dir: Path,  # This is the parent_dir for all Calculation steps of this molecule
    pipeline_steps: List[Dict[str, Any]],
    cpus: int,
    mem_per_cpu_gb: Optional[int],
    scratch_base_dir_for_molecule: Optional[
        Path
    ],  # Base for this molecule's scratch, passed to Calculation
    overwrite: bool,
    keep_scratch: bool,
    config_file_parent: Path,
):
    """Process a single molecule through the defined pipeline."""
    molecule_start_time = time.time()  # Start timing for this molecule
    mol_name = molecule_config["name"]
    default_charge = molecule_config["charge"]
    default_mult = molecule_config["mult"]
    initial_xyz_file = config_file_parent / Path(molecule_config["xyz_file"])

    logger.info(f"Starting pipeline for molecule: {mol_name}")
    logger.info(f"  Initial XYZ: {initial_xyz_file}")
    logger.info(f"  Default Charge: {default_charge}, Multiplicity: {default_mult}")
    logger.info(f"  Output directory for this molecule: {molecule_output_dir}")
    if scratch_base_dir_for_molecule:
        logger.info(
            f"  Scratch base for this molecule: {scratch_base_dir_for_molecule}"
        )

    previous_calc: Optional[Calculation] = None

    for i, step_config in enumerate(pipeline_steps):
        step_start_time = time.time()  # Start timing for this step
        step_name = step_config["name"]
        step_keywords = step_config["keywords"]
        step_blocks = step_config.get("blocks", [])
        step_charge = step_config.get("charge", default_charge)
        step_mult = step_config.get("mult", default_mult)

        logger.info(
            f"--- Pipeline Step {i + 1}/{len(pipeline_steps)}: '{step_name}' for molecule '{mol_name}' ---"
        )
        logger.debug(
            f"  Step Config: Name='{step_name}', Charge={step_charge}, Mult={step_mult}"
        )
        logger.debug(f"  Keywords: {step_keywords}")
        logger.debug(f"  Blocks: {step_blocks}")

        current_calc: Calculation
        if previous_calc is None:  # First step
            logger.debug(
                f"  This is the first step. Initializing calculation from {initial_xyz_file}."
            )
            current_calc = Calculation(
                name=step_name,
                parent_dir=molecule_output_dir,  # All steps for this molecule share this parent_dir
                charge=step_charge,
                mult=step_mult,
                atoms=[],  # Will be set from XYZ
                keywords=step_keywords,
                blocks=step_blocks,
                cpus=cpus,
                mem_per_cpu_gb=mem_per_cpu_gb,
                scratch_base_dir=scratch_base_dir_for_molecule,  # This is Calculation's scratch_base_dir
                overwrite=overwrite,
                keep_scratch=keep_scratch,
            )
            try:
                current_calc.set_atoms_from_xyz_file(initial_xyz_file)
            except FileNotFoundError:
                logger.error(
                    f"Initial XYZ file not found: {initial_xyz_file} for step '{step_name}' of molecule '{mol_name}'"
                )
                raise
            except ValueError as e:  # XYZ parsing error
                logger.error(
                    f"Error parsing initial XYZ file {initial_xyz_file} for step '{step_name}' of molecule '{mol_name}': {e}"
                )
                raise

        else:  # Subsequent step
            logger.debug(f"  This is a follow-up step from '{previous_calc.name}'.")
            current_calc = previous_calc.create_follow_up(
                name=step_name,
                set_all_keywords=step_keywords,  # create_follow_up will handle this
                set_blocks=step_blocks,  # and this
                new_charge=step_charge,  # and this
                new_mult=step_mult,  # and this
            )
            # Ensure other parameters are consistent if create_follow_up doesn't copy all
            current_calc.cpus = cpus
            current_calc.mem_per_cpu_gb = mem_per_cpu_gb
            current_calc.scratch_base_dir = scratch_base_dir_for_molecule
            current_calc.overwrite = overwrite
            current_calc.keep_scratch = keep_scratch
            # parent_dir is inherited correctly by create_follow_up

        logger.info(f"Running step '{step_name}' for molecule '{mol_name}'...")
        try:
            success = current_calc.run()
            if not success:
                logger.error(
                    f"Step '{step_name}' for molecule '{mol_name}' failed to terminate normally. Stopping pipeline for this molecule."
                )
                # Optionally, re-raise an exception or return a status
                raise RuntimeError(
                    f"ORCA calculation for step '{step_name}', molecule '{mol_name}' failed."
                )
            logger.info(
                f"Step '{step_name}' for molecule '{mol_name}' completed successfully."
            )
        except IsADirectoryError as e:  # Catch overwrite issues specifically
            logger.error(
                f"Directory conflict for step '{step_name}', molecule '{mol_name}': {e}"
            )
            logger.error(
                "If you intend to overwrite, set 'overwrite = true' in the [general] section of your config."
            )
            raise
        except Exception as e:
            logger.error(
                f"An error occurred during execution of step '{step_name}' for molecule '{mol_name}': {e}"
            )
            raise  # Re-raise to stop processing or be caught by the main try-except

        step_elapsed_time = time.time() - step_start_time
        logger.info(
            f"Step '{step_name}' for molecule '{mol_name}' completed in {step_elapsed_time:.2f} seconds ({format_time(step_elapsed_time)})"
        )
        previous_calc = current_calc

    molecule_elapsed_time = time.time() - molecule_start_time
    logger.info(
        f"Pipeline for molecule '{mol_name}' completed all steps in {molecule_elapsed_time:.2f} seconds ({format_time(molecule_elapsed_time)})"
    )

    # Clean up the molecule-specific scratch directory if it exists and keep_scratch is False
    if (
        not keep_scratch
        and scratch_base_dir_for_molecule
        and scratch_base_dir_for_molecule.exists()
    ):
        try:
            logger.info(
                f"Cleaning up molecule scratch directory: {scratch_base_dir_for_molecule}"
            )
            shutil.rmtree(scratch_base_dir_for_molecule)
        except OSError as e:
            logger.error(f"Error removing molecule scratch directory: {e}")
    logger.info(f"Pipeline for molecule '{mol_name}' completed all steps.")


def validate_config(config: dict) -> None:
    logger.debug("Validating configuration file")

    if "general" not in config:
        raise ValueError("Missing required section 'general' in config file")
    required_general = ["output_dir"]
    for field in required_general:
        if field not in config["general"]:
            raise ValueError(f"Missing required field '{field}' in [general] section")

        # Ensure we have at least one method to define molecules
        if "molecule" not in config and "molecules" not in config:
            raise ValueError(
                "Either a 'molecule' section or 'molecules' array must be present"
            )

        # Validate molecule section if present
        if "molecule" in config:
            # Check for either xyz_dir or standard molecule fields
            has_xyz_dir = "xyz_dir" in config["molecule"]
            has_std_fields = all(
                field in config["molecule"] for field in ["xyz_file", "charge", "mult"]
            )

            if not (has_xyz_dir or has_std_fields):
                raise ValueError(
                    "The [molecule] section must contain either 'xyz_dir' OR all of these: 'xyz_file', 'charge', 'mult'"
                )

            # If using xyz_dir, validate it
            if has_xyz_dir:
                if not isinstance(config["molecule"]["xyz_dir"], str):
                    raise ValueError(
                        "Field 'xyz_dir' in [molecule] section must be a string path"
                    )

            # If standard fields, validate them
            elif has_std_fields:
                validate_molecule_section(config["molecule"])

        # Validate molecules array if present
        if "molecules" in config:
            if not isinstance(config["molecules"], list) or not config["molecules"]:
                raise ValueError(
                    "'molecules' must be a non-empty array of molecule objects"
                )
            for idx, molecule in enumerate(config["molecules"]):
                if "name" not in molecule:
                    raise ValueError(
                        f"Missing 'name' field in molecule at index {idx} in 'molecules' array"
                    )
                validate_molecule_section(
                    molecule, is_array_item=True, item_name=molecule.get("name")
                )

    if (
        "pipeline" not in config
        or not isinstance(config["pipeline"], list)
        or not config["pipeline"]
    ):
        raise ValueError(
            "Missing or empty 'pipeline' array in config file. Define at least one step."
        )

    for idx, step in enumerate(config["pipeline"]):
        if not isinstance(step, dict):
            raise ValueError(
                f"Pipeline step at index {idx} is not a valid object/dictionary."
            )
        if "name" not in step or not isinstance(step["name"], str):
            raise ValueError(
                f"Pipeline step at index {idx} is missing a 'name' or it's not a string."
            )
        if "keywords" not in step or not isinstance(step["keywords"], list):
            raise ValueError(
                f"Pipeline step '{step['name']}' is missing 'keywords' or it's not a list."
            )
        if "blocks" in step and not isinstance(step["blocks"], list):
            raise ValueError(
                f"Pipeline step '{step['name']}' has 'blocks' but it's not a list."
            )
        if "charge" in step and not isinstance(step["charge"], int):
            raise ValueError(
                f"Pipeline step '{step['name']}' has 'charge' but it's not an integer."
            )
        if "mult" in step and not isinstance(step["mult"], int):
            raise ValueError(
                f"Pipeline step '{step['name']}' has 'mult' but it's not an integer."
            )

    # Deprecation warnings for old sections
    for old_section in ["optimization", "frequency", "single_point"]:
        if old_section in config:
            logger.warning(
                f"Configuration section '[{old_section}]' is deprecated. Use the 'pipeline' array instead."
            )

    if "xyz_dir" in config and ("molecule" in config or "molecules" in config):
        raise ValueError(
            "Cannot specify both 'xyz_dir' and 'molecule'/'molecules' in the same config. "
            "Use only one method to define molecules."
        )

    # Check that we have at least one method to define molecules
    if (
        "xyz_dir" not in config
        and "molecule" not in config
        and "molecules" not in config
    ):
        raise ValueError(
            "Either 'xyz_dir', 'molecule', or 'molecules' must be present to define molecules."
        )

    # Validate xyz_dir if present
    if "xyz_dir" in config:
        if not isinstance(config["xyz_dir"], str):
            raise ValueError("'xyz_dir' must be a string path to a directory")

    logger.debug("Configuration validation successful")


def validate_molecule_section(
    molecule: dict, is_array_item: bool = False, item_name: Optional[str] = None
) -> None:
    section_name_prefix = (
        f"molecule '{item_name}'" if is_array_item and item_name else "molecule"
    )

    required_fields = ["charge", "mult", "xyz_file"]
    if (
        not is_array_item and "name" not in molecule
    ):  # For single [molecule] section, name is not strictly required by this validator but good practice
        logger.debug(
            "Field 'name' is recommended for the single [molecule] section for clarity."
        )

    for field in required_fields:
        if field not in molecule:
            raise ValueError(
                f"Missing required field '{field}' in {section_name_prefix} section"
            )

    if not isinstance(molecule["charge"], int):
        raise ValueError(
            f"Field 'charge' in {section_name_prefix} section must be an integer."
        )
    if not isinstance(molecule["mult"], int):
        raise ValueError(
            f"Field 'mult' in {section_name_prefix} section must be an integer."
        )
    if not isinstance(molecule["xyz_file"], str):
        raise ValueError(
            f"Field 'xyz_file' in {section_name_prefix} section must be a string path."
        )


def generate_slurm_script(config_file: Path, config: dict) -> str:
    logger.debug("Generating SLURM batch script")

    slurm_config = config.get("slurm", {})
    general_config = config["general"]

    job_name = slurm_config.get("job_name", config_file.stem)
    partition = slurm_config.get("partition", "normal")
    nodes = slurm_config.get("nodes", 1)

    # SLURM ntasks should correspond to ORCA's %pal nprocs, which is general.cpus
    slurm_ntasks = general_config.get("cpus", 1)
    # cpus-per-task is usually 1 for ORCA MPI jobs, unless hybrid MPI/OpenMP
    # For simple MPI, each task is a core.
    cpus_per_task = slurm_config.get("cpus_per_task", 1)

    mem_per_cpu_val = general_config.get("mem_per_cpu_gb")
    mem_per_cpu_slurm = (
        f"{mem_per_cpu_val}G" if mem_per_cpu_val else "2G"
    )  # Default if not set

    time_h = slurm_config.get("time_h", 24)
    time_m = slurm_config.get("time_m", 0)
    time_s = slurm_config.get("time_s", 0)
    time_str = f"{time_h:02d}:{time_m:02d}:{time_s:02d}"

    account = slurm_config.get("account")
    account_line = f"#SBATCH --account={account}" if account else ""

    email = slurm_config.get("email")
    email_line = f"#SBATCH --mail-user={email}" if email else ""
    email_type = slurm_config.get("email_type", "END,FAIL")
    email_type_line = f"#SBATCH --mail-type={email_type}" if email else ""

    # Construct the command to run orcastrator itself
    # Use absolute path for config_file to be safe
    orcastrator_command = f"uvx orcastrator run {config_file.resolve()}"
    # Add verbosity to SLURM run if specified in CLI (this is tricky, SLURM script is static)
    # For now, SLURM script will run with default verbosity unless user edits it.

    script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --partition={partition}
#SBATCH --nodes={nodes}
#SBATCH --ntasks={slurm_ntasks}
#SBATCH --cpus-per-task={cpus_per_task}
#SBATCH --mem-per-cpu={mem_per_cpu_slurm}
#SBATCH --time={time_str}
#SBATCH --output=%x-%j.slurm.log
#SBATCH --error=%x-%j.slurm.log
{account_line}
{email_line}
{email_type_line}

echo "Job started at $(date)"
echo "Running on nodes: $SLURM_JOB_NODELIST"
echo "Using $SLURM_NTASKS tasks, $SLURM_CPUS_PER_TASK CPUs per task"

# Environment setup (adjust ORCA/OpenMPI paths if necessary)
# These defaults might not be suitable for all systems.
# Consider making these configurable in the TOML [slurm] section.
export ORCA_INSTALL_DIR="{DEFAULT_ORCA_DIR}"
export OPENMPI_INSTALL_DIR="{DEFAULT_OPENMPI_DIR}"

export PATH="$ORCA_INSTALL_DIR:$OPENMPI_INSTALL_DIR/bin:$PATH"
export LD_LIBRARY_PATH="$ORCA_INSTALL_DIR/lib:$OPENMPI_INSTALL_DIR/lib64:$LD_LIBRARY_PATH"

echo "ORCA executable: $(which orca)"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"

# Run the orcastrator command
echo "Executing: {orcastrator_command}"
{orcastrator_command}

echo "Job finished at $(date)"
"""
    return script


@cli.command()
def example_config():
    """Generate an example configuration file."""
    example = """
# Orcastrator Configuration File Example

[general]
output_dir = "orcastrator_output" # Directory for all calculation outputs
cpus = 4                          # Default CPU cores for ORCA calculations
mem_per_cpu_gb = 2                # Default RAM per CPU core in GB for ORCA (e.g., %maxcore)
# scratch_dir = "/path/to/global_scratch" # Optional: Global scratch base directory
overwrite = false                 # Whether to overwrite existing calculation step directories
keep_scratch = false              # Whether to keep scratch directories after calculations

# Two ways to define molecules:

# Option 1: Using [molecule] section with either:
# 1a: Directory of XYZ files (each becomes a molecule)
[molecule]
xyz_dir = "initial_geometries"    # Directory containing XYZ files
# Each XYZ file's comment line (2nd line) must contain charge and multiplicity
# Format should be either "charge=0 mult=1" or simply "0 1"

# OR

# 1b: Single explicit molecule
# [molecule]
# name = "my_molecule"            # Name for the molecule (used for directory naming)
# xyz_file = "path/to/molecule.xyz" # Path to input XYZ file (relative to this config file)
# charge = 0                      # Molecular charge
# mult = 1                        # Spin multiplicity

# Option 2: Multiple specific molecules using array
# [[molecules]]
# name = "water_dimer"
# xyz_file = "initial_geometries/water_dimer.xyz"
# charge = 0
# mult = 1

# [[molecules]]
# name = "formaldehyde_triplet"
# xyz_file = "initial_geometries/formaldehyde.xyz"
# charge = 0
# mult = 3

# Define the calculation pipeline (sequence of steps)
# Each step is executed in order. Geometry from the previous step's .xyz output
# (if any) is used as input for the current step.
[[pipeline]]
name = "geom_opt"
keywords = ["B3LYP", "def2-SVP", "D3BJ", "OPT"]
blocks = ["%geom MaxIter 200 end"]

[[pipeline]]
name = "freq_calc"
keywords = ["B3LYP", "def2-SVP", "D3BJ", "FREQ", "AnFreq"]

[[pipeline]]
name = "sp_tzvp"
keywords = ["B3LYP", "def2-TZVP", "D3BJ", "RIJCOSX"]

[[pipeline]]
name = "tddft_excited_states"
keywords = ["B3LYP", "def2-TZVP", "D3BJ", "RIJCOSX"]
blocks = ["%TDDFT NROOTS 10 END"]
# mult = 1  # Optional override of multiplicity

# SLURM configuration for generating batch scripts (optional)
[slurm]
job_name = "orcapipeline"      # SLURM job name (default: config file stem)
partition = "compute"          # SLURM partition/queue
nodes = 1                      # Number of nodes
# cpus = from [general]        # ntasks for SLURM is taken from general.cpus
# mem_per_cpu_gb = from [general] # mem-per-cpu for SLURM
cpus_per_task = 1              # SLURM cpus-per-task (usually 1 for MPI ORCA)
time_h = 12                    # Max wall time (hours)
time_m = 0                     # Max wall time (minutes)
# account = "your_project_account" # Optional: SLURM account
# email = "user@example.com"     # Optional: Email for notifications
# email_type = "ALL"             # Optional: SLURM email types (BEGIN, END, FAIL, ALL)
"""
    click.echo(example.strip())


def scan_xyz_directory(
    xyz_dir_path: Path,
    default_charge: Optional[int] = None,
    default_mult: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Scan a directory for XYZ files and create molecule configurations.
    Each XYZ file becomes a molecule with charge and multiplicity from the comment line.

    Args:
        xyz_dir_path: Path to directory containing XYZ files

    Returns:
        List of molecule configuration dictionaries
    """
    logger.info(f"Scanning directory for XYZ files: {xyz_dir_path}")
    molecules = []

    for xyz_file in xyz_dir_path.glob("*.xyz"):
        logger.debug(f"Processing XYZ file: {xyz_file}")

        try:
            # Read the XYZ file to extract charge and mult from the comment line
            with open(xyz_file, "r") as f:
                lines = f.readlines()

            if len(lines) < 2:
                logger.warning(f"XYZ file too short, skipping: {xyz_file}")
                continue

            comment_line = lines[1].strip()

            # Try to extract charge and multiplicity from comment line
            charge, mult = parse_charge_mult_from_comment(comment_line)

            # Use defaults if not found in comment line
            if charge is None and default_charge is not None:
                logger.info(
                    f"Using default charge={default_charge} for {xyz_file.name}"
                )
                charge = default_charge

            if mult is None and default_mult is not None:
                logger.info(
                    f"Using default multiplicity={default_mult} for {xyz_file.name}"
                )
                mult = default_mult

            # Skip if we still don't have both charge and mult
            if charge is None or mult is None:
                logger.warning(
                    f"Could not determine charge and/or multiplicity for {xyz_file.name}. "
                    f"Comment line: '{comment_line}'. No suitable defaults provided. Skipping this file."
                )
                continue

            # Create a molecule config using the stem of the filename as the name
            molecule_config = {
                "name": xyz_file.stem,
                "xyz_file": str(
                    xyz_file.relative_to(xyz_dir_path.parent)
                    if xyz_dir_path.parent in xyz_file.parents
                    else xyz_file
                ),
                "charge": charge,
                "mult": mult,
            }

            molecules.append(molecule_config)
            logger.info(
                f"Added molecule '{xyz_file.stem}' from {xyz_file} with charge={charge}, mult={mult}"
            )

        except Exception as e:
            logger.warning(f"Error processing XYZ file {xyz_file}: {str(e)}")
            continue

    logger.info(f"Found {len(molecules)} valid molecules in XYZ directory")
    return molecules


def parse_charge_mult_from_comment(
    comment_line: str,
) -> Tuple[Optional[int], Optional[int]]:
    """
    Parse charge and multiplicity from an XYZ file comment line.

    Expected formats:
    - "charge=0 mult=1"
    - "0 1"
    - "charge: 0, multiplicity: 1"

    Args:
        comment_line: Comment line from XYZ file

    Returns:
        Tuple of (charge, multiplicity) or (None, None) if parsing failed
    """
    charge = None
    mult = None

    tokens = [token.strip() for token in comment_line.replace(",", " ").split()]
    for token in tokens:
        if token.isdigit() or (token.startswith("-") and token[1:].isdigit()):
            if charge is None:
                charge = int(token)
            elif mult is None:
                mult = int(token)
        elif token.lower().startswith("charge"):
            charge = int(token.split("=")[-1].strip())
        elif token.lower().startswith("mult") or token.lower().startswith(
            "multiplicity"
        ):
            mult = int(token.split("=")[-1].strip())

    return charge, mult


def format_time(seconds: float) -> str:
    """Format seconds into a readable time string."""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} hours"


if __name__ == "__main__":
    cli()
