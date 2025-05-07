"""
Basic agent implementation for Factorio Learning Environment.
"""
from .agent_abc import Agent

class BasicAgent(Agent):
    """Basic agent implementation."""
    
    def __init__(self):
        """Initialize the basic agent."""
        pass
        
    def act(self, observation):
        """Process an observation and return an action.
        
        Args:
            observation: The observation from the environment
            
        Returns:
            action: The action to perform
        """
        # Stub implementation
        return {"type": "no_op"}
