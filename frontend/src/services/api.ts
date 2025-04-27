// API Service for communicating with the backend

// API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Interface for the Agent API response
 */
export interface AgentResponse {
  response: string;
  conversation_id: string;
  tool_calls?: {
    tool_name: string;
    tool_input: Record<string, unknown>;
    tool_output: unknown;
  }[];
}

/**
 * Service for interacting with the Agent API
 */
export class AgentService {
  /**
   * Send a query to the agent
   * @param query The user's query to the agent
   * @param conversationId Optional ID to continue a conversation
   * @returns Promise resolving to the agent's response
   */
  static async queryAgent(query: string, conversationId?: string): Promise<AgentResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/agent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query,
          conversation_id: conversationId 
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An error occurred while querying the agent.');
      }

      return await response.json();
    } catch (error) {
      console.error('Error querying agent:', error);
      throw error;
    }
  }

  /**
   * Delete a conversation history
   * @param conversationId ID of the conversation to delete
   */
  static async deleteConversation(conversationId: string): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/conversations/${conversationId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An error occurred while deleting the conversation.');
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  }

  /**
   * Check the health of the API
   * @returns Promise resolving to a boolean indicating if the API is healthy
   */
  static async checkHealth(): Promise<{isHealthy: boolean; apiKeyConfigured?: boolean}> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: 'GET',
      });
      
      if (response.ok) {
        const data = await response.json();
        return { 
          isHealthy: true,
          apiKeyConfigured: data.api_key_configured
        };
      }
      return { isHealthy: false };
    } catch (error) {
      console.error('Health check failed:', error);
      return { isHealthy: false };
    }
  }
}
