from pathlib import Path
from typing import Self

from orcastrator.geometry import Geometry
from orcastrator.logger import logger


class LevelOfTheory:
    """Represent an ORCA calculation input.

    Instanciate and then populate the attributes, or construct from an input file
    with `LevelOfTheory().read_file(file)`

    Supports keywords, blocks, and the geometry.

    - `keywords`: list[str] = A list of plain ORCA keywords
    - `blocks`: dict = A dict with names and the *full* block string (e.g. "pal": "%pal nprocs 8 end")
    - `geometry`: Geometry = A custom class that holds the charge, mult, and the xyz coordinates
    """

    def __init__(self) -> None:
        self.keywords: set[str] = set()
        self.blocks: dict = {}
        self.input: str = ""
        self.charge: int = 0
        self.mult: int = 1
        self.geometry: Geometry | None = None

    def __str__(self) -> str:
        keywords = " ".join(sorted(self.keywords))
        blocks = "\n".join(self.blocks.values())
        return f"! {keywords}\n{blocks}\n{self.geometry}".lower()

    def write_to(self, file: str | Path) -> Path:
        """Create the specified file and write the ORCA input to it"""
        file = Path(file)
        file.write_text(f"{self}")
        logger.info(f"ORCA input written to file: {file}")
        return file

    def add_keyword(self, kw: str) -> Self:
        """Add one or more ORCA keywords"""
        self.keywords.add(kw.lower())
        logger.debug(f"Added keyword: {kw.lower()}")
        return self

    def add_keywords(self, *kw: str) -> Self:
        """Add one or more ORCA keywords"""
        self.keywords.update([k.lower() for k in kw])
        logger.debug(f"Added keywords: {[k.lower() for k in kw]}")
        return self

    def set_geometry(self, geom: Geometry) -> Self:
        self.geometry = geom
        return self

    def set_geometry_from_file(self, xyz_file: str | Path) -> Self:
        self.geometry = Geometry.from_xyz_file(
            charge=self.charge, mult=self.mult, xyz_file=xyz_file
        )
        return self

    def read_input(self, input: str) -> Self:
        """Parse and ORCA-like input string.

        E.g. "! D4 TPSS def2-TZVP\n %TDDFT NROOTS 8 END"
        """
        self.__init__()
        self.input = input
        lines = [line.strip() for line in self.input.splitlines()]

        for i, line in enumerate(lines):
            # keywords
            if line.startswith("!"):
                keywords = line.strip("!").split()
                logger.debug(f"Parsed keywords: {keywords}")
                self.add_keywords(*keywords)

            # blocks
            if line.startswith("%"):
                # Isolate block lines
                block_lines = []
                block_start_idx = i
                key = line.strip().lstrip("%").split()[0]  # Get the block type (pal, etc)

                # Collect lines until we find "end"
                for j in range(i, len(lines)):
                    block_lines.append(lines[j])
                    if lines[j].strip().lower() == "end":
                        i = j  # Update the outer loop index
                        break

                self.blocks[key] = "\n".join(block_lines)
                logger.debug(f"Parsed block: {key}")

            # geometry
            if line.startswith("*") and not self.geometry:
                tokens = line.strip("*").split()
                if not tokens:
                    logger.error("Line is empty or only contains asterisks.")
                    raise ValueError("Line is empty or only contains asterisks.")

                geom_type = tokens[0].lower()
                logger.debug(f"Parsing geometry type: {geom_type}")

                if geom_type == "xyzfile":
                    _, charge, mult, xyz_file = tokens
                    xyz_file_path = self.file.parent / xyz_file
                    if not xyz_file_path.exists():
                        logger.error(f"XYZ file not found: {xyz_file_path}")
                        raise FileNotFoundError(f"XYZ file not found: {xyz_file_path}")
                    atoms = xyz_file_path.read_text().splitlines()[2:]
                    logger.info(f"Read geometry from XYZ file: {xyz_file_path}")
                elif geom_type == "xyz":
                    _, charge, mult = tokens
                    atoms = lines[i + 1 : -1]
                    logger.info("Read inline XYZ geometry.")
                else:
                    logger.error(f"Unknown geometry type: {geom_type}")
                    raise ValueError(f"Unknown geometry type: {geom_type}")

                self.geometry = Geometry(int(charge), int(mult), atoms)
                logger.debug(
                    f"Geometry set with charge={charge}, mult={mult}, atoms={len(atoms)}"
                )

        if len(self.keywords) == 0:
            raise ValueError(f"No keywords parsed from {input}!")
        return self

    def read_file(self, file: str | Path) -> Self:
        # Clear state
        self.__init__()
        self.file = Path(file)
        logger.info(f"Reading ORCA input file: {file}")
        self.input = self.file.read_text()
        return self
