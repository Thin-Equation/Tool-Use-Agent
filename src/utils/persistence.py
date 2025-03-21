import os
from langgraph.checkpoint import FileSystemCheckpointer

from ..config import CHECKPOINT_DIR

def create_filesystem_checkpointer(directory=None):
    """
    Create a FileSystemCheckpointer for persistent conversations.
    
    Args:
        directory: Custom directory to store checkpoints (defaults to config.CHECKPOINT_DIR)
    
    Returns:
        A FileSystemCheckpointer instance
    """
    if directory is None:
        directory = CHECKPOINT_DIR
        
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)
    
    return FileSystemCheckpointer(directory)

def get_persistent_agent(agent_executor, checkpointer=None):
    """
    Add persistence capabilities to an agent executor.
    
    Args:
        agent_executor: The agent executor to make persistent
        checkpointer: Custom checkpointer (creates a new one if None)
    
    Returns:
        The agent executor with persistence enabled
    """
    if checkpointer is None:
        checkpointer = create_filesystem_checkpointer()
        
    # Add the checkpointer to the agent
    agent_executor.checkpointer = checkpointer
    
    return agent_executor
