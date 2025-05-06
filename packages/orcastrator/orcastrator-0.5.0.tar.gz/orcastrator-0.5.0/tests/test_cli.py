import shutil
from pathlib import Path

from click.testing import CliRunner

from orcastrator.cli import cli


def test_cli():
    config_file = Path("tests/test_config.toml")
    test_files = config_file.parent / "test_cli_calculations"
    runner = CliRunner()
    result = runner.invoke(cli, ["run", str(config_file)])
    assert (
        "FINAL SINGLE POINT ENERGY        -1.172971839688"
        in (test_files / "sp/sp.out").read_text()
    )
    shutil.rmtree(test_files)
