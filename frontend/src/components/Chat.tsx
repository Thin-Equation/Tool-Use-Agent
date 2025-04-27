"use client";

import { useState, useRef, useEffect } from 'react';
import { AgentService, AgentResponse } from '@/services/api';
import Image from 'next/image';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  toolCalls?: AgentResponse['tool_calls'];
}

export default function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<'connecting' | 'connected' | 'error' | 'warning'>('connecting');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check API health on component mount
  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        const healthCheck = await AgentService.checkHealth();
        
        if (!healthCheck.isHealthy) {
          setApiStatus('error');
          setStatusMessage('Cannot connect to backend API');
        } else if (!healthCheck.apiKeyConfigured) {
          setApiStatus('warning');
          setStatusMessage('API key not configured. Agent functionality limited.');
        } else {
          setApiStatus('connected');
          setStatusMessage(null);
        }
      } catch {
        setApiStatus('error');
        setStatusMessage('Cannot connect to backend API');
      }
    };

    checkApiHealth();
    // Poll API health every 30 seconds
    const interval = setInterval(checkApiHealth, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Don't submit empty messages
    if (!input.trim()) return;
    
    // Add user message to chat
    const userMessage: ChatMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    
    // Clear input and set loading state
    const currentInput = input;
    setInput('');
    setIsLoading(true);
    
    try {
      // Send query to agent with conversation ID if one exists
      const response = await AgentService.queryAgent(currentInput, conversationId || undefined);
      
      // Save conversation ID for future interactions
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }
      
      // Add assistant response to chat
      const assistantMessage: ChatMessage = { 
        role: 'assistant', 
        content: response.response,
        toolCalls: response.tool_calls
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error querying agent:', error);
      
      // Add error message
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error while processing your request. Please try again.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Start a new conversation
  const startNewConversation = async () => {
    if (conversationId) {
      try {
        await AgentService.deleteConversation(conversationId);
      } catch (error) {
        console.error('Error deleting conversation:', error);
      }
    }
    
    setConversationId(null);
    setMessages([]);
  };

  // Render tool usage visualization
  const renderToolUsage = (tool: {
    tool_name: string;
    tool_input: Record<string, unknown>;
    tool_output: unknown;
  }) => {
    // Select icon based on tool type
    const getToolIcon = (toolName: string) => {
      switch (toolName) {
        case 'get_weather':
          return '/globe.svg';
        case 'search_web':
          return '/window.svg';  
        case 'calculate':
          return '/file.svg';
        case 'lookup_definition':
          return '/file.svg';
        default:
          return '/file.svg';
      }
    };

    return (
      <div key={`${tool.tool_name}-${JSON.stringify(tool.tool_input)}`} className="bg-gray-50 p-3 rounded-md mb-2 border border-gray-200">
        <div className="flex items-center gap-2 mb-1">
          <Image 
            src={getToolIcon(tool.tool_name)}
            alt={tool.tool_name} 
            width={16} 
            height={16}
            priority={false}
            unoptimized={true}
          />
          <span className="font-medium text-gray-800">{tool.tool_name}</span>
        </div>
        
        <div className="text-sm mb-1">
          <span className="text-gray-600 font-medium">Input: </span>
          <code className="bg-gray-100 px-1 py-0.5 rounded">{JSON.stringify(tool.tool_input)}</code>
        </div>
        
        <div className="text-sm">
          <span className="text-gray-600 font-medium">Output: </span>
          <code className="bg-gray-100 px-1 py-0.5 rounded whitespace-pre-wrap">
            {typeof tool.tool_output === 'string' ? tool.tool_output : JSON.stringify(tool.tool_output, null, 2)}
          </code>
        </div>
      </div>
    );
  };

  // Render a single message
  const renderMessage = (message: ChatMessage, index: number) => {
    const isUser = message.role === 'user';
    
    return (
      <div 
        key={index}
        className={`p-4 rounded-lg mb-4 ${
          isUser 
            ? 'bg-blue-100 ml-auto max-w-2xl' 
            : 'bg-gray-100 max-w-3xl'
        }`}
      >
        {/* Message header */}
        <div className="flex items-center mb-2">
          <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
            isUser ? 'bg-blue-500 text-white' : 'bg-gray-700 text-white'
          }`}>
            {isUser ? 'U' : 'A'}
          </div>
          <span className="ml-2 font-medium">
            {isUser ? 'You' : 'Assistant'}
          </span>
        </div>
        
        {/* Message content */}
        <div className="prose max-w-none">
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
        
        {/* Tool calls */}
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="mt-3 border-t border-gray-200 pt-3">
            <p className="text-sm font-semibold mb-2">Tools Used:</p>
            <div className="space-y-2">
              {message.toolCalls.map(renderToolUsage)}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      {/* API Status */}
      <div className={`text-sm px-4 py-2 mb-2 rounded-md flex justify-between items-center ${
        apiStatus === 'connected' ? 'bg-green-100 text-green-800' : 
        apiStatus === 'warning' ? 'bg-yellow-100 text-yellow-800' : 
        apiStatus === 'error' ? 'bg-red-100 text-red-800' : 
        'bg-yellow-100 text-yellow-800'
      }`}>
        <div className="flex items-center">
          <div className={`w-2 h-2 rounded-full mr-2 ${
            apiStatus === 'connected' ? 'bg-green-600' : 
            apiStatus === 'warning' ? 'bg-yellow-600' : 
            'bg-red-600'
          }`}></div>
          <span>
            {apiStatus === 'connected' ? 'Connected to API' : 
            apiStatus === 'warning' ? 'API Warning' : 
            apiStatus === 'error' ? 'API Error' : 
            'Connecting to API...'}
          </span>
        </div>
        
        {statusMessage && <span className="text-xs">{statusMessage}</span>}
        
        <button 
          onClick={startNewConversation}
          disabled={messages.length === 0}
          className={`text-xs px-2 py-1 rounded ${
            messages.length === 0 
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          New Conversation
        </button>
      </div>
      
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 my-8">
            <p className="text-xl font-semibold mb-2">Welcome to the Tool-Use Agent Demo</p>
            <p>Start a conversation by sending a message below.</p>
            <p className="mt-4 text-sm">
              Try asking questions that might require tools, such as:
            </p>
            <ul className="mt-2 space-y-1 text-sm list-disc list-inside">
                <li>&ldquo;What&apos;s the weather in New York?&rdquo;</li>
                <li>&ldquo;Search for information about machine learning&rdquo;</li>
                <li>&ldquo;Calculate 15 * (23 + 7)&rdquo;</li>
                <li>&ldquo;What is the definition of langchain?&rdquo;</li>
              </ul>
            <div className="mt-6 max-w-md mx-auto bg-blue-50 p-3 rounded-md text-sm text-blue-800">
              <p className="font-medium">About this demo</p>
              <p className="mt-1">This is a demonstration of tool use with LangChain, LangGraph, and Gemini 2.0 Flash. The agent has access to tools for weather forecasts, web searches, calculations, and term definitions.</p>
            </div>
          </div>
        ) : (
          messages.map(renderMessage)
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Form */}
      <form onSubmit={handleSubmit} className="border-t p-4 bg-white">
        <div className="flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 p-2 border rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading || apiStatus === 'error'}
          />
          <button
            type="submit"
            className={`bg-blue-500 text-white p-2 rounded-r-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              isLoading || apiStatus === 'error' ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            disabled={isLoading || apiStatus === 'error'}
          >
            {isLoading ? 'Thinking...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
}
