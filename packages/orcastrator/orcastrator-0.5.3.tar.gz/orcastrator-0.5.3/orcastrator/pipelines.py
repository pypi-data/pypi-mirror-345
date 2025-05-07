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
    blocks: list[list[str]] = [],
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

    # Ensure blocks has 3 elements
    while len(blocks) < 3:
        logger.info(f"Only {len(blocks)} block sets provided, adding empty set")
        blocks.append([])

    opt_kws, freq_kws, sp_kws = keywords
    opt_blks, freq_blks, sp_blks = blocks

    logger.debug(f"Optimization keywords: {opt_kws}")
    logger.debug(f"Optimization blocks: {opt_blks}")
    logger.debug(f"Frequency keywords: {freq_kws}")
    logger.debug(f"Frequency blocks: {freq_blks}")
    logger.debug(f"Single point keywords: {sp_kws}")
    logger.debug(f"Single point blocks: {sp_blks}")

    # Initialize blocks if None
    if blocks is None:
        blocks = [[], [], []]
    logger.debug(f"Blocks for steps: {blocks}")
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
        blocks=opt_blks,  # Add blocks to optimization calculation
        scratch_base_dir=Path(scratch_base_dir) if scratch_base_dir else None,
        overwrite=overwrite,
        keep_scratch=keep_scratch,
    )
    opt.set_atoms_from_xyz_file(Path(xyz_file))
    opt.add_keyword("OPT")
    logger.info("Running optimization calculation")
    opt.run()

    logger.info("Setting up frequency calculation")
    freq = opt.create_follow_up(
        "freq",
        set_all_keywords=freq_kws,
        set_blocks=freq_blks,  # Add blocks to frequency calculation
    )
    freq.add_keyword("FREQ")
    logger.info("Running frequency calculation")
    freq.run()

    logger.info("Setting up single point calculation")
    sp = freq.create_follow_up(
        "sp",
        set_all_keywords=sp_kws,
        set_blocks=sp_blks,  # Add blocks to single point calculation
    )
    logger.info("Running single point calculation")
    sp.run()

    logger.info("Pipeline completed successfully")
