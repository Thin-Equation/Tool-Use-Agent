from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
import json
import re
import requests
import sympy
import time
from functools import lru_cache
from datetime import datetime, timedelta

# For web search
from duckduckgo_search import DDGS

# For weather 
import pyowm
from pyowm.utils.config import get_default_config

# Import LangChain and LangGraph components
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langchain_core.utils.function_calling import convert_to_openai_tool

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Tool Use Agent API",
    description="API for interacting with a tool-using agent built with LangChain, LangGraph, and Gemini 2.0 Flash",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check if the API key is available
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY environment variable is not set!")

# Initialize the Gemini 2.0 Flash model
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    # Removed deprecated convert_system_message_to_human parameter
    temperature=0.7,
)

# Define request and response models
class UserQuery(BaseModel):
    query: str
    conversation_id: Optional[str] = None

class ToolCall(BaseModel):
    name: str
    input: Dict[str, Any]

class ToolResponse(BaseModel):
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Any

class AgentResponse(BaseModel):
    response: str
    conversation_id: str
    tool_calls: Optional[List[ToolResponse]] = None

# Weather cache to prevent redundant API calls
weather_cache = {}
WEATHER_CACHE_DURATION = 30 * 60  # Cache weather data for 30 minutes

# Define tools using LangChain's tool decorator
@tool
def get_weather(location: str) -> str:
    """Get the current weather in a given location"""
    # Check if we have a recent cache entry for this location
    current_time = time.time()
    cache_key = location.lower()
    
    if cache_key in weather_cache:
        cache_entry = weather_cache[cache_key]
        # If the cached result is still fresh, return it
        if current_time - cache_entry["timestamp"] < WEATHER_CACHE_DURATION:
            return cache_entry["result"]
    
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key or api_key == "your_openweathermap_api_key":
        # Fallback if API key isn't set
        import random
        weather_conditions = ["Sunny", "Cloudy", "Rainy", "Snowy", "Partly cloudy", "Windy"]
        temperatures = {"Sunny": "75°F", "Cloudy": "65°F", "Rainy": "55°F", "Snowy": "32°F", "Partly cloudy": "70°F", "Windy": "60°F"}
        
        condition = random.choice(weather_conditions)
        temperature = temperatures[condition]
        result = f"Weather in {location} (simulated): {condition} with a temperature of {temperature}"
        
        # Cache the simulated result
        weather_cache[cache_key] = {
            "timestamp": current_time,
            "result": result
        }
        
        return result
    
    # Use real OpenWeatherMap API when key is configured
    try:
        config_dict = get_default_config()
        config_dict['language'] = 'en'
        owm = pyowm.OWM(api_key, config_dict)
        mgr = owm.weather_manager()
        
        observation = mgr.weather_at_place(location)
        weather = observation.weather
        temperature = weather.temperature('fahrenheit')['temp']
        status = weather.detailed_status
        humidity = weather.humidity
        wind = weather.wind()['speed']
        
        result = f"Weather in {location}: {status} with a temperature of {temperature:.1f}°F, humidity: {humidity}%, wind: {wind} mph"
        
        # Cache the API result
        weather_cache[cache_key] = {
            "timestamp": current_time,
            "result": result
        }
        
        return result
    except Exception as e:
        error_msg = f"Error getting weather for {location}: {str(e)}"
        
        # Don't cache errors related to rate limiting, but cache other errors briefly
        if "429" not in str(e):
            weather_cache[cache_key] = {
                "timestamp": current_time,
                "result": f"Weather in {location} (cached): Data temporarily unavailable. Please try again in a few minutes."
            }
        
        return error_msg

@tool
def search_web(query: str) -> str:
    """Search the web for information on a given query"""
    ddgs = DDGS()
    results = ddgs.text(query)
    if not results:
        return f"No results found for '{query}'."
    
    response = f"Search results for '{query}':\n\n"
    for i, result in enumerate(results[:3], start=1):
        response += f"{i}. {result['title']}: {result['href']}\n"
    
    return response

@tool
def calculate(expression: str) -> str:
    """Calculate the result of a mathematical expression"""
    try:
        result = sympy.sympify(expression)
        return f"Result of '{expression}' = {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"

