#!/usr/bin/env python3

import sys
import os
from typing import List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import create_graph_agent
from src.tools import default_tools

def format_message(message):
    """Format a message for display."""
    if isinstance(message, HumanMessage):
        return f"Human: {message.content}"
    elif isinstance(message, AIMessage):
        # Handle tool calls if present
        tool_calls = getattr(message, "tool_calls", [])
        if not tool_calls and hasattr(message, "additional_kwargs"):
            tool_calls = message.additional_kwargs.get("tool_calls", [])
            
        if tool_calls:
            # Use dictionary access (bracket notation) instead of attribute access
            tool_info = "\n  Tool Calls: " + ", ".join([f"{t['name']}({t['args']})" for t in tool_calls])
            return f"AI: {message.content}{tool_info}"
        return f"AI: {message.content}"
    elif isinstance(message, SystemMessage):
        return f"System: {message.content}"
    else:
        return f"Unknown message type: {str(message)}"


def print_conversation(messages):
    """Print a conversation in a readable format."""
    for msg in messages:
        print(format_message(msg))
        print("-" * 40)

def main():
    print("Creating Gemini Tool-Use Agent with LangGraph...")
    
    # Create a graph agent with all default tools
    graph = create_graph_agent(tools=default_tools)
    
    # Define example queries
    example_queries = [
        "What's the weather forecast for Chicago tomorrow?",
        "Can you search the database for recent sales data?",
        "What's the current date and time?",
        "Calculate 24 * 7 + 365"
    ]
    
    # Run the examples
    for i, query in enumerate(example_queries):
        print(f"\n\n{'='*50}")
        print(f"Example {i+1}: {query}")
        print(f"{'='*50}\n")
        
        # Create initial state with human message
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "intermediate_steps": []
        }
        
        # Invoke the graph
        result = graph.invoke(initial_state)
        
        # Display the conversation
        print("\nConversation Flow:")
        print_conversation(result["messages"])
        
        # Display the final answer
        final_message = result["messages"][-1].content if result["messages"] else "No response"
        print(f"\nFinal Answer: {final_message}")
    
    # Interactive mode
    print("\n\n" + "="*50)
    print("Interactive Mode (type 'exit' to quit)")
    print("="*50 + "\n")
    
    # Initialize conversation history
    conversation_history = []
    
    while True:
        user_input = input("\nEnter your question: ")
        if user_input.lower() in ['exit', 'quit', 'q']:
            break
            
        # Add the user input to conversation history
        conversation_history.append(HumanMessage(content=user_input))
        
        # Create initial state with the full conversation history
        initial_state = {
            "messages": conversation_history.copy(),
            "intermediate_steps": []
        }
        
        # Invoke the graph
        result = graph.invoke(initial_state)
        
        # Get any new messages
        new_messages = result["messages"][len(conversation_history):]
        
        # Update conversation history
        conversation_history.extend(new_messages)
        
        # Display the new messages
        print("\nConversation:")
        print(f"Human: {user_input}")
        for msg in new_messages:
            print(format_message(msg))
        
        # Display the final answer if there are new messages
        if new_messages:
            final_message = new_messages[-1].content
            print(f"\nFinal Answer: {final_message}")
        else:
            print("\nNo response from agent.")

if __name__ == "__main__":
    main()
