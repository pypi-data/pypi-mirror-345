import logging
import tomllib as toml
from pathlib import Path
from typing import Optional

from morca import OrcaOutput

from orcastrator import OrcaEngine, configure_logging, logger
from orcastrator.calculation import Calculation
from orcastrator.geometry import Geometry
from orcastrator.level_of_theory import LevelOfTheory

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


class OptFreqSinglePoint:
    def __init__(
        self,
        directory: Path,
        initial_geom: Geometry,
        lots: list[str],
        overwrite: bool = False,
        log_level: str = "info",
        log_file: Optional[str | Path] = None,
        engine=OrcaEngine(),
    ) -> None:
        """lots is a list of ORCA-like keywords, whitespace-separated.
        E.g. "lots = ["D4 TPSS def2-SVP", "D4 TPSSh def2-TZVP"]
        if only two LOTs are given, assumes an opt/freq, sp split
        """
        # Initialize logging
        self.directory = Path(directory)
        self.directory.mkdir(exist_ok=True)
        logger.info(f"Created {self.directory}")
        if log_file:
            if not Path(log_file).is_absolute():
                log_file = self.directory / log_file
        configure_logging(level=LOG_LEVELS[log_level], log_file=log_file)
        self.initial_geom = initial_geom
        if len(lots) == 2:
            lots = [lots[0], lots[0], lots[1]]
        elif len(lots) != 3:
            raise ValueError("Three levels of theory required")
        self.lots = [
            LevelOfTheory().read_input(lot).set_geometry(self.initial_geom)
            for lot in lots
        ]

        self.overwrite = overwrite
        self.engine = engine

    def run(self):
        logger.info("\n\n ------ OptFreqSinglePoint")
        opt = Calculation(
            name="opt",
            directory=self.directory,
            level_of_theory=self.lots[0].add_keyword("OPT"),
            overwrite=self.overwrite,
        )
        opt_out = opt.run(self.engine)
        opt_xyz_file = opt_out.with_suffix(".xyz")
        logger.info("--- OPT finished")

        freq = opt.copy_with(
            name="freq",
            level_of_theory=self.lots[1]
            .set_geometry_from_file(opt_xyz_file)
            .add_keyword("FREQ"),
        )
        freq_out = OrcaOutput(freq.run(self.engine))
        logger.info("--- FREQ finished")

        sp = freq.copy_with(name="sp", level_of_theory=self.lots[2])
        sp_out = OrcaOutput(sp.run(self.engine))
        logger.info("--- SP finished")

        print(
            f"Enthalpy: {freq_out.enthalpy_eh}\nGibbs free energy: {freq_out.gibbs_free_energy_eh}\n"
        )
        print(
            f"Corrected Gibbs free energy: {sp_out.fspe_eh + freq_out.gibbs_free_energy_correction_eh}\n"
        )

    @classmethod
    def from_toml(cls, file: str | Path) -> "OptFreqSinglePoint":
        file = Path(file)
        config = toml.loads(file.read_text())
        # validate
        if dir := config["pipeline"]["directory"]:
            dir = Path(dir)
            if not dir.is_absolute():
                dir = file.parent / dir
        else:
            raise ValueError("Missing pipeline directory")

        # Geometry
        charge = config["geometry"].get("charge")
        mult = config["geometry"].get("mult")
        if xyz_file := config["geometry"].get("xyz_file"):
            xyz_file = file.parent / xyz_file
        initial_geom = Geometry.from_xyz_file(charge, mult, xyz_file)

        # Log file
        if log_file_name := config["pipeline"].get("log_file"):
            log_file = (dir / log_file_name).resolve()
        else:
            log_file = None

        pipeline = cls(
            directory=dir,
            initial_geom=initial_geom,
            log_file=log_file,
            lots=config["pipeline"]["lots"],
            overwrite=config["pipeline"].get("overwrite", False),
        )
        return pipeline


# initial_geom = Geometry.from_xyz_file(charge=0, mult=1, xyz_file="test/h2.xyz")

# pipe = OptFreqSinglePoint(
#     directory=Path("test/scratch/pipeline_test"),
#     initial_geom=initial_geom,
#     lots=["D4 TPSS def2-SVP", "D4 TPSSh def2-TZVP"],
#     overwrite=True,
#     log_file="opt_freq_sp.log",
# )
# pipe.run()

pipe = OptFreqSinglePoint.from_toml("test/test_config.toml")
pipe.run()