@tool
def lookup_definition(term: str) -> str:
    """Look up the definition of a term using a dictionary API"""
    api_key = os.getenv("WORDNIK_API_KEY")
    
    if not api_key or api_key == "your_wordnik_api_key":
        # Fallback to built-in dictionary when API key isn't set
        definitions = {
            "langchain": "An open-source framework for building applications with large language models.",
            "langgraph": "A library for building stateful, multi-actor applications with LLMs, built on top of LangChain.",
            "gemini": "A family of multimodal large language models developed by Google DeepMind.",
            "tool use": "The capability of AI systems to use external tools to accomplish tasks.",
            "next.js": "A React framework for building web applications with server-side rendering and static site generation.",
            "fastapi": "A modern, fast web framework for building APIs with Python based on standard Python type hints.",
            "python": "A high-level, interpreted programming language known for its readability and versatility.",
            "api": "Application Programming Interface - a set of rules that allow different software applications to communicate with each other.",
            "frontend": "The part of a website or application that users interact with directly.",
            "backend": "The server-side of a website or application that works behind the scenes.",
            "react": "A JavaScript library for building user interfaces, particularly single-page applications.",
            "typescript": "A strongly typed programming language that builds on JavaScript."
        }
        
        # Case-insensitive search
        term_lower = term.lower()
        for key, value in definitions.items():
            if key.lower() == term_lower:
                return f"{term}: {value}"
                
        # Try online dictionary API as fallback (no authentication required)
        try:
            response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}")
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    meanings = data[0].get('meanings', [])
                    if meanings:
                        definition = meanings[0].get('definitions', [{}])[0].get('definition', '')
                        part_of_speech = meanings[0].get('partOfSpeech', '')
                        return f"{term} ({part_of_speech}): {definition}"
            return f"Sorry, I couldn't find a definition for '{term}'."
        except Exception:
            return f"Sorry, I couldn't find a definition for '{term}'."
    
    # Use Wordnik API when key is configured
    try:
        url = f"https://api.wordnik.com/v4/word.json/{term}/definitions"
        params = {
            "limit": 3,
            "includeRelated": "false",
            "sourceDictionaries": "all",
            "useCanonical": "true",
            "includeTags": "false",
            "api_key": api_key
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200 and data:
            definition = data[0].get('text', '')
            part_of_speech = data[0].get('partOfSpeech', '')
            return f"{term} ({part_of_speech}): {definition}"
        else:
            # Try the free dictionary API as fallback
            response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}")
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    meanings = data[0].get('meanings', [])
                    if meanings:
                        definition = meanings[0].get('definitions', [{}])[0].get('definition', '')
                        part_of_speech = meanings[0].get('partOfSpeech', '')
                        return f"{term} ({part_of_speech}): {definition}"
            return f"Sorry, I couldn't find a definition for '{term}'."
    except Exception as e:
        return f"Error looking up '{term}': {str(e)}"

# Convert tools to the format expected by Gemini
tools_list = [get_weather, search_web, calculate, lookup_definition]
gemini_tools = [convert_to_openai_tool(t) for t in tools_list]

# Define the agent state
class AgentState(BaseModel):
    conversation_id: str
    messages: List[Dict[str, Any]]
    tool_calls: List[ToolResponse] = Field(default_factory=list)
    current_response: Optional[str] = None
    iteration_count: int = 0  # Add counter to track iterations

# Define tool execution logic
def process_tool_calls(content: str) -> List[dict]:
    """Extract tool calls from model response content"""
    tool_calls = []
    
    # Pattern to match Gemini 2.0 Flash tool calling format
    tool_pattern = r"```tool\s*\n(.*?)\n\s*```"
    tool_matches = re.finditer(tool_pattern, content, re.DOTALL)
    
    for match in tool_matches:
        try:
            tool_data = json.loads(match.group(1))
            if isinstance(tool_data, dict) and "name" in tool_data and "input" in tool_data:
                tool_calls.append(tool_data)
        except json.JSONDecodeError:
            pass
    
    return tool_calls

