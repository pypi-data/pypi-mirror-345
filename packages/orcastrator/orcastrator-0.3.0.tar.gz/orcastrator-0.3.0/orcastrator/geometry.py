from pathlib import Path

from orcastrator.logger import logger


class Geometry:
    """Dataclass to represent a geometry with a charge and a multiplicity."""

    def __init__(self, charge: int, mult: int, atoms: list[str]) -> None:
        logger.debug(
            "Initializing Geometry with charge=%d, mult=%d, atoms=%s",
            charge,
            mult,
            atoms,
        )
        self.charge: int = charge
        self.mult: int = mult
        tokens = [a.split() for a in atoms]
        self.atoms: list[str] = [
            f"{s:4}    {float(x):>8.4f}    {float(y):>8.4f}    {float(z):>8.4f}"
            for s, x, y, z in tokens
        ]
        logger.debug("Geometry initialized with formatted atoms: %s", self.atoms)

    def __str__(self) -> str:
        atom_lines = '\n'.join(self.atoms)
        geometry_str = f"* XYZ {self.charge} {self.mult}\n{atom_lines}\n*"
        logger.debug("Converting Geometry to string: %s", geometry_str)
        return geometry_str

    @classmethod
    def from_xyz_file(cls, charge: int, mult: int, xyz_file: str | Path) -> "Geometry":
        logger.debug(
            "Creating Geometry from XYZ file: %s with charge=%d, mult=%d",
            xyz_file,
            charge,
            mult,
        )
        lines = Path(xyz_file).read_text().splitlines()
        logger.debug("Read %d lines from XYZ file: %s", len(lines), xyz_file)
        geometry = cls(charge, mult, lines[2:])
        logger.debug("Geometry created from XYZ file: %s", geometry)
        return geometry
