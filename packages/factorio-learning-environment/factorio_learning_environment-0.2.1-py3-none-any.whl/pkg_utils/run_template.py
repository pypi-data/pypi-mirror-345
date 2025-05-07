#!/usr/bin/env python3
"""
Entry point for the Factorio Learning Environment.
Version: {version}
"""
import importlib.util
import os
import sys

def main():
    """Main entry point for the CLI."""
    # Check for version flag
    if len(sys.argv) > 1 and sys.argv[1] in ['--version', '-v']:
        print("Factorio Learning Environment {version}")
        return
        
    # Try to import the run module directly
    try:
        from factorio_learning_environment.eval.open.independent_runs import run
        run.main()
    except ImportError:
        # Fallback for development mode
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_src_dir = os.path.join(root_dir, 'env', 'src')
        
        # Add paths to sys.path if they're not already there
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
        if env_src_dir not in sys.path:
            sys.path.insert(0, env_src_dir)
        
        # Import using path
        run_module_path = os.path.join(root_dir, 'eval', 'open', 'independent_runs', 'run.py')
        
        spec = importlib.util.spec_from_file_location('run', run_module_path)
        run_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_module)
        run_module.main()

if __name__ == "__main__":
    main()