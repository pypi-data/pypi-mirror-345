import shutil
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Optional

from orcastrator.engines import OrcaEngine
from orcastrator.geometry import Geometry
from orcastrator.level_of_theory import LevelOfTheory
from orcastrator.logger import logger


@dataclass
class Calculation:
    name: str
    directory: Path
    level_of_theory: LevelOfTheory
    overwrite: bool = False

    @property
    def source_dir(self) -> Path:
        return self.directory / self.name

    @property
    def input_file(self) -> Path:
        return self.source_dir / f"{self.name}.inp"

    @property
    def output_file(self) -> Path:
        return self.input_file.with_suffix(".out")

    def run(self, engine: OrcaEngine) -> Path:
        """Run the calculation and return the output file"""
        engine.run(self)
        return self.output_file

    def get_optimized_geometry(self) -> Geometry:
        xyz_file = self.output_file.with_suffix(".xyz")
        if not xyz_file.exists():
            raise FileNotFoundError(f"Optimized geometry {xyz_file} not found")
        return Geometry.from_xyz_file(
            self.level_of_theory.charge, self.level_of_theory.mult, xyz_file
        )

    def copy_with(self, **kwargs) -> "Calculation":
        return replace(self, **kwargs)

    def check_output(self) -> bool:
        for line in reversed(self.output_file.read_text().splitlines()):
            if "****ORCA TERMINATED NORMALLY****" in line:
                return True
        return False

    def setup(self, cpus: Optional[int] = None, mem_per_cpu_gb: Optional[int] = None) -> None:
        # Check if calculation dir already exists
        logger.info(f"Setting up {self.source_dir}")
        if self.source_dir.exists():
            logger.debug(f"Directory {self.source_dir} already exists")
            if self.overwrite:
                logger.info(f"Overwriting existing source_dir: {self.source_dir}")
                shutil.rmtree(self.source_dir)
            else:
                raise IsADirectoryError(
                    f"Directory {self.source_dir} already exists and overwrite=False"
                )

        # Create calculation source_dir
        self.source_dir.mkdir(parents=True)
        logger.debug(f"Created source_dir: {self.source_dir}")

        # Create input file
        if cpus:
            self.level_of_theory.blocks["pal"] = f"%PAL NPROCS {cpus} END"
        if mem_per_cpu_gb:
            self.level_of_theory.blocks["maxcore"] = f"%MAXCORE {mem_per_cpu_gb * 1000}"
        self.level_of_theory.write_to(self.input_file)
        logger.debug(f"Created input file: {self.input_file}")
        logger.debug(f"Input file contents:\n{self.input_file.read_text()}")
