"""
Abstract base class for Factorio Learning Environment agents.
"""
from abc import ABC, abstractmethod

class Agent(ABC):
    """Abstract base class for agents."""
    
    @abstractmethod
    def act(self, observation):
        """Process an observation and return an action.
        
        Args:
            observation: The observation from the environment
            
        Returns:
            action: The action to perform
        """
        pass
