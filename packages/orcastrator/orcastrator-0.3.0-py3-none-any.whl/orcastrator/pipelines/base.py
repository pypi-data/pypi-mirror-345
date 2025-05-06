from abc import ABC, abstractmethod
from pathlib import Path
import logging
from typing import Any, Dict, Optional, List

import tomllib as toml

from orcastrator.logger import logger, configure_logging
from orcastrator.slurm import SlurmConfig, SlurmBatchGenerator


LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}

class Pipeline(ABC):
    """Base class for all computational pipelines."""

    def __init__(
        self,
        name: str,
        directory: Path,
        slurm_config: Dict[str, Any],
        overwrite: bool = False,
        log_level: str = "info",
        log_file: Optional[str | Path] = None,
    ):
        """
        Initialize the base pipeline.

        Args:
            name: Name of the pipeline
            directory: Working directory for pipeline outputs
            slurm_config: Dictionary with SLURM configuration options
            overwrite: Whether to overwrite existing files
            log_level: Logging level (debug, info, warning, error)
            log_file: Optional path to log file
        """
        self.name = name
        self.directory = Path(directory)
        self.directory.mkdir(exist_ok=True, parents=True)
        self.slurm_config = slurm_config
        self.overwrite = overwrite
        self.log_level = log_level
        self.log_file = log_file
        self.config_file = None

        # Set up logging
        if log_file:
            if not Path(log_file).is_absolute():
                log_file = self.directory / log_file
        configure_logging(level=LOG_LEVELS[log_level], log_file=log_file)

        logger.info(f"Initialized pipeline '{name}' in {self.directory}")

    @abstractmethod
    def run(self) -> None:
        """Run the pipeline. Must be implemented by subclasses."""
        pass

    def create_slurm_script(self, output_path: Optional[Path] = None) -> Path:
        """
        Create a SLURM batch script for running this pipeline.

        Args:
            output_path: Path where to save the SLURM script (default: directory/name.slurm)

        Returns:
            Path to the generated SLURM batch script
        """
        if output_path is None:
            output_path = self.directory / f"{self.name}.slurm"

        # Extract current config file path if it was loaded from a file
        config_file = getattr(self, 'config_file', None)

        # Set up slurm configuration
        slurm_conf = SlurmConfig(
            file=str(config_file) if config_file else str(self.directory / f"{self.name}.toml"),
            job_name=self.slurm_config.get("job_name", self.name),
            **{k: v for k, v in self.slurm_config.items() if k != "job_name"}
        )

        # Create generator and write script
        generator = SlurmBatchGenerator(slurm_conf, "-m orcastrator.pipeline_runner")
        return generator.write_script(output_path)

    @classmethod
    def from_toml(cls, file_path: str | Path) -> "Pipeline":
        """
        Create a pipeline from a TOML configuration file.

        Args:
            file_path: Path to the TOML configuration file

        Returns:
            Initialized pipeline instance
        """
        file_path = Path(file_path)
        try:
            config = toml.loads(file_path.read_text())

            # Validate required sections
            if "pipeline" not in config:
                raise ValueError("Missing 'pipeline' section in TOML file")
            if "slurm" not in config:
                raise ValueError("Missing 'slurm' section in TOML file")

            # Get pipeline type and create appropriate instance
            pipeline_type = config["pipeline"].get("type")
            if not pipeline_type:
                raise ValueError("Pipeline type not specified in TOML file")

            # Import the pipeline registry to get the appropriate class
            from orcastrator.pipelines import get_pipeline
            pipeline_class = get_pipeline(pipeline_type)

            # Store the config file path for reference
            pipeline = pipeline_class.from_config(config, file_path)
            pipeline.config_file = file_path

            return pipeline

        except Exception as e:
            logger.error(f"Error loading pipeline from {file_path}: {e}")
            raise

    @classmethod
    @abstractmethod
    def from_config(cls, config: Dict[str, Any], config_path: Path) -> "Pipeline":
        """
        Create a pipeline from a configuration dictionary.
        Must be implemented by subclasses to handle specific config formats.

        Args:
            config: Dictionary with configuration options
            config_path: Path to the original config file (for resolving relative paths)

        Returns:
            Initialized pipeline instance
        """
        pass
