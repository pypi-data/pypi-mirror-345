"""
Memory system for agents to maintain context across interactions.
"""
from typing import Dict, List, Any
import time

class Memory:
    """Memory system for agents to store and retrieve information."""
    
    def __init__(self):
        """Initialize memory storage."""
        self.short_term = []  # Recent interactions
        self.long_term = {}   # Persistent knowledge
        
    def add_short_term(self, entry: Dict[str, Any]) -> None:
        """Add an entry to short-term memory."""
        entry["timestamp"] = time.time()
        self.short_term.append(entry)
        
        # Limit short-term memory size
        if len(self.short_term) > 10:
            self.short_term.pop(0)
    
    def add_long_term(self, key: str, value: Any) -> None:
        """Add or update information in long-term memory."""
        self.long_term[key] = {
            "value": value,
            "timestamp": time.time()
        }
    
    def get_context(self) -> Dict[str, Any]:
        """Get combined memory context for the agent."""
        return {
            "short_term": self.short_term,
            "long_term": self.long_term
        }