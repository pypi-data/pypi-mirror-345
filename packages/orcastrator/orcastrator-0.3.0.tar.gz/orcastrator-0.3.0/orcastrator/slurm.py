import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

from orcastrator.logger import logger


@dataclass
class SlurmConfig:
    """Configuration for a SLURM batch script."""

    # Required parameters
    file: str
    job_name: str

    # Optional parameters with defaults
    cpus: int = 1
    time_h: int = 72  # Default: three days
    ntasks: int = 1
    nodes: Optional[int] = None
    tasks_per_node: Optional[int] = None
    partition: Optional[str] = None
    mem_per_cpu_gb: Optional[int] = None  # Format: 4G, 1000M, etc.
    account: Optional[str] = None
    output: Optional[str] = None  # Default: slurm-%j.out
    error: Optional[str] = None   # Default: same as output
    mail_type: Optional[str] = None  # BEGIN, END, FAIL, ALL
    mail_user: Optional[str] = None
    exclusive: bool = False
    constraint: Optional[str] = None

    # Additional arbitrary SLURM directives
    extra_directives: Optional[Dict[str, str]] = None

    # Environment setup
    modules: Optional[List[str]] = None
    environment_vars: Optional[Dict[str, str]] = None
    setup_commands: Optional[List[str]] = None

    def __post_init__(self):
        """Initialize default values for collections if None."""
        if self.extra_directives is None:
            self.extra_directives = {}
        if self.modules is None:
            self.modules = []
        if self.environment_vars is None:
            self.environment_vars = {}
        if self.setup_commands is None:
            self.setup_commands = []


class SlurmBatchGenerator:
    """Generates SLURM batch scripts for running pipelines."""

    def __init__(self, config: SlurmConfig, pipeline_script: str, pipeline_args: Optional[List[str]] = None):
        """
        Initialize the SLURM batch generator.

        Args:
            config: SlurmConfig object with SLURM settings
            pipeline_script: Path to the pipeline script to run
            pipeline_args: List of arguments to pass to the pipeline script
        """
        self.config = config
        self.pipeline_script = Path(pipeline_script)
        self.pipeline_args = pipeline_args or []

    def generate_script(self) -> str:
        """Generate the SLURM batch script as a string."""
        lines = [
            "#!/bin/bash",
            f"#SBATCH --job-name={self.config.job_name}",
            f"#SBATCH --time={self.config.time_h}",
            f"#SBATCH --cpus-per-task={self.config.cpus}",
            f"#SBATCH --ntasks={self.config.ntasks}"
        ]

        # Optional parameters
        if self.config.nodes:
            lines.append(f"#SBATCH --nodes={self.config.nodes}")
        if self.config.tasks_per_node:
            lines.append(f"#SBATCH --ntasks-per-node={self.config.tasks_per_node}")
        if self.config.partition:
            lines.append(f"#SBATCH --partition={self.config.partition}")
        if self.config.mem_per_cpu_gb:
            lines.append(f"#SBATCH --mem-per-cpu={self.config.mem_per_cpu_gb}GB")
        if self.config.account:
            lines.append(f"#SBATCH --account={self.config.account}")
        if self.config.output:
            lines.append(f"#SBATCH --output={self.config.output}")
        if self.config.error:
            lines.append(f"#SBATCH --error={self.config.error}")
        if self.config.mail_type:
            lines.append(f"#SBATCH --mail-type={self.config.mail_type}")
        if self.config.mail_user:
            lines.append(f"#SBATCH --mail-user={self.config.mail_user}")
        if self.config.exclusive:
            lines.append("#SBATCH --exclusive")
        if self.config.constraint:
            lines.append(f"#SBATCH --constraint={self.config.constraint}")

        # Extra directives
        if self.config.extra_directives:
            for key, value in self.config.extra_directives.items():
                lines.append(f"#SBATCH --{key}={value}")

        # Environment setup
        lines.append("\n# Environment setup")

        # Load modules
        if self.config.modules:
            lines.append("\n# Load required modules")
            for module in self.config.modules:
                lines.append(f"module load {module}")

        # Environment variables
        if self.config.environment_vars:
            lines.append("\n# Set environment variables")
            for key, value in self.config.environment_vars.items():
                lines.append(f"export {key}={value}")

        # Setup commands
        if self.config.setup_commands:
            lines.append("\n# Setup commands")
            for cmd in self.config.setup_commands:
                lines.append(cmd)

        # Pipeline execution
        lines.append("\n# Execute the pipeline")
        cmd = f"uv run -v -m orcastrator.pipeline_runner {Path(self.config.file).resolve()}\n"
        if self.pipeline_args:
            cmd += " " + " ".join(self.pipeline_args)
        lines.append(cmd)

        return "\n".join(lines)

    def write_script(self, output_path: Union[str, Path]) -> Path:
        """Write the SLURM batch script to a file and return the file path."""
        output_path = Path(output_path)
        script_content = self.generate_script()

        output_path.write_text(script_content)
        output_path.chmod(0o755)  # Make executable

        logger.info(f"SLURM batch script written to: {output_path}")
        return output_path

    @classmethod
    def from_toml(cls, file: str | Path, toml_config: Dict, pipeline_script: str, pipeline_args: Optional[List[str]] = None):
        """Create a SlurmBatchGenerator from a TOML configuration dictionary."""
        if "slurm" not in toml_config:
            raise ValueError("TOML configuration must contain a 'slurm' section")

        slurm_config = toml_config["slurm"]

        # Check if a template is specified
        template_name = slurm_config.pop("template", None)

        if template_name:
            # Load the template first
            from orcastrator.slurm_templates import get_template
            try:
                template_config = get_template(template_name)

                # Override template settings with any specified in TOML
                for key, value in slurm_config.items():
                    if isinstance(value, dict) and key in template_config and isinstance(template_config[key], dict):
                        # For nested dictionaries like environment_vars, merge them
                        template_config[key].update(value)
                    else:
                        template_config[key] = value

                # Use the merged configuration
                slurm_config = template_config
            except ValueError as e:
                logger.warning(f"Template '{template_name}' not found: {e}. Using explicit configuration.")

        # Ensure required parameters exist
        required_params = ["job_name", "time_h"]
        for param in required_params:
            if param not in slurm_config:
                raise ValueError(f"Required SLURM parameter '{param}' missing from TOML configuration")

        # Create the SlurmConfig object
        config = SlurmConfig(
            file=str(file),
            job_name=slurm_config["job_name"],
            time_h=slurm_config["time_h"],
            cpus=slurm_config.get("cpus", 1),
            partition=slurm_config.get("partition", "normal"),
            nodes=slurm_config.get("nodes"),
            tasks_per_node=slurm_config.get("tasks_per_node"),
            mem_per_cpu_gb=slurm_config.get("mem_per_cpu_gb"),
            account=slurm_config.get("account"),
            output=slurm_config.get("output"),
            error=slurm_config.get("error"),
            mail_type=slurm_config.get("mail_type"),
            mail_user=slurm_config.get("mail_user"),
            exclusive=slurm_config.get("exclusive", False),
            constraint=slurm_config.get("constraint"),
            extra_directives=slurm_config.get("extra_directives", {}),
            modules=slurm_config.get("modules", []),
            environment_vars=slurm_config.get("environment_vars", {}),
            setup_commands=slurm_config.get("setup_commands", []),
        )

        return cls(config, pipeline_script, pipeline_args)

    @classmethod
    def from_template(cls, template_name: str, pipeline_script: str,
                      overrides: Optional[Dict[str, Any]] = None,
                      pipeline_args: Optional[List[str]] = None):
        """Create a SlurmBatchGenerator from a predefined template with optional overrides."""
        from orcastrator.slurm_templates import get_template

        # Get the template configuration
        config_dict = get_template(template_name)

        # Apply any overrides
        if overrides:
            for key, value in overrides.items():
                if isinstance(value, dict) and key in config_dict and isinstance(config_dict[key], dict):
                    # Merge dictionaries for nested fields like environment_vars
                    config_dict[key].update(value)
                else:
                    config_dict[key] = value

        # Create SlurmConfig from the dictionary
        config = SlurmConfig(**config_dict)

        return cls(config, pipeline_script, pipeline_args)



