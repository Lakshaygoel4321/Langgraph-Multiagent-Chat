export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  classifier?: string;
  confidence_score?: string;
  reasoning?: string;
}

export interface AgentResponse {
  question: string;
  answer: string;
  confidence_score: string;
  classifier: string;
  reasoning: string;
  timestamp: string;
  thread_id: string;
}

export interface StreamChunk {
  event: string;
  data: {
    node?: string;
    content?: string;
    classifier?: string;
    score?: string;
    status?: string;
    message?: string;
    thread_id: string;
  };
  timestamp: string;
}
