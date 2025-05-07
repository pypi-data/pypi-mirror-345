"""
Factorio Learning Environment
============================

A Python framework for training and evaluating AI agents in the Factorio game environment.
"""

__version__ = "0.2.0"

# Import subpackages
try:
    from . import agents
    from . import env
    from . import eval
    from . import data
    from . import server
except ImportError:
    # Fallback for partial installation
    pass
