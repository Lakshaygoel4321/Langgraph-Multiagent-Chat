import axios, { AxiosInstance } from 'axios';
import { AgentResponse, StreamChunk } from '@/types';

class AgentAPIService {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 120000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Submit question to agent (non-streaming)
   */
  async askQuestion(question: string, threadId?: string): Promise<AgentResponse> {
    try {
      const response = await this.client.post<AgentResponse>(
        '/api/v1/ask',
        { 
          question, 
          thread_id: threadId,
          stream: false 
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('Error asking question:', error);
      throw new Error(
        error.response?.data?.detail || 'Failed to get answer from agent'
      );
    }
  }

  /**
   * Submit question with streaming response (SSE)
   */
  async askQuestionStream(
    question: string,
    threadId: string | undefined,
    onChunk: (chunk: StreamChunk) => void,
    onError: (error: string) => void,
    onComplete: () => void
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/ask/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          question, 
          thread_id: threadId,
          stream: true 
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Response body is not readable');
      }

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          onComplete();
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.substring(6)) as StreamChunk;
              onChunk(data);
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error: any) {
      console.error('Streaming error:', error);
      onError(error.message || 'Failed to stream response');
    }
  }

  /**
   * Get conversation history
   */
  async getHistory(threadId: string, limit: number = 10) {
    try {
      const response = await this.client.get(`/api/v1/history/${threadId}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get history:', error);
      throw error;
    }
  }

  /**
   * Get thread state
   */
  async getThreadState(threadId: string) {
    try {
      const response = await this.client.get(`/api/v1/state/${threadId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get thread state:', error);
      throw error;
    }
  }

  /**
   * Check API health status
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.data.status === 'healthy';
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  /**
   * Get API status and configuration
   */
  async getStatus() {
    try {
      const response = await this.client.get('/api/v1/status');
      return response.data;
    } catch (error) {
      console.error('Failed to get status:', error);
      throw error;
    }
  }
}

export const agentAPI = new AgentAPIService();
