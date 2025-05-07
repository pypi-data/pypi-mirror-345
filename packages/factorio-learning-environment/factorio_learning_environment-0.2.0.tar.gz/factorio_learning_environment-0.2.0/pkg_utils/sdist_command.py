"""
Custom sdist command for Factorio Learning Environment.
"""
from setuptools.command.sdist import sdist as _sdist
import os
import shutil

def create_custom_sdist(TEMP_DIR, subpackages):
    """Create a custom sdist command class."""
    
    class custom_sdist(_sdist):
        """Custom sdist command that ensures only the temporary package structure is included."""
        def make_distribution(self):
            """Create the source distribution."""
            # First, remove any existing factorio_learning_environment directory
            if os.path.exists(TEMP_DIR):
                for item in os.listdir(TEMP_DIR):
                    item_path = os.path.join(TEMP_DIR, item)
                    if os.path.islink(item_path):
                        os.unlink(item_path)
            
            # Create fresh package directories
            for pkg in subpackages:
                pkg_dest_path = os.path.join(TEMP_DIR, pkg)
                if not os.path.exists(pkg_dest_path):
                    os.makedirs(pkg_dest_path, exist_ok=True)
                
                # Add an __init__.py to make it a proper package
                init_file = os.path.join(pkg_dest_path, "__init__.py")
                if not os.path.exists(init_file):
                    with open(init_file, "w") as f:
                        f.write(f"# {pkg} package for Factorio Learning Environment\n")
                
                # If the original package exists, copy its contents
                if os.path.exists(pkg):
                    # Recursively copy Python files and necessary assets
                    for root, dirs, files in os.walk(pkg):
                        # Skip __pycache__ directories
                        if "__pycache__" in dirs:
                            dirs.remove("__pycache__")
                        
                        # Get the relative path from the package root
                        rel_path = os.path.relpath(root, pkg)
                        if rel_path == ".":
                            rel_path = ""
                        
                        dest_dir = os.path.join(pkg_dest_path, rel_path) if rel_path else pkg_dest_path
                        
                        # Create the destination directory
                        if not os.path.exists(dest_dir):
                            os.makedirs(dest_dir, exist_ok=True)
                        
                        # Copy files
                        for file in files:
                            if file.endswith(('.py', '.md', '.json', '.lua')):
                                src_file = os.path.join(root, file)
                                dest_file = os.path.join(dest_dir, file)
                                shutil.copy2(src_file, dest_file)
            
            # Call the parent method to create the actual distribution
            _sdist.make_distribution(self)
            
    return custom_sdist