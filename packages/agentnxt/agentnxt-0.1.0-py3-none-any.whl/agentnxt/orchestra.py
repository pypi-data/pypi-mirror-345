"""
Orchestra module for coordinating multiple agents to work together.
"""
from typing import List, Dict, Any, Optional
from .agent import Agent
from .memory import Memory

class Orchestra:
    """
    Coordinates multiple agents to work together on complex tasks.
    """
    
    def __init__(
        self,
        agents: List[Agent],
        memory: Optional[Memory] = None,
        coordinator_prompt: str = "Coordinate the agents to solve the task efficiently"
    ):
        """
        Initialize a multi-agent orchestra.
        
        Args:
            agents: List of agents to coordinate
            memory: Shared memory for the agents
            coordinator_prompt: Instructions for the coordinator
        """
        self.agents = agents
        self.memory = memory or Memory()
        self.coordinator_prompt = coordinator_prompt
    
    def run(self, task: str) -> str:
        """
        Run the multi-agent system on a task.
        
        Args:
            task: The task to be completed
            
        Returns:
            The final result after agent collaboration
        """
        # Create a coordinator agent
        coordinator = Agent(
            name="Coordinator",
            description=f"Coordinator that manages collaboration between agents: {', '.join([agent.name for agent in self.agents])}",
            model=self.agents[0].model  # Use the model of the first agent
        )
        
        # Initial task planning
        planning_prompt = f"""
        Task: {task}
        
        Coordinator prompt: {self.coordinator_prompt}
        
        Available agents:
        {', '.join([f"{agent.name}: {agent.description}" for agent in self.agents])}
        
        Create a plan to solve this task using these agents efficiently.
        """
        
        plan = coordinator.run(planning_prompt)
        
        # Add plan to memory
        self.memory.add_short_term({
            "type": "plan",
            "content": plan
        })
        
        # Execute plan with agent collaboration (simplified)
        current_state = f"Initial task: {task}\n\nPlan: {plan}"
        
        # Simple round-robin execution among agents (in a real implementation, this would be more sophisticated)
        for i, agent in enumerate(self.agents):
            agent_prompt = f"""
            Task: {task}
            
            Current state: {current_state}
            
            As {agent.name}, your role is: {agent.description}
            
            What is your contribution to solving this task?
            """
            
            agent_response = agent.run(agent_prompt)
            current_state += f"\n\n{agent.name}'s contribution: {agent_response}"
            
            # Add to shared memory
            self.memory.add_short_term({
                "agent": agent.name,
                "contribution": agent_response
            })
        
        # Final synthesis by coordinator
        synthesis_prompt = f"""
        Task: {task}
        
        All agent contributions:
        {current_state}
        
        Synthesize these contributions into a coherent final response that addresses the original task.
        """
        
        final_result = coordinator.run(synthesis_prompt)
        return final_result