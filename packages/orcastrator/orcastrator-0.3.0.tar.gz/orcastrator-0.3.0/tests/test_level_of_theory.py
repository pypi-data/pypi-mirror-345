import pytest
import tempfile
from pathlib import Path

from orcastrator.level_of_theory import LevelOfTheory
from orcastrator.geometry import Geometry


def test_level_of_theory_keywords():
    """Test adding keywords to a level of theory."""
    lot = LevelOfTheory()

    # Add individual keywords
    lot.add_keyword("PBE")
    lot.add_keyword("def2-SVP")

    assert "pbe" in lot.keywords
    assert "def2-svp" in lot.keywords

    # Add multiple keywords
    lot.add_keywords("TIGHTSCF", "GRID4")

    assert "tightscf" in lot.keywords
    assert "grid4" in lot.keywords


def test_level_of_theory_string_representation():
    """Test string representation of a level of theory."""
    lot = LevelOfTheory()
    lot.add_keywords("PBE", "def2-SVP", "GRID4")

    # Set a block
    lot.blocks["pal"] = "%pal nprocs 4 end"

    # Set geometry
    geom = Geometry(charge=0, mult=1, atoms=["H 0 0 0", "H 0 0 1"])
    lot.set_geometry(geom)

    string_rep = str(lot)

    assert "! def2-svp grid4 pbe" in string_rep.lower()  # keywords are sorted
    assert "%pal nprocs 4 end" in string_rep.lower()
    assert "* xyz 0 1" in string_rep.lower()


def test_level_of_theory_write_to_file():
    """Test writing a level of theory to a file."""
    lot = LevelOfTheory()
    lot.add_keywords("PBE", "def2-SVP")
    lot.blocks["pal"] = "%PAL NPROCS 4 END"

    # Set geometry
    geom = Geometry(charge=0, mult=1, atoms=["H 0 0 0", "H 0 0 1"])
    lot.set_geometry(geom)

    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = Path(tmp_dir) / "test.inp"
        lot.write_to(file_path)

        assert file_path.exists()
        content = file_path.read_text()

        assert "! def2-SVP PBE".lower() in content
        assert "%PAL NPROCS 4 END".lower() in content
        assert "* XYZ 0 1".lower() in content


def test_level_of_theory_read_input():
    """Test reading a level of theory from an input string."""
    input_str = """! PBE def2-SVP OPT
%pal
  nprocs 4
end

* xyz 0 1
H 0.0 0.0 0.0
H 0.0 0.0 1.0
*
"""

    lot = LevelOfTheory().read_input(input_str)

    assert "pbe" in lot.keywords
    assert "def2-svp" in lot.keywords
    assert "opt" in lot.keywords

    # Check that the block was parsed
    assert "pal" in lot.blocks

    # Check that geometry was set
    assert lot.geometry is not None
    assert lot.geometry.charge == 0
    assert lot.geometry.mult == 1
    assert len(lot.geometry.atoms) == 2
