#!/usr/bin/env python3
"""
Entry point for the Factorio Learning Environment.
Version: {version}
"""
import os
import sys
import importlib.util

def _import_module(module_path, module_name):
    """Import a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def main():
    """Main entry point for the CLI."""
    # Check for version flag
    if len(sys.argv) > 1 and sys.argv[1] in ['--version', '-v']:
        print("Factorio Learning Environment {version}")
        return
        
    # Add the repository root to the path
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Add the env/src directory to the path
    env_src_dir = os.path.join(root_dir, 'env', 'src')
    
    # Add paths to sys.path if they're not already there
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    if env_src_dir not in sys.path:
        sys.path.insert(0, env_src_dir)
    
    # Import the actual run module
    run_module_path = os.path.join(root_dir, 'eval', 'open', 'independent_runs', 'run.py')
    run_module = _import_module(run_module_path, 'eval.open.independent_runs.run')
    
    # Call the main function from the run module
    run_module.main()

if __name__ == "__main__":
    main()