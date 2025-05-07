"""
Factorio Learning Environment setup script.

This setup creates the package structure during build, automatically detecting whether
it's running in development mode (using symlinks) or distribution mode (copying files).
"""

from setuptools import setup, find_packages, Command
import os
import sys
import shutil
import atexit
import glob

# Add pkg_utils to sys.path to ensure it's available during installation
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our packaging utilities
from pkg_utils import cleanup_temp_dir

# Directory to create for packaging
TEMP_DIR = "factorio_learning_environment"

# Detect if we're in development mode or distribution mode
# Development: Installing with -e, original directories exist
# Distribution: Building for PyPI, original directories might not exist
is_dev_install = any('editable' in arg for arg in sys.argv)
is_sdist = 'sdist' in sys.argv or 'bdist_wheel' in sys.argv

# Only register cleanup for regular installs (not dev or sdist)
if not (is_dev_install or is_sdist):
    atexit.register(cleanup_temp_dir)

# Custom clean command
class CleanCommand(Command):
    """Custom clean command to clean up the project root."""
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        cleanup_temp_dir()

# Create the temporary packaging directory structure
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Write the main package __init__.py file
init_path = os.path.join(TEMP_DIR, "__init__.py")
if is_sdist or not all(os.path.exists(pkg) for pkg in ["agents", "env", "eval", "data", "server"]):
    # For sdist, use the simple import mechanism
    with open('pkg_utils/init_template.py', 'r') as template:
        with open(init_path, 'w') as f:
            f.write(template.read())
else:
    # For development mode, use the dynamic import mechanism
    with open('pkg_utils/init_template_dev.py', 'r') as template:
        with open(init_path, 'w') as f:
            f.write(template.read())

# Create the run.py entry point
run_path = os.path.join(TEMP_DIR, "run.py")
if is_sdist or not all(os.path.exists(pkg) for pkg in ["agents", "env", "eval", "data", "server"]):
    # For sdist, use the simple approach
    with open('pkg_utils/run_template.py', 'r') as template:
        with open(run_path, 'w') as f:
            f.write(template.read())
else:
    # For development mode, use the dynamic approach
    with open('pkg_utils/run_template_dev.py', 'r') as template:
        with open(run_path, 'w') as f:
            f.write(template.read())

# Handle the package modules
subpackages = ["agents", "env", "eval", "data", "server"]

# For source distribution, we need to package the actual files
if is_sdist:
    # Import the custom sdist command
    from pkg_utils.sdist_command import create_custom_sdist
    
    # Create the custom sdist command
    custom_sdist = create_custom_sdist(TEMP_DIR, subpackages)
    
    # Register the custom sdist command
    cmdclass = {'sdist': custom_sdist, 'clean': CleanCommand}
else:
    cmdclass = {'clean': CleanCommand}

# For local development, create symlinks
for pkg in subpackages:
    pkg_dest_path = os.path.join(TEMP_DIR, pkg)
    if not os.path.exists(pkg_dest_path):
        # For local development (original directories exist)
        if os.path.exists(pkg):
            if sys.platform == "win32":
                # On Windows, we need to use directory junctions
                os.system(f'mklink /J "{pkg_dest_path}" "{pkg}"')
            else:
                # On Unix, we can create symlinks
                os.symlink(f"../{pkg}", pkg_dest_path, target_is_directory=True)
        # For remote installation (create empty package directories)
        else:
            os.makedirs(pkg_dest_path, exist_ok=True)
            # Create an __init__.py file to make it a proper package
            with open(os.path.join(pkg_dest_path, "__init__.py"), "w") as f:
                f.write(f"# {pkg} package for Factorio Learning Environment\n")

# Main setup call that uses configuration from both setup.py and pyproject.toml
if __name__ == "__main__":
    # Define package metadata that needs to be available in setup.py
    setup(
        packages=["factorio_learning_environment"] + [f"factorio_learning_environment.{pkg}" for pkg in subpackages],
        package_dir={"factorio_learning_environment": TEMP_DIR},
        include_package_data=True,
        cmdclass=cmdclass,
    )