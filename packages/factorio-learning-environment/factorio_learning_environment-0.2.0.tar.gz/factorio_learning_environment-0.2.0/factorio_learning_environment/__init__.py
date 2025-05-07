"""
Factorio Learning Environment
============================

A Python framework for training and evaluating AI agents in the Factorio game environment.
"""

__version__ = '0.2.0'

# Import subpackages
from . import env
from . import data
try:
    from . import agents
except ImportError:
    agents = None
try:
    from . import eval
except ImportError:
    eval = None
try:
    from . import server
except ImportError:
    server = None