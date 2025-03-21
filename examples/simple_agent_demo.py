import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import create_simple_agent
from src.tools import default_tools

def main():
    print("Creating Gemini Tool-Use Agent with LangChain...")
    
    # Create a simple agent with all default tools
    agent = create_simple_agent(tools=default_tools, verbose=True)
    
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
        
        response = agent.invoke({"input": query})
        print(f"\nFinal Answer: {response['output']}")
    
    # Interactive mode
    print("\n\n" + "="*50)
    print("Interactive Mode (type 'exit' to quit)")
    print("="*50 + "\n")
    
    while True:
        user_input = input("\nEnter your question: ")
        if user_input.lower() in ['exit', 'quit', 'q']:
            break
            
        response = agent.invoke({"input": user_input})
        print(f"\nAgent: {response['output']}")

if __name__ == "__main__":
    main()
