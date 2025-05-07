import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from orcastrator.calculation import Calculation


# Fixtures
@pytest.fixture
def temp_dir():
    """Create a temporary directory for test calculations."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def h2_calculation(temp_dir):
    """Create a basic H2 calculation."""
    return Calculation(
        name="h2_test",
        parent_dir=temp_dir,
        charge=0,
        mult=1,
        atoms=[("H", 0, 0, 0), ("H", 0, 0, 0.74)],
        keywords=["B3LYP", "def2-SVP", "TightSCF"],
        cpus=2,
        mem_per_cpu_gb=1,
        overwrite=True,
    )


@pytest.fixture
def water_xyz_file(temp_dir):
    """Create a temporary XYZ file for water."""
    xyz_path = temp_dir / "water.xyz"
    xyz_content = """3
Water molecule
O    0.000000    0.000000    0.117790
H    0.000000    0.757160   -0.471160
H    0.000000   -0.757160   -0.471160
"""
    xyz_path.write_text(xyz_content)
    return xyz_path


# Tests for initialization and basic properties
class TestCalculationInit:
    def test_init_with_string_keywords(self, temp_dir):
        """Test initialization with space-separated string keywords."""
        calc = Calculation(
            name="test1",
            parent_dir=temp_dir,
            charge=0,
            mult=1,
            atoms=[("H", 0, 0, 0), ("H", 0, 0, 1)],
            keywords="B3LYP def2-SVP TightSCF",
        )
        assert calc.keywords == {"b3lyp", "def2-svp", "tightscf"}

    def test_init_with_list_keywords(self, temp_dir):
        """Test initialization with list keywords."""
        calc = Calculation(
            name="test2",
            parent_dir=temp_dir,
            charge=0,
            mult=1,
            atoms=[("H", 0, 0, 0), ("H", 0, 0, 1)],
            keywords=["B3LYP", "def2-SVP", "TightSCF"],
        )
        assert calc.keywords == {"b3lyp", "def2-svp", "tightscf"}

    def test_init_with_set_keywords(self, temp_dir):
        """Test initialization with set keywords."""
        calc = Calculation(
            name="test3",
            parent_dir=temp_dir,
            charge=0,
            mult=1,
            atoms=[("H", 0, 0, 0), ("H", 0, 0, 1)],
            keywords={"B3LYP", "def2-SVP", "TightSCF"},
        )
        assert calc.keywords == {"b3lyp", "def2-svp", "tightscf"}

    def test_path_properties(self, h2_calculation):
        """Test that path properties are correctly set."""
        calc = h2_calculation
        assert calc.directory == calc.parent_dir / calc.name
        assert calc.input_file == calc.directory / f"{calc.name}.inp"
        assert calc.output_file == calc.input_file.with_suffix(".out")
        assert calc.xyz_file == calc.input_file.with_suffix(".xyz")


# Tests for file operations
class TestCalculationFiles:
    def test_directory_setup(self, h2_calculation):
        """Test directory creation."""
        calc = h2_calculation
        calc.setup_directory()
        assert calc.directory.exists()
        assert calc.directory.is_dir()

    def test_directory_overwrite(self, h2_calculation):
        """Test directory overwrite behavior."""
        calc = h2_calculation
        # Create directory first time
        calc.setup_directory()
        # Should succeed with overwrite=True
        calc.setup_directory()

        # Test with overwrite=False
        calc.overwrite = False
        with pytest.raises(IsADirectoryError):
            calc.setup_directory()

    def test_input_file_generation(self, h2_calculation):
        """Test input file content generation."""
        calc = h2_calculation
        input_path = calc.write_input_file()

        # Check file exists
        assert input_path.exists()

        # Check content
        content = input_path.read_text()
        assert "! b3lyp def2-svp tightscf" in content
        assert "* xyz 0 1" in content
        assert "H         0.00000000      0.00000000      0.00000000" in content
        assert "H         0.00000000      0.00000000      0.74000000" in content
        assert "%pal nprocs 2 end" in content
        assert "%maxcore 1000" in content

    def test_input_file_validation(self, temp_dir):
        """Test validation for input file generation."""
        # Test with no keywords
        calc = Calculation(
            name="invalid1",
            parent_dir=temp_dir,
            charge=0,
            mult=1,
            atoms=[("H", 0, 0, 0), ("H", 0, 0, 1)],
            keywords=[],
        )
        with pytest.raises(ValueError, match="No keywords defined"):
            calc.write_input_file()

        # Test with no atoms
        calc = Calculation(
            name="invalid2",
            parent_dir=temp_dir,
            charge=0,
            mult=1,
            atoms=[],
            keywords=["B3LYP"],
        )
        with pytest.raises(ValueError, match="No atoms defined"):
            calc.write_input_file()

    def test_xyz_file_import(self, temp_dir, water_xyz_file):
        """Test importing geometry from XYZ file."""
        calc = Calculation(
            name="water_test",
            parent_dir=temp_dir,
            charge=0,
            mult=1,
            atoms=[],  # Empty initially
            keywords=["B3LYP"],
        )

        calc.set_atoms_from_xyz_file(water_xyz_file)

        # Check atoms were imported correctly
        assert len(calc.atoms) == 3
        assert calc.atoms[0][0] == "O"
        assert pytest.approx(calc.atoms[0][1]) == 0.0
        assert pytest.approx(calc.atoms[0][2]) == 0.0
        assert pytest.approx(calc.atoms[0][3]) == 0.11779


# Tests for execution
class TestCalculationExecution:
    @patch("subprocess.run")
    @patch("shutil.which")
    def test_successful_run(self, mock_which, mock_run, h2_calculation):
        """Test a successful calculation run."""
        mock_which.return_value = "/path/to/orca"

        # Mock successful ORCA termination
        process_mock = MagicMock()
        process_mock.stdout = (
            "Some output\n****ORCA TERMINATED NORMALLY****\nMore output"
        )
        mock_run.return_value = process_mock

        result = h2_calculation.run()

        # Check subprocess was called correctly
        mock_run.assert_called_once()
        assert result is True
        assert h2_calculation.output_file.exists()

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_failed_run(self, mock_which, mock_run, h2_calculation):
        """Test a failed calculation run."""
        mock_which.return_value = "/path/to/orca"

        # Mock failed ORCA termination
        process_mock = MagicMock()
        process_mock.stdout = (
            "Error output\nORCA ABNORMAL TERMINATION\nMore error output"
        )
        mock_run.return_value = process_mock

        result = h2_calculation.run()

        # Check subprocess was called correctly
        mock_run.assert_called_once()
        assert result is False
        assert h2_calculation.output_file.exists()

    @patch("shutil.which")
    def test_missing_orca_executable(self, mock_which, h2_calculation):
        """Test behavior when ORCA executable is not found."""
        mock_which.return_value = None

        with pytest.raises(RuntimeError, match="ORCA executable not found"):
            h2_calculation.run()


# Tests for follow-up calculations
class TestFollowUpCalculations:
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_create_followup(self, mock_read_text, mock_exists, h2_calculation):
        """Test creating a follow-up calculation."""
        # Make it seem like the output file exists
        mock_exists.return_value = True
        mock_read_text.return_value = "2\n\nH 0 0 0\nH 0 0 0.74"

        # Create a follow-up with modified keywords
        freq_calc = h2_calculation.create_follow_up(
            name="h2_freq", additional_keywords=["Freq"], remove_keywords=["TightSCF"]
        )

        # Check the new calculation's properties
        assert freq_calc.name == "h2_freq"
        assert freq_calc.parent_dir == h2_calculation.parent_dir
        assert "freq" in freq_calc.keywords
        assert "b3lyp" in freq_calc.keywords
        assert "tightscf" not in freq_calc.keywords
        assert freq_calc.charge == h2_calculation.charge
        assert freq_calc.mult == h2_calculation.mult
        assert freq_calc.atoms == h2_calculation.atoms

    def test_followup_requires_output(self, h2_calculation):
        """Test that creating a follow-up requires an output file."""
        # The output file shouldn't exist yet
        with pytest.raises(FileNotFoundError, match="No output file found"):
            h2_calculation.create_follow_up(name="h2_freq")


# Tests for method chaining
class TestMethodChaining:
    def test_keyword_and_block_chaining(self, h2_calculation):
        """Test method chaining for adding keywords and blocks."""
        result = (
            h2_calculation.add_keyword("RIJCOSX")
            .add_block("%scf maxiter 100 end")
            .add_keyword("Grid4")
        )

        # Verify the object was modified and returned itself
        assert result is h2_calculation
        assert "rijcosx" in h2_calculation.keywords
        assert "grid4" in h2_calculation.keywords
        assert "%scf maxiter 100 end" in h2_calculation.blocks
