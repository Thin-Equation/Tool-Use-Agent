from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents.format_scratchpad.tools import format_to_tool_messages

# Basic system message for the agent
DEFAULT_SYSTEM_MESSAGE = SystemMessage(
    content="""You are a helpful assistant that can use tools to answer user questions.
    
    When you use tools, carefully check the results and make sure you're providing
    accurate information. If you don't know something or can't find the information
    using the available tools, be honest about it.
    
    Always explain your reasoning clearly and in a friendly, conversational tone.
    """
)

# More detailed system message for complex tasks
DETAILED_SYSTEM_MESSAGE = SystemMessage(
    content="""You are an advanced AI assistant that can use tools to solve complex problems.
    
    Follow these guidelines:
    1. Understand what tools are available and what they can do
    2. Break down complex problems into steps
    3. Use the appropriate tools for each step
    4. Interpret the results of tool calls accurately
    5. Explain your process and reasoning clearly
    6. If you encounter errors or unexpected results, troubleshoot and try again
    7. Maintain a friendly, helpful tone throughout
    
    Remember: if you cannot find an answer with the available tools, acknowledge this
    limitation and suggest alternatives if possible.
    """
)

# Custom prompt template for the agent
def create_custom_prompt(include_history=True):
    """Create a custom prompt template with optional conversation history."""
    if include_history:
        mapping = {
            "user_input": lambda x: x["input"],
            "history": lambda x: x.get("history", []),
            "agent_scratchpad": lambda x: format_to_tool_messages(x["intermediate_steps"]),
        }
        template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant with access to tools."),
            ("placeholder", "{history}"),
            ("user", "{user_input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
    else:
        mapping = {
            "user_input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_tool_messages(x["intermediate_steps"]),
        }
        template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant with access to tools."),
            ("user", "{user_input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
    
    return mapping | template
