import pytest
import tempfile
from pathlib import Path

from orcastrator.geometry import Geometry


def test_geometry_init():
    """Test initializing geometry directly."""
    geom = Geometry(
        charge=0,
        mult=1,
        atoms=["H  0.0  0.0  0.0", "H  0.0  0.0  1.0"]
    )

    assert geom.charge == 0
    assert geom.mult == 1
    assert len(geom.atoms) == 2

    # Check formatting
    assert "H         0.0000      0.0000      0.0000" == geom.atoms[0]
    assert "H         0.0000      0.0000      1.0000" == geom.atoms[1]


def test_geometry_string_representation():
    """Test string representation of geometry."""
    geom = Geometry(
        charge=1,
        mult=2,
        atoms=["H  0.0  0.0  0.0", "H  0.0  0.0  1.0"]
    )

    string_rep = str(geom)

    assert "* XYZ 1 2" in string_rep
    assert "H         0.0000      0.0000      0.0000" in string_rep
    assert "H         0.0000      0.0000      1.0000" in string_rep
    assert string_rep.endswith("*")


def test_geometry_from_xyz_file():
    """Test creating a geometry from an XYZ file."""
    # Create a temporary XYZ file
    xyz_content = """2
This is a comment line
H 0.0 0.0 0.0
H 0.0 0.0 1.0
"""

    with tempfile.NamedTemporaryFile(suffix='.xyz', mode='w+') as temp_file:
        temp_file.write(xyz_content)
        temp_file.flush()

        # Create geometry from the file
        geom = Geometry.from_xyz_file(charge=0, mult=1, xyz_file=temp_file.name)

        # Check that it loaded correctly
        assert geom.charge == 0
        assert geom.mult == 1
        assert len(geom.atoms) == 2
        assert "H         0.0000      0.0000      0.0000" == geom.atoms[0]
