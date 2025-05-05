from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Protocol
from uuid import uuid4

from orcastrator.logger import logger


class QCEngine(Protocol):
    def run(self, calculation) -> bool: ...


class OrcaEngine:
    """Engine for running ORCA calculations.

    - `scratch`: str | Path = The scratch directory to use. Defaults to `$SCRATCH` or `/tmp`)
    """

    def __init__(self, cpus: int = 1, mem_per_cpu_gb: int = 4, binary_dir: Optional[str] = None, scratch: Optional[str] = None):
        self.cpus = cpus
        self.mem_per_cpu_gb = mem_per_cpu_gb

        # Set ORCA binaries
        if binary_dir:
            self.orca_binary_dir = Path(binary_dir).resolve()
            logger.debug(
                f"Using provided ORCA binary directory: {self.orca_binary_dir}"
            )
        elif orca_binary := shutil.which("orca"):
            self.orca_binary_dir = Path(orca_binary).parent.resolve()
            logger.debug(f"Found ORCA in PATH: {self.orca_binary_dir}")
        else:
            logger.error("ORCA binary not found")
            raise ValueError("ORCA binary not found.")

        # Set scratch directory
        if scratch:
            self.scratch = Path(scratch)
            logger.debug(f"Scratch directory set to: {self.scratch}")
        elif env_scratch := os.getenv("SCRATCH"):
            self.scratch = Path(env_scratch)
            logger.debug(f"Scratch directory set from $SCRATCH to: {self.scratch}")
        else:
            self.scratch = Path("/tmp")
            logger.debug(f"Scratch directory set to default directory: {self.scratch}")

        self.executable = self.orca_binary_dir / "orca"
        logger.debug(f"Scratch directory set to: {self.scratch}")
        logger.debug(f"ORCA executable: {self.executable}")

    def run(self, calculation, keep_scratch: bool = False) -> bool:
        """Run an ORCA calculation."""
        # Initialize the calculation
        calculation.setup(cpus=self.cpus, mem_per_cpu_gb=self.mem_per_cpu_gb)

        # Prepare scratch directory
        uuid = str(uuid4())[:8]
        scratch_dir: Path = (self.scratch / f"{calculation.name}_{uuid}").resolve()
        if scratch_dir.exists():
            logger.info(f"Purging existing scratch directory: {scratch_dir}")
            shutil.rmtree(scratch_dir)
        scratch_dir.mkdir(parents=True)
        logger.debug(f"Created scratch directory: {scratch_dir}")
        for f in calculation.source_dir.iterdir():
            shutil.copy(f, scratch_dir)
            logger.debug(f"Copied {f} to scratch directory")

        logger.info(f"Working in scratch directory: {scratch_dir}")

        # Run ORCA
        cmd = [self.executable, scratch_dir / calculation.input_file.name]
        logger.info(f"Running '{calculation.name}'")
        logger.debug(f"Running '{calculation.name}': {' '.join(map(str, cmd))}")

        success = False
        try:
            result = subprocess.run(
                cmd,
                cwd=scratch_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Write output to file
            calculation.output_file.write_text(result.stdout)
            logger.debug(f"Wrote output to {calculation.output_file}")

            # Log stderr if there was any
            if result.stderr:
                logger.warning(f"STDERR from ORCA:\n{result.stderr}")

            # Check if calculation completed successfully
            if calculation.check_output():
                logger.info("ORCA calculation successful")
                success = True
            else:
                logger.warning("ORCA calculation was not successful")
                success = False

        except Exception as e:
            logger.error(f"Error running ORCA calculation: {e}", exc_info=True)
            success = False

        # Copy files back from the scratch_dir to the source_dir
        logger.info(f"Copying results from {scratch_dir} to {calculation.source_dir}")
        shutil.copytree(scratch_dir, calculation.source_dir, dirs_exist_ok=True)

        if not keep_scratch:
            shutil.rmtree(scratch_dir)
            logger.info(f"Removed {scratch_dir}")

        return success
