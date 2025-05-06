import shutil
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional, Self
from uuid import uuid4

from morca import OrcaOutput


@dataclass
class Calculation:
    name: str
    parent_dir: Path

    # Geometry
    charge: int
    mult: int
    atoms: list[tuple[str, float, float, float]]

    # Level of theory
    keywords: str | list[str] | set[str]
    blocks: list[str] = field(default_factory=list)

    # Technical
    cpus: int = 1
    mem_per_cpu_gb: Optional[int] = None
    scratch_base_dir: Optional[Path] = None

    # Behaviour
    overwrite: bool = False
    keep_scratch: bool = False

    def __post_init__(self):
        """Ensure keywords and blocks are always lowercase."""
        # Handle different input types for keywords
        if isinstance(self.keywords, str):
            # Split space-separated string into individual keywords
            self.keywords = set(self.keywords.split())
        elif isinstance(self.keywords, list):
            # Convert list to set
            self.keywords = set(self.keywords)
        # If it's already a set, no conversion needed

        # Convert keywords to lowercase
        self.keywords = {kw.lower() for kw in self.keywords}

        # Convert blocks to lowercase
        self.blocks = [block.lower() for block in self.blocks]

    @property
    def directory(self) -> Path:
        return self.parent_dir / self.name

    @property
    def input_file(self) -> Path:
        return self.directory / f"{self.name}.inp"

    @property
    def output_file(self) -> Path:
        return self.input_file.with_suffix(".out")

    @property
    def xyz_file(self) -> Path:
        return self.input_file.with_suffix(".xyz")

    @property
    def data(self) -> OrcaOutput:
        return OrcaOutput(self.output_file)

    def set_atoms_from_xyz_file(self, xyz_file: Path) -> Self:
        lines = Path(xyz_file).read_text().splitlines()
        new_atoms = []
        for line in lines[2:]:
            symbol, x, y, z = line.split()
            new_atoms.append((symbol, float(x), float(y), float(z)))
        self.atoms = new_atoms
        return self

    def _format_geometry_input_string(self) -> str:
        """Formats the atoms into the ORCA * xyz block."""
        atom_lines = [
            f" {s:4}    {x:>12.8f}    {y:>12.8f}    {z:>12.8f}"
            for s, x, y, z in self.atoms
        ]
        return f"* xyz {self.charge} {self.mult}\n" + "\n".join(atom_lines) + "\n*"

    def _generate_input_string(self) -> str:
        """Constructs the full ORCA input file content."""
        # Start with keywords
        input_lines = [f"! {' '.join(sorted(self.keywords))}"]

        # Add resource blocks (don't permanently store them in self.blocks)
        temp_blocks = self.blocks.copy()
        if self.cpus > 1:
            temp_blocks.append(f"%pal nprocs {self.cpus} end")
        if self.mem_per_cpu_gb:
            # ORCA uses total memory in MB per core for %maxcore
            total_mem_mb = self.mem_per_cpu_gb * 1000  # Approximate GB to MB
            temp_blocks.append(f"%maxcore {total_mem_mb}")

        # Add other defined blocks
        input_lines.extend(temp_blocks)

        # Add geometry
        input_lines.append(self._format_geometry_input_string())

        return "\n".join(input_lines)  # ORCA often prefers lowercase

    def write_input_file(self) -> Path:
        """Generates and writes the ORCA input file."""
        if not self.keywords:
            raise ValueError("Cannot write input file: No keywords defined.")
        if not self.atoms:
            raise ValueError("Cannot write input file: No atoms defined.")

        input_content = self._generate_input_string()
        self.setup_directory()
        self.input_file.write_text(input_content)
        return self.input_file

    def setup_directory(self) -> None:
        """Creates the source directory, handling overwrites."""
        if self.directory.exists():
            if self.overwrite:
                shutil.rmtree(self.directory)
            else:
                raise IsADirectoryError(
                    f"Directory {self.directory} already exists and overwrite=False"
                )
        self.directory.mkdir(parents=True)

    @contextmanager
    def _scratch_directory(self) -> Iterator[Path]:
        """
        Context manager for handling the scratch directory lifecycle.
        Creates a scratch directory, yields it, and cleans it up afterwards.
        """
        run_id = str(uuid4())[:8]
        base_dir = self.scratch_base_dir or self.directory / "scratch"
        scratch_run_dir = (base_dir / f"{self.name}_{run_id}").resolve()

        try:
            # Setup scratch directory
            if scratch_run_dir.exists():
                shutil.rmtree(scratch_run_dir)

            scratch_run_dir.mkdir(parents=True, exist_ok=True)

            # Copy input file to scratch
            shutil.copy(self.input_file, scratch_run_dir)

            # Yield the scratch directory for use in the run method
            yield scratch_run_dir

        finally:
            # Clean up scratch directory
            if not self.keep_scratch and scratch_run_dir.exists():
                try:
                    shutil.rmtree(scratch_run_dir)
                except OSError as e:
                    print(e)

    def run(self) -> bool:
        orca_bin = shutil.which("orca")
        if orca_bin is None:
            raise RuntimeError("ORCA executable not found")
        orca_bin = Path(orca_bin).resolve()

        self.write_input_file()
        with self._scratch_directory() as scratch_dir:
            cmd = [str(orca_bin), self.input_file.name]  # Run relative to scratch dir

            result = subprocess.run(
                cmd,
                cwd=scratch_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,  # Don't raise exception on non-zero exit code
            )

            self.output_file.write_text(result.stdout)
            shutil.copytree(scratch_dir, self.directory, dirs_exist_ok=True)

        is_normal = "****ORCA TERMINATED NORMALLY****" in self.output_file.read_text()
        return is_normal

    def set_keywords(self, kws: list[str] | set[str]) -> Self:
        self.keywords = set(kws)
        return self

    def add_keyword(self, kw: str) -> Self:
        self.keywords = set(self.keywords)
        self.keywords.add(kw.lower())
        return self

    def add_block(self, block: str) -> Self:
        self.blocks.append(block.lower())
        return self

    def remove_keyword(self, kw: str) -> Self:
        self.keywords = set(self.keywords)
        self.keywords.remove(kw.lower())
        return self

    def remove_block(self, block_kw: str) -> Self:
        self.blocks = [b for b in self.blocks if not b.startswith(block_kw.lower())]
        return self

    def create_follow_up(
        self,
        name: str,
        set_all_keywords: Optional[list[str] | set[str]] = None,
        additional_keywords: Optional[list[str] | set[str]] = None,
        remove_keywords: Optional[list[str] | set[str]] = None,
        add_blocks: Optional[list[str]] = None,
        remove_blocks: Optional[list[str]] = None,
    ) -> "Calculation":
        """Create a follow-up calculation using the optimized geometry from this one."""
        if not self.output_file.exists():
            raise FileNotFoundError(
                f"Cannot create follow-up: No output file found at {self.output_file}"
            )

        new_calc = Calculation(
            name=name,
            keywords=self.keywords,
            parent_dir=self.parent_dir,
            charge=self.charge,
            mult=self.mult,
            atoms=self.atoms,
            blocks=self.blocks.copy(),
            cpus=self.cpus,
            mem_per_cpu_gb=self.mem_per_cpu_gb,
            scratch_base_dir=self.scratch_base_dir,
            overwrite=self.overwrite,
            keep_scratch=self.keep_scratch,
        )

        if additional_keywords:
            for kw in additional_keywords:
                new_calc.add_keyword(kw)
        if remove_keywords:
            for kw in remove_keywords:
                new_calc.remove_keyword(kw)
        if add_blocks:
            for block in add_blocks:
                new_calc.add_block(block)
        if remove_blocks:
            for block in remove_blocks:
                new_calc.remove_block(block)
        if set_all_keywords:
            new_calc.set_keywords(set_all_keywords)

        # Try to use optimized geometry if available
        try:
            new_calc.set_atoms_from_xyz_file(self.xyz_file)
        except FileNotFoundError:
            pass  # Use original geometry if no optimized one exists

        return new_calc