# Define the agent nodes
def prompt_model(state: AgentState) -> AgentState:
    """Send the conversation to the LLM and get a response"""
    # Increment iteration counter
    state.iteration_count += 1
    
    messages = []
    
    # Add system message with instruction about tools
    system_prompt = """You are a helpful AI assistant with access to tools.
You can use the following tools when appropriate:
- get_weather: Get real-time weather information for a specific location (city, country, etc.)
- search_web: Search the web for up-to-date information using DuckDuckGo
- calculate: Evaluate mathematical expressions including advanced operations supported by sympy 
- lookup_definition: Look up the definition of a term or word using dictionary APIs

When you need to use a tool, use the following format:
```tool
{"name": "tool_name", "input": {"param_name": "value"}}
```

Otherwise, respond directly to the user in a helpful, informative, and friendly manner.
Use the tools when relevant to the user's request, but don't suggest using tools when you can answer directly."""
    
    messages.append(SystemMessage(content=system_prompt))
    
    # Add conversation history
    for message in state.messages:
        if message["role"] == "user":
            messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            messages.append(AIMessage(content=message["content"]))
        elif message["role"] == "tool":
            messages.append(ToolMessage(content=message["content"], tool_call_id=message.get("tool_call_id", "unknown")))
    
    # Get response from the model
    response = model.invoke(messages)
    content = response.content
    
    # Extract tool calls
    extracted_tool_calls = process_tool_calls(content)
    
    # Process any tool calls found in the response
    for tool_call in extracted_tool_calls:
        state.tool_calls.append(
            ToolResponse(
                tool_name=tool_call["name"],
                tool_input=tool_call["input"],
                tool_output=None  # Will be filled by execute_tools
            )
        )
        
        # Remove the tool call from the response text
        content = content.replace(f"```tool\n{json.dumps(tool_call)}\n```", "", 1)
    
    state.current_response = content.strip()
    return state

def execute_tools(state: AgentState) -> AgentState:
    """Execute any tool calls and add the results to the conversation"""
    tool_map = {
        "get_weather": get_weather,
        "search_web": search_web,
        "calculate": calculate,
        "lookup_definition": lookup_definition
    }
    
    # Execute pending tool calls
    for i, tool_call in enumerate(state.tool_calls):
        if tool_call.tool_output is None:
            tool_name = tool_call.tool_name
            
            if tool_name in tool_map:
                try:
                    # Execute the appropriate tool with its inputs using .invoke() instead of direct calling
                    if tool_name == "get_weather":
                        tool_call.tool_output = tool_map[tool_name].invoke(tool_call.tool_input.get("location", ""))
                    elif tool_name == "search_web":
                        tool_call.tool_output = tool_map[tool_name].invoke(tool_call.tool_input.get("query", ""))
                    elif tool_name == "calculate":
                        tool_call.tool_output = tool_map[tool_name].invoke(tool_call.tool_input.get("expression", ""))
                    elif tool_name == "lookup_definition":
                        tool_call.tool_output = tool_map[tool_name].invoke(tool_call.tool_input.get("term", ""))
                    else:
                        tool_call.tool_output = "Tool execution failed: Unknown tool"
                except Exception as e:
                    tool_call.tool_output = f"Tool execution failed: {str(e)}"
            else:
                tool_call.tool_output = f"Tool '{tool_name}' is not available"
                
            # Add tool result to state messages
            state.messages.append({
                "role": "tool",
                "content": str(tool_call.tool_output),
                "tool_call_id": f"call_{len(state.messages) + i}"
            })
    
    return state

# Define routing logic
def should_continue(state: AgentState) -> str:
    """Determine if the agent should continue or end the conversation"""
    # Safety: Force end after too many iterations to prevent infinite loops
    MAX_ITERATIONS = 8
    if state.iteration_count >= MAX_ITERATIONS:
        # Add a message explaining we're ending due to iteration limit
        if state.current_response:
            state.messages.append({
                "role": "assistant",
                "content": state.current_response
            })
        return "end"
        
    executed_tools = [t for t in state.tool_calls if t.tool_output is not None]
    pending_tools = [t for t in state.tool_calls if t.tool_output is None]
    
    if pending_tools:
        return "continue"
    elif executed_tools and state.current_response:
        # If tools were executed and we have a response, add to messages and end
        state.messages.append({
            "role": "assistant",
            "content": state.current_response
        })
        return "end"
    elif executed_tools:
        # If tools were executed but no final response yet, continue to generate response
        return "continue"
    else:
        # No tools to execute, just add the response and end
        state.messages.append({
            "role": "assistant",
            "content": state.current_response or "I processed your request but couldn't generate a response."
        })
        return "end"

