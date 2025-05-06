"""Pre-defined SLURM templates for common HPC environments and ORCA versions."""

from typing import Dict, Any

# Template presets for different HPC environments
TEMPLATES = {
    "apollo_orca_6_0_1": {
        "environment_vars": {
            "OPENMPI": '"/soft/openmpi/openmpi-4.1.6"',
            "ORCA": '"/soft/orca/orca_6_0_1_linux_x86-64_shared_openmpi416_avx2"',
            "PATH": '"$ORCA:$OPENMPI/bin:$PATH"',
            "LD_LIBRARY_PATH": '"$ORCA/lib:$OPENMPI/lib64:$LD_LIBRARY_PATH"',
            "DYLD_LIBRARY_PATH": '"$LD_LIBRARY_PATH"',
            "SCRATCH": '"/scratch/$USER/$SLURM_JOB_ID"'
        },
    },
    "apollo_orca_5_0_4": {
        "environment_vars": {
            "OPENMPI": '"/soft/openmpi/openmpi-4.1.1"',
            "ORCA": '"/soft/orca/orca_5_0_4_linux_x86-64_shared_openmpi411"',
            "PATH": '"$ORCA:$OPENMPI/bin:$PATH"',
            "LD_LIBRARY_PATH": '"$ORCA/lib:$OPENMPI/lib64:$LD_LIBRARY_PATH"',
            "DYLD_LIBRARY_PATH": '"$LD_LIBRARY_PATH"',
            "SCRATCH": '"/scratch/$USER/$SLURM_JOB_ID"'
        },
    },
}

def get_template(name: str) -> Dict[str, Any]:
    """Retrieve a named template configuration."""
    if name not in TEMPLATES:
        raise ValueError(f"Unknown template: {name}. Available templates: {list(TEMPLATES.keys())}")
    return TEMPLATES[name].copy()
