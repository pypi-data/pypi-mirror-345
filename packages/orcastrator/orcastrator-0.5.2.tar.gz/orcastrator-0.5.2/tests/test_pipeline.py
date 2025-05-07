import shutil
from pathlib import Path

import pytest

from orcastrator.calculation import Calculation
from orcastrator.pipelines import run_opt_freq_sp


def test_new_pipeline():
    temp_dir = Path("/tmp/opt_freq_sp")
    try:
        run_opt_freq_sp(
            parent_dir=temp_dir,
            charge=0,
            mult=1,
            xyz_file=Path("tests/assets/h2.xyz"),
            keywords=[["D4", "TPSS", "def2-SVP"], ["D4", "TPSSh", "def2-TZVP"]],
            scratch_base_dir=temp_dir / "scratch",
        )
    finally:
        shutil.rmtree(temp_dir)


def test_opt_freq_sp_pipeline():
    temp_dir = Path("/tmp/opt_freq_sp")
    try:
        opt = Calculation(
            name="opt",
            parent_dir=temp_dir,
            charge=0,
            mult=1,
            atoms=[("H", 0, 0, 0), ("H", 0, 0, 1)],
            keywords=["OPT", "TPSS", "def2-SVP"],
            scratch_base_dir=temp_dir / "scratch",
            overwrite=True,
            keep_scratch=False,
        )
        opt.run()

        freq = opt.create_follow_up(
            "freq", additional_keywords=["FREQ"], remove_keywords=["OPT"]
        )
        freq.run()

        sp = freq.create_follow_up(
            "sp", additional_keywords=["TPSSh"], remove_keywords=["FREQ", "TPSS"]
        )
        sp.add_block("%TDDFT NROOTS 2 END")
        sp.run()

        assert freq.data.gibbs_free_energy_eh == pytest.approx(-1.1780214)
        assert sp.data.fspe_eh == pytest.approx(-194.838897072667)
    finally:
        shutil.rmtree(temp_dir)
