"""
Custom sdist command for Factorio Learning Environment.
This optimized version aggressively filters directories and files to reduce build time.
"""
from setuptools.command.sdist import sdist as _sdist
import os
import shutil
import fnmatch

def create_custom_sdist(TEMP_DIR, subpackages):
    """Create a custom sdist command class with aggressive optimization."""
    
    # Directories to completely exclude from sdist
    HEAVY_DIRS = [
        'summary_cache', 'mods', '_screenshots', 'assets', 'dist', 'build', 
        'leaderboard', 'venv', 'venv_py311', 'log', '__pycache__', 'node_modules',
        '.git', '.github', '.pytest_cache', '.idea', 'docs', 'cluster'
    ]
    
    # File patterns to exclude (wildcard patterns)
    EXCLUDE_PATTERNS = [
        '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.zip', '*.tar.gz', '*.whl',
        '*.mp4', '*.webp', '*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg', '*.ico',
        '.DS_Store', '*.log', '*.db', '*.sqlite', 'Thumbs.db'
    ]
    
    # Core directories where we want to include all Python files
    CORE_DIRS = ['agents', 'server', 'pkg_utils']
    
    # Extended core directories for functions
    EXT_CORE_PATTERNS = [
        os.path.join('env', 'src', '*.py'),
        os.path.join('env', 'src', 'models', '*.py'),
        os.path.join('env', 'src', 'tools', '*.py'),
        os.path.join('env', 'src', 'tools', '*', '*.py'),
        os.path.join('env', 'src', 'utils', '*.py')
    ]
    
    class custom_sdist(_sdist):
        """Optimized sdist command that minimizes included files."""
        def make_distribution(self):
            """Create a minimal source distribution optimized for install (not development)."""
            print("\nBuilding minimal source distribution...")
            
            # First, remove any existing links in factorio_learning_environment directory
            if os.path.exists(TEMP_DIR):
                for item in os.listdir(TEMP_DIR):
                    item_path = os.path.join(TEMP_DIR, item)
                    if os.path.islink(item_path):
                        os.unlink(item_path)
            
            # Process each package efficiently
            for pkg in subpackages:
                pkg_dest_path = os.path.join(TEMP_DIR, pkg)
                if not os.path.exists(pkg_dest_path):
                    os.makedirs(pkg_dest_path, exist_ok=True)
                
                # Always create an __init__.py in the root of the package
                init_file = os.path.join(pkg_dest_path, "__init__.py")
                with open(init_file, "w") as f:
                    f.write(f"# {pkg} package for Factorio Learning Environment\n")
                
                # Only copy selected files if the original package exists
                if os.path.exists(pkg):
                    print(f"Processing package: {pkg}")
                    
                    # Separate processing for core vs. non-core packages
                    if pkg in CORE_DIRS:
                        # For core directories, include all Python files
                        self._process_core_package(pkg, pkg_dest_path)
                    else:
                        # For non-core packages, use more aggressive filtering
                        self._process_non_core_package(pkg, pkg_dest_path)
            
            # Create some empty directories to ensure package structure
            for pkg in subpackages:
                # Create minimal structure for eval (most prone to timeout)
                if pkg == 'eval':
                    self._ensure_directory_with_init(os.path.join(TEMP_DIR, 'eval', 'open'))
                    self._ensure_directory_with_init(os.path.join(TEMP_DIR, 'eval', 'tasks'))
                
                # Create minimal structure for data (also prone to timeout)
                if pkg == 'data':
                    self._ensure_directory_with_init(os.path.join(TEMP_DIR, 'data', 'plans'))
                    self._ensure_directory_with_init(os.path.join(TEMP_DIR, 'data', 'scripts'))
                    self._ensure_directory_with_init(os.path.join(TEMP_DIR, 'data', 'blueprints_to_policies'))
            
            # Copy extended core patterns
            for pattern in EXT_CORE_PATTERNS:
                self._copy_pattern_files(pattern)
            
            print("Finished preparing minimal source distribution")
            # Call the parent method to create the actual distribution
            _sdist.make_distribution(self)
        
        def _ensure_directory_with_init(self, dir_path):
            """Create a directory and add an __init__.py file."""
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            # Add an __init__.py
            init_file = os.path.join(dir_path, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, "w") as f:
                    pkg_name = os.path.relpath(dir_path, TEMP_DIR).replace(os.path.sep, ".")
                    f.write(f"# factorio_learning_environment.{pkg_name} package\n")
        
        def _process_core_package(self, pkg, pkg_dest_path):
            """Process a core package with less aggressive filtering."""
            for root, dirs, files in os.walk(pkg):
                # Filter out heavy dirs and hidden dirs
                dirs[:] = [d for d in dirs if d not in HEAVY_DIRS and not d.startswith('.')]
                
                # Get relative path from package root
                rel_path = os.path.relpath(root, pkg)
                dest_dir = os.path.join(pkg_dest_path, rel_path) if rel_path != "." else pkg_dest_path
                
                # Create destination directory
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)
                
                # Add an __init__.py if needed
                init_file = os.path.join(dest_dir, "__init__.py")
                if not os.path.exists(init_file):
                    with open(init_file, "w") as f:
                        rel_pkg = rel_path.replace(os.path.sep, ".") if rel_path != "." else ""
                        if rel_pkg:
                            f.write(f"# {pkg}.{rel_pkg} package\n")
                        else:
                            f.write(f"# {pkg} package\n")
                
                # Copy Python files and important config files
                for file in files:
                    # Skip files that match exclude patterns
                    if any(fnmatch.fnmatch(file, pattern) for pattern in EXCLUDE_PATTERNS):
                        continue
                    
                    # Check extensions for inclusion
                    if file.endswith('.py') or file in ['__init__.py', 'README.md', 'requirements.txt']:
                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(dest_dir, file)
                        try:
                            shutil.copy2(src_file, dest_file)
                        except (IOError, OSError) as e:
                            print(f"Warning: Could not copy {src_file}: {e}")
        
        def _process_non_core_package(self, pkg, pkg_dest_path):
            """Process a non-core package with aggressive filtering."""
            # For non-core packages, we just ensure basic structure and __init__.py files
            # Extremely minimal approach to avoid timeout
            
            # Only add the key Python files in the root dir
            if os.path.exists(pkg):
                # Get all Python files in the root
                for file in os.listdir(pkg):
                    file_path = os.path.join(pkg, file)
                    if file.endswith('.py') and os.path.isfile(file_path):
                        dest_file = os.path.join(pkg_dest_path, file)
                        try:
                            shutil.copy2(file_path, dest_file)
                        except (IOError, OSError) as e:
                            print(f"Warning: Could not copy {file_path}: {e}")
                
                # For env, eval and data packages, only add key implementation files
                # This is a compromise between functionality and build time
                if pkg == 'env':
                    # Key implementation files in env
                    self._ensure_directory_with_init(os.path.join(pkg_dest_path, 'src'))
                    self._ensure_directory_with_init(os.path.join(pkg_dest_path, 'src', 'models'))
                    self._ensure_directory_with_init(os.path.join(pkg_dest_path, 'src', 'tools'))
                    self._ensure_directory_with_init(os.path.join(pkg_dest_path, 'src', 'utils'))
                
                elif pkg == 'eval' or pkg == 'data':
                    # For eval and data, just ensure the minimal viable directories
                    # Get directories with __init__.py at the first level only
                    for item in os.listdir(pkg):
                        item_path = os.path.join(pkg, item)
                        init_path = os.path.join(item_path, '__init__.py')
                        if os.path.isdir(item_path) and os.path.exists(init_path):
                            # Create subdirectory
                            subdir_path = os.path.join(pkg_dest_path, item)
                            if not os.path.exists(subdir_path):
                                os.makedirs(subdir_path, exist_ok=True)
                            
                            # Copy just the __init__.py
                            try:
                                shutil.copy2(init_path, os.path.join(subdir_path, '__init__.py'))
                            except (IOError, OSError) as e:
                                # If copy fails, just create an empty one
                                with open(os.path.join(subdir_path, '__init__.py'), 'w') as f:
                                    f.write(f"# factorio_learning_environment.{pkg}.{item} package\n")
        
        def _copy_pattern_files(self, pattern):
            """Copy files matching a glob pattern to their corresponding location in TEMP_DIR."""
            import glob as glob_module
            
            # For each matching file, copy it to the corresponding location in TEMP_DIR
            base_dir = os.path.dirname(pattern)
            for file_path in glob_module.glob(pattern):
                if os.path.isfile(file_path):
                    # Get relative path from the base directory
                    rel_path = os.path.relpath(file_path, '.')
                    dest_path = os.path.join(TEMP_DIR, rel_path)
                    
                    # Create directories if needed
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    
                    # Copy the file
                    try:
                        shutil.copy2(file_path, dest_path)
                    except (IOError, OSError) as e:
                        print(f"Warning: Could not copy pattern file {file_path}: {e}")
            
    return custom_sdist