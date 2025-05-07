import logging
from pathlib import Path

from orcastrator.calculation import Calculation

# Get logger for this module
logger = logging.getLogger("orcastrator.pipelines")


def run_opt_freq_sp(
    parent_dir: str | Path,
    charge: int,
    mult: int,
    xyz_file: str | Path,
    keywords: list[list[str]],
    scratch_base_dir: str | Path,
    cpus: int = 1,
    mem_per_cpu_gb: int = 1,
    overwrite: bool = False,
    keep_scratch: bool = False,
):
    logger.info("Starting optimization-frequency-single point calculation pipeline")
    logger.debug(
        f"Pipeline parameters: parent_dir={parent_dir}, charge={charge}, mult={mult}"
    )
    logger.debug(f"XYZ file: {xyz_file}")
    logger.debug(f"Keywords for steps: {keywords}")

    if len(keywords) == 2:
        logger.info("Only 2 keyword sets provided, duplicating first set")
        keywords.insert(0, keywords[0])

    opt_kws, freq_kws, sp_kws = keywords
    logger.debug(f"Optimization keywords: {opt_kws}")
    logger.debug(f"Frequency keywords: {freq_kws}")
    logger.debug(f"Single point keywords: {sp_kws}")

    logger.info("Setting up optimization calculation")
    opt = Calculation(
        name="opt",
        parent_dir=Path(parent_dir),
        charge=charge,
        mult=mult,
        atoms=[],
        cpus=cpus,
        mem_per_cpu_gb=mem_per_cpu_gb,
        keywords=opt_kws,
        scratch_base_dir=Path(scratch_base_dir),
        overwrite=overwrite,
        keep_scratch=keep_scratch,
    )
    opt.set_atoms_from_xyz_file(Path(xyz_file))
    opt.add_keyword("OPT")
    logger.info("Running optimization calculation")
    opt.run()

    logger.info("Setting up frequency calculation")
    freq = opt.create_follow_up("freq", set_all_keywords=freq_kws)
    freq.add_keyword("FREQ")
    logger.info("Running frequency calculation")
    freq.run()

    logger.info("Setting up single point calculation")
    sp = freq.create_follow_up("sp", set_all_keywords=sp_kws)
    logger.info("Running single point calculation")
    sp.run()

    logger.info("Pipeline completed successfully")
