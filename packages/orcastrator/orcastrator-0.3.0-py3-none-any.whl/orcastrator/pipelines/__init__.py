from typing import Dict, Type, Any

from orcastrator.pipelines.base import Pipeline
from orcastrator.pipelines.opt_freq_sp import OptFreqSinglePoint

# Registry of available pipeline types
_PIPELINE_REGISTRY: Dict[str, Type[Pipeline]] = {
    "OptFreqSinglePoint": OptFreqSinglePoint,
}

def register_pipeline(name: str, pipeline_class: Type[Pipeline]) -> None:
    """Register a pipeline class by name."""
    _PIPELINE_REGISTRY[name] = pipeline_class

def get_pipeline(name: str) -> Type[Pipeline]:
    """Get a pipeline class by name."""
    if name not in _PIPELINE_REGISTRY:
        raise ValueError(f"Unknown pipeline type: '{name}'. Available types: {list(_PIPELINE_REGISTRY.keys())}")
    return _PIPELINE_REGISTRY[name]

def get_available_pipelines() -> list[str]:
    """Get a list of all registered pipeline names."""
    return list(_PIPELINE_REGISTRY.keys())

__all__ = [
    "Pipeline",
    "OptFreqSinglePoint",
    "register_pipeline",
    "get_pipeline",
    "get_available_pipelines",
]