def create_slurm_script_from_toml(
    toml_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    pipeline_args: Optional[List[str]] = None
) -> Path:
    """
    Create a SLURM batch script from a TOML configuration file.

    Args:
        toml_path: Path to the TOML configuration file
        output_path: Path where to save the SLURM script (default: same dir as toml with .sh extension)
        pipeline_args: List of arguments to pass to the pipeline script

    Returns:
        Path to the generated SLURM batch script
    """
    import tomllib as toml

    toml_path = Path(toml_path)
    config = toml.loads(toml_path.read_text())

    # Use the built-in pipeline runner
    pipeline_script = "-m orcastrator.pipeline_runner"

    generator = SlurmBatchGenerator.from_toml(toml_path, config, pipeline_script, pipeline_args)

    if output_path is None:
        output_path = toml_path.with_suffix(".slurm")

    return generator.write_script(output_path)

def create_slurm_script_from_template(
    template_name: str,
    pipeline_script: str,
    output_path: Union[str, Path],
    overrides: Optional[Dict[str, Any]] = None,
    pipeline_args: Optional[List[str]] = None
) -> Path:
    """
    Create a SLURM batch script from a predefined template.

    Args:
        template_name: Name of the template to use
        pipeline_script: Path to the pipeline script to run
        output_path: Path where to save the SLURM script
        overrides: Dictionary of values to override in the template
        pipeline_args: List of arguments to pass to the pipeline script

    Returns:
        Path to the generated SLURM batch script
    """
    generator = SlurmBatchGenerator.from_template(
        template_name, pipeline_script, overrides, pipeline_args
    )
    return generator.write_script(output_path)
