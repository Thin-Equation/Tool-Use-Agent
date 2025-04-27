# Tool-Use Agent Demo

This project demonstrates a tool-using AI agent built with Next.js, FastAPI, LangChain, LangGraph, and Google's Gemini 2.0 Flash model. The application allows users to interact with an AI assistant that can use tools to answer questions and perform tasks.

## Project Structure

The project is organized into two main components:

- **Frontend**: Next.js application with TypeScript and Tailwind CSS
- **Backend**: FastAPI server with LangChain, LangGraph, and Gemini 2.0 Flash integration

## Features

- Interactive chat interface
- Real-time status indicators
- Tool usage visualization
- Responsive design
- Tool implementations:
  - Real-time weather information using OpenWeatherMap API
  - Web search using DuckDuckGo
  - Advanced mathematical calculations with sympy
  - Dictionary lookups with free dictionary APIs

## Prerequisites

- Node.js (v16+)
- Python (v3.9+)
- Google AI API key (for Gemini 2.0 Flash)
- Optional API keys:
  - OpenWeatherMap API key (free tier available)
  - Wordnik API key (for dictionary lookups, free tier available)

## Installation & Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   ```bash
   # Create a .env file in the backend directory with the following:
   GOOGLE_API_KEY="your_google_api_key"
   OPENWEATHERMAP_API_KEY="your_openweathermap_api_key"  # Optional
   WORDNIK_API_KEY="your_wordnik_api_key"  # Optional
   ```

   > Note: The application will use simulated data when API keys are not provided.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up your environment variables:
   ```bash
   # Create a .env.local file with:
   NEXT_PUBLIC_API_URL="http://localhost:8000"
   ```

## Running the Application

### Start the Backend

1. With the virtual environment activated:
   ```bash
   cd backend
   python run.py
   ```

2. The API server will start on http://localhost:8000

### Start the Frontend

1. In a separate terminal:
   ```bash
   cd frontend
   npm run dev
   ```

2. The Next.js app will start on http://localhost:3000

## API Endpoints

- `POST /api/agent`: Send user queries to the agent
- `DELETE /api/conversations/{conversation_id}`: Delete a conversation
- `GET /health`: Check API health status and API key configuration

## Architecture

The agent uses a stateful graph-based architecture via LangGraph:

1. User messages are sent to the backend
2. Gemini 2.0 Flash model processes the input and determines if tools are needed
3. Tools are executed with appropriate parameters
4. Responses are formatted and sent back to the user

## Technologies Used

- **Frontend**:
  - Next.js
  - TypeScript
  - Tailwind CSS
  - React Hooks

- **Backend**:
  - FastAPI
  - LangChain & LangGraph
  - Gemini 2.0 Flash
  - Pydantic
  - Tool integrations:
    - OpenWeatherMap API (weather)
    - DuckDuckGo Search (web search)
    - Sympy (calculations)
    - Free Dictionary APIs (definitions)

## Extending the Agent

To add more tools to the agent:

1. Define a new function with the `@tool` decorator in `backend/app/main.py`
2. Add the tool to the `tools_list`
3. Update the system prompt in the `prompt_model` function to document the new tool
4. Add appropriate tool execution logic in the `execute_tools` function

## Troubleshooting

- **Weather API Rate Limit**: The application implements caching to prevent hitting OpenWeatherMap rate limits
- **Backend Connection Issues**: Verify the API is running and check the `.env` files for correct configuration
- **Tool Execution Failures**: Check the console logs for specific error messages

## Acknowledgements

- LangChain and LangGraph for the agent framework
- Google's Gemini 2.0 Flash for language capabilities
- OpenWeatherMap, DuckDuckGo, and other APIs for tool functionalities

