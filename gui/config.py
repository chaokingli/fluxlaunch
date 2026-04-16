"""
Configuration management for llama-server
Save, load, and update server settings using JSON
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

# Import parameter definitions from params_db
from gui.params_db import PARAMETER_DATABASE, DEFAULT_CONFIG as PARAM_DEFAULTS

# Current config version for migration
CONFIG_VERSION = 2

# Build DEFAULT_CONFIG from PARAMETER_DATABASE
# Copy all parameters with their defaults (excluding None values)
DEFAULT_CONFIG: Dict[str, Any] = {
    param_def.name: param_def.default
    for param_def in PARAMETER_DATABASE.values()
    if param_def.default is not None
}

# Add backward compatibility keys that were in the original DEFAULT_CONFIG
DEFAULT_CONFIG.update(
    {
        "model_path": "",
        "cache_capacity": "2048MiB",
        # Language setting for i18n support (default: "en")
        "language": "en",
        # Add config version for migration
        "config_version": CONFIG_VERSION,
    }
)

CONFIG_FILE = Path.home() / ".llama-server-config.json"


def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file with migration support"""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Check if migration is needed
        config = _migrate_config(config)

        # Merge with defaults to ensure all keys exist
        return {**DEFAULT_CONFIG, **config}
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load config file: {e}")
        return DEFAULT_CONFIG.copy()


def _migrate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate old config versions to current version"""
    # Get version from config, default to 1 if not present (backward compatibility)
    config_version = config.get("config_version", 1)

    if config_version == CONFIG_VERSION:
        return config

    if config_version == 1:
        # Migrate from version 1 to version 2
        config = _migrate_v1_to_v2(config)

    # Future migrations can be added here
    # if config_version == 2:
    #     config = _migrate_v2_to_v3(config)

    # Ensure version is set correctly
    config["config_version"] = CONFIG_VERSION

    return config


def _migrate_v1_to_v2(config: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate configuration from version 1 to version 2"""
    # Start with all new parameters (from DEFAULT_CONFIG)
    migrated = DEFAULT_CONFIG.copy()

    # Preserve user values from old config for existing parameters
    # Copy all other old values that might exist
    for key, value in config.items():
        if key != "config_version":  # Skip the old version field
            migrated[key] = value

    return migrated


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to JSON file"""
    try:
        # Ensure config_version is set
        config["config_version"] = CONFIG_VERSION

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except IOError as e:
        print(f"Error saving config: {e}")
        return False


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a single configuration value"""
    config = load_config()
    return config.get(key, default)


def set_config_value(key: str, value: Any) -> bool:
    """Set a single configuration value and save"""
    config = load_config()
    config[key] = value
    return save_config(config)


def get_language() -> str:
    """Get the current language setting (default: "en")"""
    return load_config().get("language", "en")


def set_language(lang: str) -> bool:
    """Set the language setting and save to config"""
    config = load_config()
    config["language"] = lang
    return save_config(config)


def get_llama_cpp_path() -> Optional[Path]:
    """Get the path to llama.cpp installation"""
    # Look for llama-server binary in standard locations
    script_dir = Path(__file__).parent.parent
    possible_paths = [
        script_dir / "llama.cpp" / "bin" / "llama-server",
        Path.home() / "llama" / "llama.cpp" / "bin" / "llama-server",
        Path("/usr/local/bin/llama-server"),
    ]

    for path in possible_paths:
        if path.exists():
            return path.parent  # Return the bin directory
    return None


def get_models_dir() -> Path:
    """Get the models directory"""
    script_dir = Path(__file__).parent.parent
    models_dir = script_dir / "models"
    if models_dir.exists():
        return models_dir
    return Path.home() / "llama" / "models"
