"""
Factorio Learning Environment
============================

A Python framework for training and evaluating AI agents in the Factorio game environment.
"""
import importlib.util
import os
import sys
from pathlib import Path

__version__ = '{version}'

# Dynamically import the modules based on the project structure
root_path = Path(__file__).parent.parent

def _import_module_if_available(module_name):
    """Safely import a module if it's available."""
    try:
        if module_name in sys.modules:
            return sys.modules[module_name]
            
        module_path = root_path / module_name / "__init__.py"
        if module_path.exists():
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module
        return None
    except (ImportError, ModuleNotFoundError):
        return None

# Import core modules
env = _import_module_if_available("env")
data = _import_module_if_available("data")

# Import optional modules with proper dependency handling
agents = _import_module_if_available("agents")
eval = _import_module_if_available("eval")
server = _import_module_if_available("server")

# Expose as factorio_learning_environment.{module}
if env:
    sys.modules["factorio_learning_environment.env"] = env
if data:
    sys.modules["factorio_learning_environment.data"] = data
if agents:
    sys.modules["factorio_learning_environment.agents"] = agents
if eval:
    sys.modules["factorio_learning_environment.eval"] = eval
if server:
    sys.modules["factorio_learning_environment.server"] = server