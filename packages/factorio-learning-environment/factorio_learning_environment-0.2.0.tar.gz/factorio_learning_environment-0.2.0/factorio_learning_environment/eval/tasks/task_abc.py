from typing import Any, Dict, List
from env.src.entities import Inventory, Entity
from env.src.instance import FactorioInstance
from agents import TaskResponse
from env.src.models.game_state import GameState

class TaskABC:
    def __init__(self, trajectory_length, starting_inventory: Inventory, goal_description: str, task_key: str, all_technology_reserached: bool = False):
        self.trajectory_length = trajectory_length
        self.starting_inventory = starting_inventory
        self.goal_description = goal_description
        self.task_key = task_key
        self.all_technology_reserached = all_technology_reserached
    
    def verify(self, score: float, step: int, instance: FactorioInstance, step_statistics: Dict) -> bool:
        """ Return true is the task is completed"""
        pass
    def setup_instance(self, instance):
        """Code to provision the task environment"""
        pass
    
    def enhance_response_with_task_output(self, response: str, task_response: TaskResponse) -> str:
        """Add task specific information to the environment response"""
        return response
    
    
    def setup(self, instance):
        """setup function"""
        instance.initial_inventory = self.starting_inventory
        instance.all_technologies_researched = self.all_technology_reserached
        instance.reset()
        self.setup_instance(instance)
        self.starting_game_state = GameState.from_instance(instance)