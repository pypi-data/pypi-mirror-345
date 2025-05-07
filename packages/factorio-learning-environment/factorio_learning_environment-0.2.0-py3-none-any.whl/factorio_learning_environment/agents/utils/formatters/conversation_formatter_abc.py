"""
Abstract base class for conversation formatters.
"""
from abc import ABC, abstractmethod

class ConversationFormatter(ABC):
    """Abstract base class for conversation formatters."""
    
    @abstractmethod
    def format_observation(self, observation):
        """Format an observation for the agent.
        
        Args:
            observation: The observation from the environment
            
        Returns:
            str: The formatted observation
        """
        pass
