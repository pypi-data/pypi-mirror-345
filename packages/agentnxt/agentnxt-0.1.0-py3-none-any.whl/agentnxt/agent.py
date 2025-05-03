"""
Agent module for creating intelligent autonomous agents powered by LLMs.
"""
import os
import openai
from typing import List, Dict, Any, Optional
from .tools import Tool
from .memory import Memory

class Agent:
    """
    An AI agent powered by language models like GPT-4, capable of using tools
    and maintaining memory to complete tasks.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        tools: List[Tool] = None,
        memory: Memory = None
    ):
        """
        Initialize an AI agent.
        
        Args:
            name: The agent's name
            description: The agent's purpose and capabilities
            model: The LLM model to use (default: gpt-4)
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            tools: List of tools the agent can use
            memory: Memory system for the agent
        """
        self.name = name
        self.description = description
        self.model = model
        
        # Set API key
        openai.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OpenAI API key must be provided or set as OPENAI_API_KEY environment variable")
        
        # Initialize tools and memory
        self.tools = tools or []
        self.memory = memory or Memory()
    
    def run(self, instruction: str) -> str:
        """
        Run the agent on a given instruction.
        
        Args:
            instruction: The task or query for the agent
            
        Returns:
            The agent's response
        """
        # Format system message with agent description and tools
        system_message = f"You are {self.name}, {self.description}"
        
        # Add tools to system message if there are any
        if self.tools:
            system_message += "\nYou have access to the following tools:"
            for tool in self.tools:
                system_message += f"\n- {tool.name}: {tool.description}"
        
        # Add memory context
        memory_context = self.memory.get_context()
        if memory_context:
            system_message += "\n\nMemory context:"
            if memory_context.get("short_term"):
                system_message += "\nRecent interactions: " + str(memory_context["short_term"])
            if memory_context.get("long_term"):
                system_message += "\nLong-term knowledge: " + str(memory_context["long_term"])
        
        # Call OpenAI API
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": instruction}
                ]
            )
            
            # Update memory with this interaction
            self.memory.add_short_term({
                "role": "user",
                "content": instruction
            })
            self.memory.add_short_term({
                "role": "assistant",
                "content": response.choices[0].message.content
            })
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"