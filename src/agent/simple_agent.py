from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..config import DEFAULT_MODEL, AGENT_TEMPERATURE
from ..tools import default_tools
from .prompts import DEFAULT_SYSTEM_MESSAGE

def create_simple_agent(
    tools=None, 
    system_message=None,
    model_name=DEFAULT_MODEL,
    temperature=AGENT_TEMPERATURE,
    verbose=True
):
    """
    Create a simple tool-using agent with LangChain and Gemini.
    """
    
    # Use default tools if none provided
    if tools is None:
        tools = default_tools
        
    # Get system message content
    if system_message is None:
        system_message_content = DEFAULT_SYSTEM_MESSAGE.content
    else:
        system_message_content = system_message.content
    
    # Create a proper ChatPromptTemplate with required placeholders
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message_content),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Initialize the model
    model = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature
    )
    
    # Create the agent
    agent = create_tool_calling_agent(model, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        handle_parsing_errors=True,
    )
    
    return agent_executor
