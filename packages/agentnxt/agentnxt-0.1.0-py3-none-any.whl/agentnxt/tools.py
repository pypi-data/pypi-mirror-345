"""
Tool system for equipping agents with additional capabilities.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class Tool(ABC):
    """Base class for all tools that agents can use."""
    
    name: str
    description: str
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the tool with the provided arguments."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to a dictionary format for API calls."""
        return {
            "name": self.name,
            "description": self.description,
        }

