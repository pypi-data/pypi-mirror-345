import argparse
import sys
import logging
import subprocess
from pathlib import Path

from orcastrator import configure_logging
from orcastrator.logger import logger
from orcastrator.pipelines import get_available_pipelines
from orcastrator.pipelines.base import Pipeline

def cli():
    """Main command-line interface for Orcastrator."""

    parser = argparse.ArgumentParser(
        description="Orcastrator: Organize and run computational chemistry pipelines"
    )

    parser.add_argument(
        "config",
        help="Path to TOML configuration file"
    )

    # Action group - mutually exclusive actions
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--create-slurm",
        action="store_true",
        help="Create a SLURM batch script without running the pipeline"
    )
    action_group.add_argument(
        "--run-pipeline",
        action="store_true",
        help="Run the pipeline directly without creating a SLURM script"
    )
    action_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Set up pipeline but don't execute it"
    )

    # SLURM related options
    slurm_group = parser.add_argument_group("SLURM options")
    slurm_group.add_argument(
        "--slurm-output",
        help="Output path for SLURM script (default: config_name.slurm)"
    )
    slurm_group.add_argument(
        "--submit",
        action="store_true",
        help="Submit the SLURM script to the queue after creation"
    )

    # Informational options
    info_group = parser.add_argument_group("Informational options")
    info_group.add_argument(
        "--list-pipelines",
        action="store_true",
        help="List available pipeline types"
    )

    # Logging options
    log_group = parser.add_argument_group("Logging options")
    log_group.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose (DEBUG) logging"
    )
    log_group.add_argument(
        "--log-file",
        help="Path to log file (in addition to console logging)"
    )

    args = parser.parse_args()

    # Configure logging first
    log_level = logging.DEBUG if args.verbose else logging.INFO
    configure_logging(level=log_level, log_file=args.log_file)

    # List available pipelines if requested (this exits after listing)
    if args.list_pipelines:
        pipelines = get_available_pipelines()
        print("Available pipeline types:")
        for p in pipelines:
            print(f"  - {p}")
        return 0

    # Validate config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        return 1

    try:
        # Create the pipeline from the config
        pipeline = Pipeline.from_toml(config_path)
        logger.debug(f"Successfully loaded pipeline from {config_path}")
    except Exception as e:
        logger.error(f"Error loading pipeline: {e}")
        return 1

    # Default action is to create SLURM script if no other action specified
    if not (args.run_pipeline or args.dry_run):
        args.create_slurm = True

    # Create SLURM script
    if args.create_slurm:
        slurm_output = args.slurm_output or config_path.with_suffix(".slurm")
        try:
            script_path = pipeline.create_slurm_script(Path(slurm_output))
            logger.info(f"Successfully created SLURM script: {script_path}")

            if args.submit:
                logger.info(f"Submitting SLURM script: {script_path}")
                result = subprocess.run(["sbatch", script_path.resolve()],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"Job submitted: {result.stdout}")
                else:
                    logger.error(f"Error submitting job: {result.stderr}")
                    return 1
        except Exception as e:
            logger.error(f"Error creating SLURM script: {e}")
            return 1

    # Run the pipeline directly
    if args.run_pipeline:
        try:
            pipeline.run()
        except Exception as e:
            logger.error(f"Error running pipeline: {e}")
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(cli())
