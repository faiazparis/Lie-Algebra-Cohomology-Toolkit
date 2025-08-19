"""
Configuration management for the Spectral Lie Algebra Explorer.

This module handles loading, validation, and access to configuration settings
for the various components of the system.
"""

from dataclasses import dataclass
import yaml

@dataclass(frozen=True)
class Config:
    input: dict
    cohomology: dict
    spectral: dict
    physics: dict
    output: dict
    seed: int = 42

def load_config(path: str) -> Config:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    required = ["input", "cohomology", "spectral", "physics", "output"]
    for k in required:
        if k not in data:
            raise ValueError(f"Missing config section: {k}")
    return Config(**data)
