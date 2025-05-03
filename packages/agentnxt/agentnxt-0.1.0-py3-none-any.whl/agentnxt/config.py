"""
Configuration module for AgentNXT package.
"""
import openai
from typing import Optional

def configure(api_key: Optional[str] = None):
    """
    Configure global settings for AgentNXT.
    
    Args:
        api_key: OpenAI API key to use for all agents
    """
    if api_key:
        openai.api_key = api_key

