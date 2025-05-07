"""
Package build utilities for Factorio Learning Environment.
"""
import os
import sys
import shutil

# Directory to create for packaging
TEMP_DIR = "factorio_learning_environment"

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