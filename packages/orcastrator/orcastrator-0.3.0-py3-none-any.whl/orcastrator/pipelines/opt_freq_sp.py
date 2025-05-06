import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

from morca import OrcaOutput

from orcastrator import OrcaEngine, configure_logging, logger
from orcastrator.calculation import Calculation
from orcastrator.geometry import Geometry
from orcastrator.level_of_theory import LevelOfTheory
from orcastrator.pipelines.base import Pipeline

class OptFreqSinglePoint(Pipeline):
    def __init__(
        self,
        name: str,
        directory: Path,
        initial_geom: Geometry,
        lots: List[str],
        cpus: int,
        mem_per_cpu_gb: int,
        slurm_config: Dict[str, Any],
        overwrite: bool = False,
        log_level: str = "info",
        log_file: Optional[str | Path] = None,
    ) -> None:
        """
        Initialize the Optimization + Frequency + Single Point pipeline.

        Args:
            name: Name of the pipeline
            directory: Working directory for calculations
            initial_geom: Initial molecular geometry
            lots: List of ORCA-like level of theory strings
            cpus: Number of CPU cores to use
            mem_per_cpu_gb: Memory per CPU in GB
            slurm_config: SLURM configuration options
            overwrite: Whether to overwrite existing calculations
            log_level: Logging level
            log_file: Path to log file
        """
        super().__init__(
            name=name,
            directory=directory,
            slurm_config=slurm_config,
            overwrite=overwrite,
            log_level=log_level,
            log_file=log_file,
        )

        # Initialize pipeline attributes
        self.initial_geom = initial_geom

        # Process levels of theory
        if len(lots) == 2:
            lots = [lots[0], lots[0], lots[1]]
        elif len(lots) != 3:
            raise ValueError("Three levels of theory required (or two for OPT/FREQ and SP)")

        self.lots = [
            LevelOfTheory().read_input(lot).set_geometry(self.initial_geom)
            for lot in lots
        ]

        # Initialize the calculation engine
        self.engine = OrcaEngine(cpus, mem_per_cpu_gb)

    def run(self) -> None:
        """Run the Optimization + Frequency + Single Point pipeline."""
        logger.info(f"\n\n ------ Running {self.name} pipeline")

        # Optimization step
        opt = Calculation(
            name="opt",
            directory=self.directory,
            level_of_theory=self.lots[0].add_keyword("OPT"),
            overwrite=self.overwrite,
        )
        opt_out = opt.run(self.engine)
        opt_xyz_file = opt_out.with_suffix(".xyz")
        logger.info("--- OPT calculation finished")

        # Frequency step
        freq = opt.copy_with(
            name="freq",
            level_of_theory=self.lots[1]
            .set_geometry_from_file(opt_xyz_file)
            .add_keyword("FREQ"),
        )
        freq_out = OrcaOutput(freq.run(self.engine))
        logger.info("--- FREQ calculation finished")

        # Single point step
        sp = freq.copy_with(name="sp", level_of_theory=self.lots[2])
        sp_out = OrcaOutput(sp.run(self.engine))
        logger.info("--- SP calculation finished")

        # Print results
        print(
            f"Enthalpy: {freq_out.enthalpy_eh}\nGibbs free energy: {freq_out.gibbs_free_energy_eh}\n"
        )
        print(
            f"Corrected Gibbs free energy: {sp_out.fspe_eh + freq_out.gibbs_free_energy_correction_eh}\n"
        )

    @classmethod
    def from_config(cls, config: Dict[str, Any], config_path: Path) -> "OptFreqSinglePoint":
        """Create an OptFreqSinglePoint pipeline from a configuration dictionary."""
        pipeline_config = config["pipeline"]
        slurm_config = config["slurm"]

        # Resolve directory path (relative to config file location)
        directory = pipeline_config.get("directory")
        if directory:
            directory = Path(directory)
            if not directory.is_absolute():
                directory = config_path.parent / directory
        else:
            directory = config_path.parent / "calculations"

        # Set up geometry
        geom_config = config.get("geometry", {})
        charge = geom_config.get("charge", 0)
        mult = geom_config.get("mult", 1)

        # Create initial geometry
        if xyz_file := geom_config.get("xyz_file"):
            xyz_path = Path(xyz_file)
            if not xyz_path.is_absolute():
                xyz_path = config_path.parent / xyz_path
            initial_geom = Geometry.from_xyz_file(charge, mult, xyz_path)
        else:
            raise ValueError("Missing geometry.xyz_file in configuration")

        # Create the pipeline
        return cls(
            name=pipeline_config.get("name", "opt_freq_sp"),
            directory=directory,
            initial_geom=initial_geom,
            lots=pipeline_config["lots"],
            cpus=slurm_config.get("cpus", 1),
            mem_per_cpu_gb=slurm_config.get("mem_per_cpu_gb", 4),
            slurm_config=slurm_config,
            overwrite=pipeline_config.get("overwrite", False),
            log_level=pipeline_config.get("log_level", "info"),
            log_file=pipeline_config.get("log_file"),
        )