# Define and build the graph
def build_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("prompt_model", prompt_model)
    workflow.add_node("execute_tools", execute_tools)
    
    # Add edges
    workflow.add_edge("prompt_model", "execute_tools")
    workflow.add_conditional_edges(
        "execute_tools",
        should_continue,
        {
            "continue": "prompt_model",
            "end": END
        }
    )
    
    # Set the entry point
    workflow.set_entry_point("prompt_model")
    
    # Compile the graph (removed recursion_limit parameter as it's not supported)
    return workflow.compile()

# Initialize the agent graph
agent_graph = build_agent_graph()

# Store conversations (in a real app, this would be a database)
conversations = {}

@app.post("/api/agent", response_model=AgentResponse)
async def query_agent(request: UserQuery):
    conversation_id = request.conversation_id or f"conv_{len(conversations) + 1}"
    
    # Create a new state or get existing one - don't modify it yet
    if conversation_id in conversations:
        # Get existing state but create a copy for modifications
        original_state = conversations[conversation_id]
        
        # Create a fresh AgentState instance for this request
        state = AgentState(
            conversation_id=conversation_id,
            messages=list(original_state.messages) if hasattr(original_state, "messages") else [],
            tool_calls=list(original_state.tool_calls) if hasattr(original_state, "tool_calls") else [],
            current_response=original_state.current_response if hasattr(original_state, "current_response") else None,
            iteration_count=0  # Reset iteration count for new query
        )
        
        # Now we can safely append to state.messages
        state.messages.append({
            "role": "user",
            "content": request.query
        })
    else:
        # Start new conversation with fresh AgentState
        state = AgentState(
            conversation_id=conversation_id,
            messages=[
                {
                    "role": "user",
                    "content": request.query
                }
            ],
            tool_calls=[],
            current_response=None,
            iteration_count=0
        )
    
    # Run the agent graph with our properly initialized state
    result = agent_graph.invoke(state)
    
    # Handle the result, whether it's a dictionary or an object
    if hasattr(result, "get") and callable(getattr(result, "get", None)):
        # It's a dictionary-like object (AddableValuesDict)
        final_response = result.get("current_response", "")
        result_conversation_id = result.get("conversation_id", conversation_id)
        result_tool_calls = result.get("tool_calls", [])
    else:
        # It's an object with attributes
        final_response = result.current_response if hasattr(result, "current_response") else ""
        result_conversation_id = result.conversation_id if hasattr(result, "conversation_id") else conversation_id
        result_tool_calls = result.tool_calls if hasattr(result, "tool_calls") else []
    
    # If no response was generated, use the last assistant message
    if not final_response:
        # Be careful with potentially different object types
        messages = result.messages if hasattr(result, "messages") else state.messages
        assistant_messages = [m for m in messages if isinstance(m, dict) and m.get("role") == "assistant"]
        if assistant_messages:
            final_response = assistant_messages[-1].get("content", "I processed your request but don't have a specific response.")
        else:
            final_response = "I processed your request but couldn't generate a response."
    
    # Save updated conversation state
    conversations[conversation_id] = result
    
    # Return the response
    return AgentResponse(
        response=final_response,
        conversation_id=result_conversation_id,
        tool_calls=[t for t in result_tool_calls if hasattr(t, "tool_output") and t.tool_output is not None]
    )

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"status": "success", "message": f"Conversation {conversation_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")

@app.get("/health")
async def health_check():
    if os.getenv("GOOGLE_API_KEY"):
        return {"status": "ok", "api_key_configured": True}
    else:
        return {"status": "warning", "api_key_configured": False, "message": "GOOGLE_API_KEY not set"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
