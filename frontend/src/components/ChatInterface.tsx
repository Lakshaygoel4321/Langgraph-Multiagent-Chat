'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, History } from 'lucide-react';
import { agentAPI } from '@/services/api';
import { Message, StreamChunk } from '@/types';
import MessageList from './MessageList';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [useStreaming, setUseStreaming] = useState(false);
  const [threadId, setThreadId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Generate thread ID on mount
  useEffect(() => {
    const storedThreadId = sessionStorage.getItem('chat_thread_id');
    if (storedThreadId) {
      setThreadId(storedThreadId);
      loadHistory(storedThreadId);
    } else {
      const newThreadId = `thread-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      setThreadId(newThreadId);
      sessionStorage.setItem('chat_thread_id', newThreadId);
    }
  }, []);

  const loadHistory = async (tid: string) => {
    try {
      const history = await agentAPI.getHistory(tid, 20);
      // Convert history to messages format
      const historicalMessages: Message[] = history.messages.map((msg: any, idx: number) => ([
        {
          id: `hist-q-${idx}`,
          role: 'user' as const,
          content: msg.question,
          timestamp: new Date().toISOString(),
        },
        {
          id: `hist-a-${idx}`,
          role: 'assistant' as const,
          content: msg.answer,
          timestamp: new Date().toISOString(),
          classifier: msg.classifier,
          confidence_score: msg.confidence,
        }
      ])).flat();
      setMessages(historicalMessages);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setStreamingContent('');

    try {
      if (useStreaming) {
        await agentAPI.askQuestionStream(
          input,
          threadId,
          (chunk: StreamChunk) => {
            if (chunk.event === 'node_complete' && chunk.data.content) {
              setStreamingContent((prev) => prev + chunk.data.content);
            }
          },
          (error: string) => {
            console.error('Streaming error:', error);
            const errorMessage: Message = {
              id: Date.now().toString(),
              role: 'assistant',
              content: `Error: ${error}`,
              timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorMessage]);
            setIsLoading(false);
            setStreamingContent('');
          },
          () => {
            if (streamingContent) {
              const assistantMessage: Message = {
                id: Date.now().toString(),
                role: 'assistant',
                content: streamingContent,
                timestamp: new Date().toISOString(),
              };
              setMessages((prev) => [...prev, assistantMessage]);
            }
            setIsLoading(false);
            setStreamingContent('');
          }
        );
      } else {
        const response = await agentAPI.askQuestion(input, threadId);

        const assistantMessage: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: response.answer,
          timestamp: response.timestamp,
          classifier: response.classifier,
          confidence_score: response.confidence_score,
          reasoning: response.reasoning,
        };

        setMessages((prev) => [...prev, assistantMessage]);
      }
    } catch (error: any) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Error: ${error.message}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewConversation = () => {
    const newThreadId = `thread-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setThreadId(newThreadId);
    sessionStorage.setItem('chat_thread_id', newThreadId);
    setMessages([]);
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-t-lg p-6 text-white">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">LangGraph Multi-Agent System</h1>
            <p className="text-sm opacity-90">
              AI-powered assistant with business, research, and technical expertise
            </p>
            <p className="text-xs mt-1 opacity-75">Thread ID: {threadId.slice(0, 20)}...</p>
          </div>
          <button
            onClick={handleNewConversation}
            className="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-sm flex items-center gap-2 transition-colors"
          >
            <History className="w-4 h-4" />
            New Chat
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto bg-gray-50 p-4 border-x border-gray-200">
        <MessageList messages={messages} streamingContent={streamingContent} />
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="bg-white rounded-b-lg border border-gray-200 p-4">
        <div className="flex items-center gap-2 mb-3">
          <label className="flex items-center gap-2 text-sm text-gray-600">
            <input
              type="checkbox"
              checked={useStreaming}
              onChange={(e) => setUseStreaming(e.target.checked)}
              className="rounded"
            />
            Enable Streaming
          </label>
        </div>

        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about business, research, or technology..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Send
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
