"""
Minimal sdist command for Factorio Learning Environment.
This version creates a bare minimum source distribution for installation purposes only.
"""
from setuptools.command.sdist import sdist as _sdist
import os
import shutil

def create_minimal_sdist(TEMP_DIR, subpackages):
    """Create a minimal sdist command class that works reliably."""
    
    class minimal_sdist(_sdist):
        """
        Minimal sdist command that creates a basic package structure.
        This creates a super-minimal source distribution with just enough to be installable.
        It's not intended for development, only for distribution and installation.
        """
        
        def make_distribution(self):
            """Create the minimal source distribution."""
            print("\n===== PROCESS LOGGING: Starting minimal source distribution build =====")
            print("[LOG] Preparing bare-bones package structure...")
            start_time = os.times()
            
            # Clean any existing symlinks
            if os.path.exists(TEMP_DIR):
                print(f"[LOG] Cleaning existing directory: {TEMP_DIR}")
                for item in os.listdir(TEMP_DIR):
                    item_path = os.path.join(TEMP_DIR, item)
                    if os.path.islink(item_path):
                        print(f"[LOG] Removing symlink: {item_path}")
                        os.unlink(item_path)
            
            # Create only the most essential structure
            for pkg in subpackages:
                pkg_dest_path = os.path.join(TEMP_DIR, pkg)
                print(f"[LOG] Setting up minimal structure for package: {pkg}")
                
                # Create the package directory
                if not os.path.exists(pkg_dest_path):
                    print(f"[LOG] Creating directory: {pkg_dest_path}")
                    os.makedirs(pkg_dest_path, exist_ok=True)
                
                # Create a minimal __init__.py file
                init_path = os.path.join(pkg_dest_path, "__init__.py")
                print(f"[LOG] Creating __init__.py: {init_path}")
                with open(init_path, "w") as f:
                    f.write(f"# {pkg} package for Factorio Learning Environment\n")
                
                # Create minimal subdirectories for each package
                if pkg == 'agents':
                    print(f"[LOG] Setting up 'agents' package structure")
                    self._create_minimal_structure(pkg_dest_path, [
                        'utils',
                        'utils/formatters',
                    ])
                    # Add important files
                    print(f"[LOG] Copying core Python files for 'agents'")
                    self._copy_py_file_if_exists(pkg, 'agent_abc.py', pkg_dest_path)
                    self._copy_py_file_if_exists(pkg, 'basic_agent.py', pkg_dest_path)
                    self._copy_py_file_if_exists(pkg, 'visual_agent.py', pkg_dest_path)
                
                elif pkg == 'env':
                    print(f"[LOG] Setting up 'env' package structure")
                    self._create_minimal_structure(pkg_dest_path, [
                        'src',
                        'src/models',
                        'src/tools',
                        'src/utils',
                    ])
                    # Add some important files
                    src_dir = os.path.join(pkg_dest_path, 'src')
                    print(f"[LOG] Copying core Python files for 'env'")
                    self._copy_py_file_if_exists(os.path.join(pkg, 'src'), 'game_types.py', src_dir)
                    self._copy_py_file_if_exists(os.path.join(pkg, 'src'), 'instance.py', src_dir)
                    self._copy_py_file_if_exists(os.path.join(pkg, 'src'), 'namespace.py', src_dir)
                
                elif pkg == 'eval':
                    print(f"[LOG] Setting up 'eval' package structure")
                    self._create_minimal_structure(pkg_dest_path, [
                        'tasks',
                        'open',
                    ])
                    # Add important files
                    print(f"[LOG] Copying core Python files for 'eval'")
                    self._copy_py_file_if_exists(pkg, 'evaluator.py', pkg_dest_path)
                    
                elif pkg == 'data':
                    print(f"[LOG] Setting up 'data' package structure")
                    self._create_minimal_structure(pkg_dest_path, [
                        'scripts',
                        'plans',
                        'blueprints_to_policies',
                    ])
                    
                elif pkg == 'server':
                    # Server is simpler, just create the package
                    print(f"[LOG] 'server' package is minimal, just creating directory")
                    pass
            
            mid_time = os.times()
            elapsed = mid_time.user - start_time.user + mid_time.system - start_time.system
            print(f"[LOG] Finished preparing minimal structure in {elapsed:.2f} seconds")
            print("[LOG] Calling parent sdist make_distribution method...")
            print("===== PROCESS LOGGING: Starting setuptools sdist process =====")
            
            # Call the parent method to create the actual distribution
            _sdist.make_distribution(self)
            
            end_time = os.times()
            total_elapsed = end_time.user - start_time.user + end_time.system - start_time.system
            print(f"[LOG] Total time for minimal_sdist: {total_elapsed:.2f} seconds")
            print("===== PROCESS LOGGING: Completed minimal source distribution build =====")
            
        
        def _create_minimal_structure(self, base_path, subdirs):
            """Create minimal directory structure with empty __init__.py files."""
            print(f"[LOG] Creating subdirectories in {base_path}...")
            for subdir in subdirs:
                dir_path = os.path.join(base_path, subdir)
                if not os.path.exists(dir_path):
                    print(f"[LOG]   Creating directory: {dir_path}")
                    os.makedirs(dir_path, exist_ok=True)
                
                # Add an __init__.py file
                init_path = os.path.join(dir_path, "__init__.py")
                if not os.path.exists(init_path):
                    print(f"[LOG]   Creating __init__.py: {init_path}")
                    with open(init_path, "w") as f:
                        # Use the relative import path for the comment
                        rel_pkg = dir_path[len(TEMP_DIR)+1:].replace(os.path.sep, ".")
                        f.write(f"# factorio_learning_environment.{rel_pkg} package\n")
        
        def _copy_py_file_if_exists(self, src_dir, filename, dest_dir):
            """Copy a Python file if it exists in the source directory."""
            src_file = os.path.join(src_dir, filename)
            dest_file = os.path.join(dest_dir, filename)
            
            if os.path.exists(src_file) and os.path.isfile(src_file):
                print(f"[LOG]   Copying file: {src_file} -> {dest_file}")
                try:
                    shutil.copy2(src_file, dest_file)
                except (IOError, OSError) as e:
                    print(f"[LOG]   Warning: Could not copy {src_file}: {e}")
                    print(f"[LOG]   Creating placeholder instead")
                    # If we couldn't copy the file, create an empty one as a fallback
                    with open(dest_file, "w") as f:
                        f.write(f"# Empty placeholder for {filename}\n")
                        f.write("# This is a minimal placeholder created during packaging\n")
                        f.write("# The actual implementation will be installed by pip.\n")
            else:
                # If the file doesn't exist, create a placeholder
                print(f"[LOG]   File not found: {src_file}")
                print(f"[LOG]   Creating placeholder at: {dest_file}")
                with open(dest_file, "w") as f:
                    f.write(f"# Empty placeholder for {filename}\n")
                    f.write("# This is a minimal placeholder created during packaging\n")
                    f.write("# The actual implementation will be installed by pip.\n")
    
    return minimal_sdist