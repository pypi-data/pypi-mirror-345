"""
Package build utilities for Factorio Learning Environment.
"""
import os
import sys
import shutil
import re
import configparser
import tomli

# Directory to create for packaging
TEMP_DIR = "factorio_learning_environment"

def get_version_from_pyproject():
    """Extract version from pyproject.toml."""
    try:
        with open("pyproject.toml", "rb") as f:
            pyproject = tomli.load(f)
            return pyproject["project"]["version"]
    except (FileNotFoundError, KeyError):
        return "0.0.0"  # Fallback version
    except AttributeError:
        # Handle case where tomli might not be available
        try:
            import toml
            with open("pyproject.toml", "r") as f:
                pyproject = toml.load(f)
                return pyproject["project"]["version"]
        except (ImportError, FileNotFoundError, KeyError):
            return "0.0.0"  # Fallback version

def cleanup_temp_dir():
    """Clean up the temporary directory when the process exits."""
    if os.path.exists(TEMP_DIR) and os.path.isdir(TEMP_DIR):
        # Try to remove symlinks first to avoid issues with rmtree
        for pkg in os.listdir(TEMP_DIR):
            pkg_path = os.path.join(TEMP_DIR, pkg)
            if os.path.islink(pkg_path):
                os.unlink(pkg_path)
        
        # Now try to remove the directory and any remaining files
        try:
            shutil.rmtree(TEMP_DIR)
            print(f"Cleaned up temporary directory: {TEMP_DIR}")
        except Exception as e:
            print(f"Warning: Could not remove temporary directory {TEMP_DIR}: {e}")