from pathlib import Path

from orcastrator.calculation import Calculation


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
    if len(keywords) == 2:
        keywords.insert(0, keywords[0])

    opt_kws, freq_kws, sp_kws = keywords

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
    opt.run()

    freq = opt.create_follow_up("freq", set_all_keywords=freq_kws)
    freq.add_keyword("FREQ")
    freq.run()

    sp = freq.create_follow_up("sp", set_all_keywords=sp_kws)
    sp.run()
