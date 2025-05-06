import pytest
from pathlib import Path
import tempfile
import shutil
import tomllib as toml

from orcastrator.pipelines import get_pipeline, get_available_pipelines
from orcastrator.pipelines.base import Pipeline


@pytest.fixture
def test_dir():
    """Create a temporary directory for tests."""
    tmp_dir = Path(tempfile.mkdtemp())
    yield tmp_dir
    shutil.rmtree(tmp_dir)


@pytest.fixture
def sample_config(test_dir):
    """Create a sample config file."""
    xyz_content = """2

H 0 0 0
H 0 0 1
"""

    # Create an XYZ file
    xyz_file = test_dir / "h2.xyz"
    xyz_file.write_text(xyz_content)

    # Create a config file
    config_content = f"""
[pipeline]
name = "test_pipeline"
directory = "{test_dir}/calculations"
type = "OptFreqSinglePoint"
lots = ["! PBE def2-SVP", "! PBE def2-TZVP"]
overwrite = true
log_level = "info"

[geometry]
charge = 0
mult = 1
xyz_file = "{xyz_file}"

[slurm]
job_name = "test_job"
time_h = 1
cpus = 2
mem_per_cpu_gb = 1
"""

    config_file = test_dir / "test_config.toml"
    config_file.write_text(config_content)

    return config_file


def test_pipeline_registration():
    """Test that pipeline registration works correctly."""
    pipelines = get_available_pipelines()
    assert "OptFreqSinglePoint" in pipelines

    # Get a pipeline class
    pipeline_class = get_pipeline("OptFreqSinglePoint")
    assert pipeline_class.__name__ == "OptFreqSinglePoint"


def test_pipeline_from_toml(sample_config):
    """Test loading a pipeline from a TOML file."""
    pipeline = Pipeline.from_toml(sample_config)

    # Check basic attributes
    assert pipeline.name == "test_pipeline"
    assert pipeline.directory.name == "calculations"
    assert pipeline.overwrite is True

    # Check that slurm config was loaded
    assert pipeline.slurm_config["job_name"] == "test_job"
    assert pipeline.slurm_config["cpus"] == 2

    # Check levels of theory
    # Since we're testing OptFreqSinglePoint, we should have 3 levels of theory
    # (the third is duplicated from the first when only two are provided)
    assert "pbe" in pipeline.lots[0].keywords       # type: ignore
    assert "def2-svp" in pipeline.lots[0].keywords  # type: ignore
    assert "pbe" in pipeline.lots[1].keywords       # type: ignore
    assert "def2-svp" in pipeline.lots[1].keywords  # type: ignore
    assert "pbe" in pipeline.lots[2].keywords       # type: ignore
    assert "def2-tzvp" in pipeline.lots[2].keywords # type: ignore


def test_slurm_script_creation(sample_config, test_dir):
    """Test creating a SLURM script from a pipeline."""
    pipeline = Pipeline.from_toml(sample_config)

    slurm_file = test_dir / "test_job.slurm"
    script_path = pipeline.create_slurm_script(slurm_file)

    assert script_path.exists()
    content = script_path.read_text()

    # Check for basic SLURM directives
    assert "#SBATCH --job-name=test_job" in content
    assert "#SBATCH --cpus-per-task=2" in content
    assert "#SBATCH --time=1" in content
    assert "#SBATCH --mem-per-cpu=1GB" in content

    # Check for pipeline execution command
    assert "orcastrator.pipeline_runner" in content
