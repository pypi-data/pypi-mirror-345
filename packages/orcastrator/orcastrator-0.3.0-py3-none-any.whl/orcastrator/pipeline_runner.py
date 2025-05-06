import sys
from pathlib import Path

from orcastrator.logger import configure_logging, logger
from orcastrator.pipelines.base import Pipeline

def main():
    """
    Main entry point for running a pipeline from a TOML configuration file.
    """
    if len(sys.argv) < 2:
        print("Usage: python -m orcastrator.pipeline_runner <config_file>")
        return 1

    config_file = Path(sys.argv[1])
    if not config_file.exists():
        print(f"Error: Configuration file not found: {config_file}")
        return 1

    try:
        # Create pipeline from config
        pipeline = Pipeline.from_toml(config_file)

        # Run the pipeline
        pipeline.run()

        return 0
    except Exception as e:
        logger.error(f"Error running pipeline: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
