from typing import TypedDict, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
import logging


from ..config import DEFAULT_MODEL, AGENT_TEMPERATURE
from ..tools import default_tools
from .prompts import DETAILED_SYSTEM_MESSAGE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    messages: List[HumanMessage | AIMessage | SystemMessage]
    intermediate_steps: List

def create_graph_agent(
    tools=None,
    system_message=None,
    model_name=DEFAULT_MODEL,
    temperature=AGENT_TEMPERATURE
):
    """
    Create a more advanced agent using LangGraph.
    """
    if tools is None:
        tools = default_tools
        
    if system_message is None:
        system_message = DETAILED_SYSTEM_MESSAGE
    
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature
    )
    
    builder = StateGraph(AgentState)

    def determine_tool_use(state: AgentState):
        """Determine which tools to use."""
        try:
            llm_with_tools = llm.bind_tools(tools)
            all_messages = [system_message] + state["messages"]
            response = llm_with_tools.invoke(all_messages)
            return {"messages": state["messages"] + [response]}
        except Exception as e:
            logger.error(f"Error determining tools: {e}")
            return {"messages": state["messages"]}

    def execute_tools(state: AgentState):
        """Execute tools based on the agent's last response."""
        try:
            last_message = state["messages"][-1]
            tool_calls = last_message.additional_kwargs.get("tool_calls", [])
            
            if not tool_calls:
                return {"intermediate_steps": []}

            results = []
            for tool_call in tool_calls:
                try:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    
                    # Find the matching tool
                    selected_tool = next(
                        (tool for tool in tools if tool.name == tool_name), None
                    )
                    
                    if selected_tool:
                        result = selected_tool.invoke(tool_args)
                        results.append({
                            "tool_name": tool_name,
                            "args": tool_args,
                            "result": result
                        })
                    else:
                        logger.warning(f"Tool {tool_name} not found")
                        results.append({
                            "tool_name": tool_name,
                            "error": "Tool not found"
                        })
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}")
                    results.append({
                        "tool_name": tool_name,
                        "error": str(e)
                    })

            return {"intermediate_steps": state["intermediate_steps"] + results}
        except Exception as e:
            logger.error(f"Error in execute_tools: {e}")
            return {"intermediate_steps": state["intermediate_steps"]}

    def generate_final_response(state: AgentState):
        """Generate the final response."""
        try:
            if not state["intermediate_steps"]:
                return {"messages": state["messages"]}

            # Build tool results message
            tool_messages = []
            for step in state["intermediate_steps"]:
                if "result" in step:
                    tool_messages.append(AIMessage(
                        content=f"Tool '{step['tool_name']}' returned: {step['result']}"
                    ))
                elif "error" in step:
                    tool_messages.append(AIMessage(
                        content=f"Error using tool '{step['tool_name']}': {step['error']}"
                    ))

            # Generate final response
            all_messages = [system_message] + state["messages"] + tool_messages
            response = llm.invoke(all_messages)
            
            return {"messages": state["messages"] + tool_messages + [response]}
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {"messages": state["messages"]}

    def should_continue(state: AgentState) -> str:
        """Determine if we need to continue processing."""
        try:
            last_message = state["messages"][-1]
            tool_calls = last_message.additional_kwargs.get("tool_calls", [])
            return "continue" if tool_calls else "end"
        except Exception as e:
            logger.error(f"Error in should_continue: {e}")
            return "end"

    # Add nodes to the graph
    builder.add_node("determine_tool_use", determine_tool_use)
    builder.add_node("execute_tools", execute_tools)
    builder.add_node("generate_final_response", generate_final_response)

    # Define the graph flow
    builder.add_edge(START, "determine_tool_use")
    builder.add_edge("determine_tool_use", "execute_tools")
    builder.add_edge("execute_tools", "generate_final_response")
    
    builder.add_conditional_edges(
        "generate_final_response",
        should_continue,
        {
            "continue": "determine_tool_use",
            "end": END
        }
    )

    return builder.compile()
