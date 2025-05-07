"""
Custom bdist_wheel command for Factorio Learning Environment.
"""
from setuptools.command.bdist_wheel import bdist_wheel as _bdist_wheel
import os
import shutil

def create_custom_wheel(TEMP_DIR, subpackages):
    """Create a custom bdist_wheel command class."""
    
    class custom_bdist_wheel(_bdist_wheel):
        """Custom bdist_wheel command that ensures proper handling of temporary package structure."""
        
        def finalize_options(self):
            """Finalize options for the wheel build."""
            _bdist_wheel.finalize_options(self)
            # Ensure we're creating a pure Python wheel
            self.root_is_pure = True
        
        def run(self):
            """Build the wheel."""
            # Set up the temporary package structure
            self._setup_package_structure()
            
            # Call the parent method to create the actual wheel
            _bdist_wheel.run(self)
            
        def _setup_package_structure(self):
            """Set up the package structure for wheel distribution."""
            # Make sure the main package directory exists
            if not os.path.exists(TEMP_DIR):
                os.makedirs(TEMP_DIR, exist_ok=True)
                
            # Create/verify the main package __init__.py
            init_path = os.path.join(TEMP_DIR, "__init__.py")
            if not os.path.exists(init_path):
                print(f"Creating main package __init__.py in {TEMP_DIR}")
                # For wheel distribution, use the simple import mechanism
                with open(os.path.join(os.path.dirname(__file__), 'init_template.py'), 'r') as template:
                    template_content = template.read().format(version=self._get_version())
                    with open(init_path, 'w') as f:
                        f.write(template_content)
                        
            # Create run.py entry point
            run_path = os.path.join(TEMP_DIR, "run.py")
            if not os.path.exists(run_path):
                print(f"Creating run.py in {TEMP_DIR}")
                with open(os.path.join(os.path.dirname(__file__), 'run_template.py'), 'r') as template:
                    template_content = template.read().format(version=self._get_version())
                    with open(run_path, 'w') as f:
                        f.write(template_content)
            
            # Process each subpackage
            for pkg in subpackages:
                pkg_dest_path = os.path.join(TEMP_DIR, pkg)
                
                # Skip if it's already a valid directory or symlink
                if os.path.exists(pkg_dest_path) and (os.path.isdir(pkg_dest_path) or os.path.islink(pkg_dest_path)):
                    continue
                    
                # Create the package directory
                os.makedirs(pkg_dest_path, exist_ok=True)
                
                # If the source package exists, copy or link its contents
                if os.path.exists(pkg):
                    # Try to create a symlink on Unix systems
                    if os.name == 'posix' and not os.path.islink(pkg_dest_path):
                        try:
                            # Remove directory before creating symlink
                            if os.path.exists(pkg_dest_path):
                                shutil.rmtree(pkg_dest_path)
                            os.symlink(f"../{pkg}", pkg_dest_path, target_is_directory=True)
                            print(f"Created symlink from {pkg} to {pkg_dest_path}")
                            continue
                        except OSError as e:
                            print(f"Could not create symlink, falling back to copy: {e}")
                    
                    # Copy necessary files if symlink fails or on Windows
                    self._copy_package_files(pkg, pkg_dest_path)
                else:
                    # If the source package doesn't exist, create a minimal structure
                    print(f"Source package {pkg} not found, creating minimal package")
                    init_file = os.path.join(pkg_dest_path, "__init__.py")
                    with open(init_file, "w") as f:
                        f.write(f"# {pkg} package for Factorio Learning Environment\n")
        
        def _copy_package_files(self, src_pkg, dest_pkg):
            """Recursively copy package files."""
            print(f"Copying files from {src_pkg} to {dest_pkg}")
            
            # Create destination directory if it doesn't exist
            os.makedirs(dest_pkg, exist_ok=True)
            
            # Copy __init__.py file
            src_init = os.path.join(src_pkg, "__init__.py")
            dest_init = os.path.join(dest_pkg, "__init__.py")
            
            if os.path.exists(src_init):
                shutil.copy2(src_init, dest_init)
            else:
                # Create a minimal __init__.py if it doesn't exist
                with open(dest_init, "w") as f:
                    f.write(f"# {os.path.basename(src_pkg)} package for Factorio Learning Environment\n")
            
            # Walk through the source directory and copy relevant files
            for root, dirs, files in os.walk(src_pkg):
                # Skip __pycache__ directories
                if "__pycache__" in dirs:
                    dirs.remove("__pycache__")
                
                # Get the relative path from the package root
                rel_path = os.path.relpath(root, src_pkg)
                if rel_path == ".":
                    rel_path = ""
                
                # Create destination directory
                if rel_path:
                    dest_dir = os.path.join(dest_pkg, rel_path)
                    os.makedirs(dest_dir, exist_ok=True)
                else:
                    dest_dir = dest_pkg
                
                # Copy Python files and necessary data files
                for file in files:
                    # Skip __pycache__ files
                    if "__pycache__" in file:
                        continue
                        
                    if file.endswith(('.py', '.md', '.json', '.lua', '.png', '.jpg', '.jpeg', '.gif')):
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(dest_dir, file)
                        try:
                            shutil.copy2(src_file, dest_file)
                        except (IOError, OSError) as e:
                            print(f"Warning: Could not copy {src_file}: {e}")
        
        def _get_version(self):
            """Get the package version."""
            try:
                from pkg_utils import get_version_from_pyproject
                return get_version_from_pyproject()
            except ImportError:
                return "0.0.0"
    
    return custom_bdist_wheel