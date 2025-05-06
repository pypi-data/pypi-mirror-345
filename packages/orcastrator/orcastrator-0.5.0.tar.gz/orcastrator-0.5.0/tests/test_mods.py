import tempfile
from pathlib import Path

import pytest

from orcastrator.calculation import Calculation


@pytest.fixture
def basic_calculation():
    """Create a basic calculation for testing modifications."""
    return Calculation(
        name="test_calc",
        parent_dir=Path(tempfile.mkdtemp()),
        charge=0,
        mult=1,
        atoms=[("H", 0, 0, 0), ("H", 0, 0, 0.74)],
        keywords=["B3LYP", "def2-SVP"],
        blocks=["%scf maxiter 50 end", "%pal nprocs 2 end"],
    )


class TestKeywordModification:
    def test_add_keyword(self, basic_calculation):
        """Test adding a keyword."""
        calc = basic_calculation

        # Initial state
        assert "b3lyp" in calc.keywords
        assert "def2-svp" in calc.keywords
        assert "rijcosx" not in calc.keywords

        # Add a keyword
        result = calc.add_keyword("RIJCOSX")

        # Verify keyword was added and method returns self
        assert result is calc
        assert "rijcosx" in calc.keywords
        assert len(calc.keywords) == 3

    def test_add_existing_keyword(self, basic_calculation):
        """Test adding a keyword that already exists (different case)."""
        calc = basic_calculation

        # Add keyword that's already present (different case)
        calc.add_keyword("b3lyp")

        # Should not duplicate
        assert len(calc.keywords) == 2
        assert "b3lyp" in calc.keywords

    def test_remove_keyword(self, basic_calculation):
        """Test removing a keyword."""
        calc = basic_calculation

        # Initial state
        assert "b3lyp" in calc.keywords

        # Remove a keyword
        result = calc.remove_keyword("B3LYP")

        # Verify keyword was removed and method returns self
        assert result is calc
        assert "b3lyp" not in calc.keywords
        assert len(calc.keywords) == 1

    def test_remove_nonexistent_keyword(self, basic_calculation):
        """Test removing a keyword that doesn't exist."""
        calc = basic_calculation

        # Initial state
        assert "mp2" not in calc.keywords

        # Should raise KeyError
        with pytest.raises(KeyError):
            calc.remove_keyword("MP2")


class TestBlockModification:
    def test_add_block(self, basic_calculation):
        """Test adding a block."""
        calc = basic_calculation

        # Initial state
        assert len(calc.blocks) == 2
        assert "%scf maxiter 50 end" in calc.blocks

        # Add a block
        result = calc.add_block("%tddft nroots 10 end")

        # Verify block was added and method returns self
        assert result is calc
        assert "%tddft nroots 10 end" in calc.blocks
        assert len(calc.blocks) == 3

    def test_add_block_case_handling(self, basic_calculation):
        """Test that adding a block converts to lowercase."""
        calc = basic_calculation

        # Add a block with mixed case
        calc.add_block("%TDDFT nRoOtS 10 END")

        # Verify it was converted to lowercase
        assert "%tddft nroots 10 end" in calc.blocks

    def test_remove_block_by_prefix(self, basic_calculation):
        """Test removing a block by its prefix."""
        calc = basic_calculation

        # Initial state
        assert any(block.startswith("%scf") for block in calc.blocks)

        # Remove a block
        result = calc.remove_block("%scf")

        # Verify block was removed and method returns self
        assert result is calc
        assert not any(block.startswith("%scf") for block in calc.blocks)
        assert len(calc.blocks) == 1

    def test_remove_nonexistent_block(self, basic_calculation):
        """Test removing a block prefix that doesn't exist."""
        calc = basic_calculation

        # Initial state
        assert not any(block.startswith("%cosmo") for block in calc.blocks)

        # Should not error, but also not change anything
        calc.remove_block("%cosmo")
        assert len(calc.blocks) == 2


class TestMethodChaining:
    def test_comprehensive_chaining(self, basic_calculation):
        """Test a comprehensive chaining of methods."""
        calc = basic_calculation

        result = (
            calc.add_keyword("RIJCOSX")
            .remove_keyword("B3LYP")
            .add_keyword("TPSSh")
            .add_block("%cosmo epsilon 78.39 end")
            .remove_block("%pal")
            .add_block("%scf convergence tight end")
        )

        # Verify all changes were applied correctly
        assert result is calc  # Method chaining works

        # Check keywords
        assert "rijcosx" in calc.keywords
        assert "b3lyp" not in calc.keywords
        assert "tpssh" in calc.keywords
        assert "def2-svp" in calc.keywords

        # Check blocks
        assert "%cosmo epsilon 78.39 end" in calc.blocks
        assert not any(block.startswith("%pal") for block in calc.blocks)
        assert any(block.startswith("%scf") for block in calc.blocks)
        assert "%scf convergence tight end" in calc.blocks

    def test_input_generation_after_modifications(self, basic_calculation):
        """Test that modifications appear in generated input."""
        calc = basic_calculation

        # Apply a series of modifications
        calc.add_keyword("RIJCOSX").remove_keyword("B3LYP").add_keyword("TPSSh")
        calc.add_block("%cosmo epsilon 78.39 end")

        # Generate input
        input_content = calc._generate_input_string()

        # Verify content reflects all modifications
        assert "! def2-svp rijcosx tpssh" in input_content.lower()
        assert "b3lyp" not in input_content.lower()
        assert "%cosmo epsilon 78.39 end" in input_content.lower()
