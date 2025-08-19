"""
Registry for Lie algebra types and configurations.

This module provides a centralized registry for different types of Lie algebras,
their structure constants, and configuration data.
"""

from typing import Dict, Any, Optional, List
import json
import yaml
from pathlib import Path


REGISTRY = {}

def register(name: str):
    def deco(cls):
        if name in REGISTRY:
            raise ValueError(f"Component already registered: {name}")
        REGISTRY[name] = cls
        return cls
    return deco

def get_component(name: str):
    if name not in REGISTRY:
        raise KeyError(f"Component not found: {name}")
    return REGISTRY[name]
