orcastrator
===========

chain orca calculations together to build complex
quantum chemistry pipelines.


Usage
-----

```py
configure_logging(level=logging.DEBUG)

logger.info("Starting calculation")
opt = Calculation(
    name="opt",
    root_dir=Path("/Users/freddy/Documents/Projects/orcastrator/test/no_fac"),
    level_of_theory="! OPT D4 TPSS def2-SVP",
    charge=0,
    mult=1,
    xyz_string=Path(
        "/Users/freddy/Documents/Projects/orcastrator/test/opt_freq.xyz"
    ).read_text(),
    aux_files=[
        Path(
            "/Users/freddy/Documents/Projects/orcastrator/test/asdf/test_sp/test_sp.densitiesinfo"
        ),
        Path("/Users/freddy/Documents/Projects/orcastrator/README.md"),
    ],
    overwrite=True,
)
opt_result: OrcaOutput = opt.run()
print(opt_result.directory)

sp = Calculation(
    name="sp",
    root_dir=opt.root_dir,
    level_of_theory="! D4 TPSSh def2-TZVP",
    charge=opt.charge,
    mult=opt.mult,
    xyz_string=opt_result.geometry,
    overwrite=True,
)
sp.run()
```


Design
------

A single executable that runs all calculations itself.
This means that the orcastrator run has to be submitted to SLURM by itself.

Calculation objects compose with an instance of a QCEngine class,
which implements a `run()` method takes consumes a Calculation object and return its results (or smth).

What does a Calculation need?
I'll focus on pure ORCA calculations, because I don't really use anything else anyway.
The QCEngine is still a good idea because e.g. there are different ORCA versions etc.
Alternatively, the Calculation is just a directory, containing at least an input file.

How can i represent the directory tree of the calculations?
I think the orcastrator should probably consume its own toml input file.


How might that look?

```toml
xyz_file = "guess.xyz"
charge = 0
mult = 1

[opt_freq]
input = """
! OPT FREQ
! D4 TPSS def2/TZVP

* XYZFILE $charge $mult $xyz_file
"""

[tddft]
input = """
! D4 TPSSh def2/TZVP

%TDDFT
    NROOTS 16
END

* XYZFILE $charge $mult $opt_freq.xyz_file
"""
```

hmm.. maybe it's better to create everything programmatically.

```py
opt_freq_template = """
! OPT FREQ ...

* XYZFILE $charge $mult $xyz_file
"""
tddft_template = """
! D4 TPSSh ...

* XYZFILE $charge $mult $xyz_file
"""

settings = dict(
    charge=0,
    mult=1,
    xyz_file="guess.xyz"
    engine=OrcaEngine(version="6.0.1", scratch="/scratch")
)

opt_freq = Calculation(input_template=opt_freq_template, settings)
tddft = Calculation(input_template=tddft_template, settings)

opt_freq.run()

tddft.xyz_file = opt_freq.files.optimized_xyz_file
tddft.run()
```
