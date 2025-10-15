# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Utilities for reading YAML configs with ${VAR} placeholder resolution."""

import os
import re
from pathlib import Path
from typing import Any, Dict

import yaml


def _smart_cast(value: str) -> Any:
    """
    Smart cast string to appropriate type (int, float, bool, or str).
    
    Args:
        value: String value to cast
        
    Returns:
        Value cast to appropriate type
    """
    # Try int
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Try bool (case insensitive)
    lower_val = value.lower()
    if lower_val in ('true', 'yes', '1'):
        return True
    elif lower_val in ('false', 'no', '0'):
        return False
    
    # Return as string
    return value


def resolve_env_vars(value: Any) -> Any:
    """
    Recursively resolve ${VAR} placeholders in strings using environment variables.
    
    Environment variables are automatically cast to appropriate types:
    - "30" → 30 (int)
    - "3.14" → 3.14 (float)
    - "true" → True (bool)
    - Other → str
    
    Args:
        value: Value to resolve (can be str, dict, list, etc.)
        
    Returns:
        Resolved value with environment variables substituted
    """
    if isinstance(value, str):
        # Check if entire value is a single ${VAR} placeholder
        pattern = r'^\$\{([^}]+)\}$'
        match = re.match(pattern, value)
        
        if match:
            # Full replacement - return with type casting
            var_name = match.group(1)
            env_value = os.getenv(var_name, '')
            if env_value:
                return _smart_cast(env_value)
            else:
                # Variable not set, return placeholder as-is
                return value
        
        # Partial replacement - find all ${VAR} patterns (keep as string)
        pattern = r'\$\{([^}]+)\}'
        
        def replacer(match: re.Match) -> str:
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        
        return re.sub(pattern, replacer, value)
    
    elif isinstance(value, dict):
        return {k: resolve_env_vars(v) for k, v in value.items()}
    
    elif isinstance(value, list):
        return [resolve_env_vars(item) for item in value]
    
    else:
        return value


def load_yaml_with_env(yaml_path: Path | str) -> Dict[str, Any]:
    """
    Load a YAML file and resolve ${VAR} placeholders with environment variables.
    
    Args:
        yaml_path: Path to YAML file
        
    Returns:
        Dictionary with resolved configuration
        
    Raises:
        FileNotFoundError: If YAML file doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    yaml_path = Path(yaml_path)
    
    if not yaml_path.exists():
        raise FileNotFoundError(f"Config file not found: {yaml_path}")
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        raw_config = yaml.safe_load(f)
    
    return resolve_env_vars(raw_config)

